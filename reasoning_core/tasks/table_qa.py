import json
import pandas as pd
import duckdb
import numpy as np
from faker import Faker
import random
from html import escape
from babel.dates import format_date
from babel.numbers import format_decimal
from tabulate import tabulate
from dataclasses import dataclass
from reasoning_core.template import Task, DevTask, Entry, Config, render_payload, stochastic_rounding as sround
from reasoning_core.utils import score_scalar
import csv
import yaml
import io

try:
    from sklearn.metrics import normalized_mutual_info_score
except Exception:
    normalized_mutual_info_score = None

@dataclass
class TableQAConfig(Config):
    num_rows: int = 8
    num_columns: int = 6
    num_tables: int = 1
    complexity: int = 1
    def apply_difficulty(self, level):
        # Keep the TABLE small. The old ramp (rows*1.7**level, +level cols, up to 3 shards)
        # exploded the prompt to ~5k tok at L4 and made this a net-hurter via prompt-length
        # tax under answer-only training (global -1.98 / bbh -3.01). Shrinking the table to
        # ~600 tok at L4 flips influence to neutral (global -0.20 / bbh +0.80), confirming
        # prompt length was the driver. Validated 2026-07-09 (REEVAL_TQSHRINK_OLMO1B); the
        # neutral run held complexity flat, so leave it at its default rather than adding an
        # unvalidated length source. Query complexity is the length-safe lever to reintroduce
        # difficulty later (re-measure length before ramping it).
        self.num_rows = 4 + 2 * level              # 4, 6, 8, 10, 12
        self.num_columns = min(3 + level, 6)       # 3, 4, 5, 6, 6
        self.num_tables = 1                        # never shard


@dataclass
class TableStatisticsConfig(Config):
    num_rows: int = 9
    num_numeric: int = 4
    num_categories: int = 3
    margin: float = 0.45
    def apply_difficulty(self, level):
        self.num_rows = sround(self.num_rows * (1.5 ** level))
        self.num_numeric = sround(self.num_numeric + level)
        self.num_categories = sround(self.num_categories + level)
        self.margin = max(0.08, self.margin * (0.85 ** level))


_faker = Faker()

LOCALES = ["en_US", "fr_FR"]
DATE_FORMATS = ["yyyy-MM-dd", "d MMM yyyy", "MMM d, yyyy", "yyyy/MM/dd"]
NUMBER_FORMATS = ["#,##0.##", "#,##0.00", "#,##0.##", "#,##0.00", "0.###E0"]
TABLEQA_NUMBER_FORMATS = ["0.##", "0.00", "0.###"]
TABLEQA_CORE = [
    "row_id", "country", "category", "status", "date", "qty", "unit_price",
]
TABLEQA_EXTRA = [
    "customer", "segment", "discount", "gross", "net", "is_refund",
]
BOOL_FORMATS = [
    {True: "true", False: "false"},
    {True: "yes", False: "no"},
    {True: "Y", False: "N"},
    {True: "1", False: "0"},
    {True: "✓", False: "✗"},
]
NULL_TOKENS = ["", "NA", "N/A", "null", "-", "—"]

def generate_random_table(config):
    f = _faker
    pool = [
        ('customer', f.name), ('city', f.city), ('country', f.country), ('email', f.email),
        ('company', f.company), ('product', lambda: f.word().capitalize()), ('job', f.job),
        ('date', lambda: f.date_between('-1y')), ('qty', lambda: random.randint(1, 1000)),
        ('revenue', lambda: round(random.uniform(10, 1000), 2)),
        ('price', lambda: round(random.uniform(5, 500), 2)),
        ('rating', lambda: round(random.uniform(1, 5), 1))
    ]
    cols = random.sample(pool, min(config.num_columns, len(pool)))
    return pd.DataFrame({n: [g() for _ in range(config.num_rows)] for n, g in cols})


def generate_tableqa_dataframe(config):
    n = config.num_rows
    countries = ["France", "Germany", "Spain", "Italy", "Netherlands"]
    segments = ["consumer", "corporate", "education"]
    categories = ["Books", "Electronics", "Clothing", "Food", "Office"]
    statuses = ["paid", "refunded", "pending", "cancelled"]

    df = pd.DataFrame({
        "row_id": [f"R{i:04d}" for i in range(n)],
        "customer": [f"C{random.randint(1, max(3, n // 3)):03d}" for _ in range(n)],
        "country": np.random.choice(countries, n),
        "segment": np.random.choice(segments, n),
        "category": np.random.choice(categories, n),
        "status": np.random.choice(statuses, n, p=[0.62, 0.12, 0.16, 0.10]),
        "date": [_faker.date_between("-18M", "today") for _ in range(n)],
        "qty": np.random.randint(1, 12, n),
        "unit_price": np.round(np.random.lognormal(3.1, 0.65, n), 2),
        "discount": np.random.choice([0, 0.05, 0.1, 0.2, 0.3], n),
    })
    df["gross"] = np.round(df["qty"] * df["unit_price"], 2)
    df["net"] = np.round(df["gross"] * (1 - df["discount"]), 2)
    df["is_refund"] = df["status"].eq("refunded")
    df = apply_tableqa_noise(df, config)

    k = max(len(TABLEQA_CORE), config.num_columns)
    extras = random.sample(TABLEQA_EXTRA, min(len(TABLEQA_EXTRA), k - len(TABLEQA_CORE)))
    cols = TABLEQA_CORE + extras
    random.shuffle(cols)
    return df[cols]


def apply_tableqa_noise(df, config):
    rate = min(0.18, 0.02 * config.complexity)
    for c in ["discount", "segment"]:
        if c in df.columns:
            df.loc[np.random.rand(len(df)) < rate, c] = np.nan
    return df

def is_date_series(s):
    xs = s.dropna()
    return len(xs) and xs.map(lambda x: hasattr(x, "strftime")).all()


def date_columns(dataframe):
    return [c for c in dataframe.columns if is_date_series(dataframe[c])]


def render_date_series(s):
    locale, fmt = random.choice(LOCALES), random.choice(DATE_FORMATS)
    out = s.map(lambda x: format_date(x, fmt, locale=locale) if pd.notna(x) else x)
    return out, {"kind": "date", "format": fmt, "locale": locale}


def render_number_series(s, number_formats=NUMBER_FORMATS, number_locales=LOCALES):
    locale, fmt = random.choice(number_locales), random.choice(number_formats)
    out = s.map(lambda x: format_decimal(x, format=fmt, locale=locale) if pd.notna(x) else x)
    return out, {"kind": "number", "format": fmt, "locale": locale}


def render_bool_series(s):
    mapping = random.choice(BOOL_FORMATS)
    meta_mapping = {str(k): v for k, v in mapping.items()}
    return s.map(lambda x: mapping.get(x, x)), {"kind": "bool", "mapping": meta_mapping}


def render_nulls(s):
    token = random.choice(NULL_TOKENS)
    return s.map(lambda x: token if pd.isna(x) else x), {"null": token}


def make_display_dataframe(dataframe, number_formats=NUMBER_FORMATS, number_locales=LOCALES):
    df, meta = dataframe.copy(), {}
    for c in df.columns:
        s = df[c]
        if is_date_series(s):
            df[c], meta[c] = render_date_series(s)
        elif pd.api.types.is_bool_dtype(s):
            df[c], meta[c] = render_bool_series(s)
        elif pd.api.types.is_numeric_dtype(s):
            df[c], meta[c] = render_number_series(
                s,
                number_formats=number_formats,
                number_locales=number_locales,
            )
        if df[c].isna().any():
            df[c], null_meta = render_nulls(df[c])
            meta.setdefault(c, {}).update(null_meta)
    return df.astype(object), {"display": meta}


def make_statistics_display_dataframe(dataframe):
    return dataframe.copy().astype(object), {"display": {}}


def apply_display_formats(dataframe, display_meta):
    df = dataframe.copy()
    for c, spec in display_meta.get("display", {}).items():
        if c not in df.columns:
            continue
        if spec.get("kind") == "date":
            df[c] = df[c].map(lambda x: format_date(x, spec["format"], locale=spec["locale"]) if pd.notna(x) else x)
        elif spec.get("kind") == "number":
            df[c] = df[c].map(lambda x: format_decimal(x, format=spec["format"], locale=spec["locale"]) if pd.notna(x) else x)
        elif spec.get("kind") == "bool":
            df[c] = df[c].map(lambda x: spec["mapping"].get(str(x), x))
        if "null" in spec:
            df[c] = df[c].map(lambda x: spec["null"] if pd.isna(x) else x)
    return df.astype(object)


def rows(dataframe, index=False):
    return dataframe.reset_index() if index else dataframe


def to_tab(dataframe, tablefmt, index=False):
    df = rows(dataframe, index=index)
    return tabulate(df, headers="keys", tablefmt=tablefmt, showindex=False, disable_numparse=True)


def to_html(dataframe, index=False):
    df = rows(dataframe, index=index)
    out = ["<table>"]
    out.append("<thead><tr>" + "".join(f"<th>{escape(str(c))}</th>" for c in df.columns) + "</tr></thead>")
    out.append("<tbody>")
    for _, row in df.iterrows():
        out.append("<tr>" + "".join(f"<td>{escape(str(row[c]))}</td>" for c in df.columns) + "</tr>")
    out += ["</tbody>", "</table>"]
    return "\n".join(out)


def to_kv_rows(dataframe, index=False):
    df = rows(dataframe, index=index)
    return "\n".join("; ".join(f"{c}: {row[c]}" for c in df.columns) for _, row in df.iterrows())


def to_jsonl(dataframe, index=False):
    return "\n".join(json.dumps(r, ensure_ascii=False, default=str) for r in rows(dataframe, index=index).to_dict("records"))


def to_python_records(dataframe, index=False):
    return repr(rows(dataframe, index=index).to_dict("records"))


def get_renderers(dataframe):
    return {
        "to_string": lambda index=False: to_tab(dataframe, "plain", index=index),
        "to_markdown": lambda index=False: to_tab(dataframe, "pipe", index=index),
        "to_grid": lambda index=False: to_tab(dataframe, "grid", index=index),
        "to_csv": lambda index=False: rows(dataframe, index=index).to_csv(index=False),
        "to_tsv": lambda index=False: rows(dataframe, index=index).to_csv(index=False, sep="\t"),
        "to_pipe": lambda index=False: rows(dataframe, index=index).to_csv(index=False, sep="|"),
        "to_html": lambda index=False: to_html(dataframe, index=index),
        "to_latex": lambda index=False: to_tab(dataframe, "latex", index=index),
        "to_json": lambda index=False: rows(dataframe, index=index).to_json(orient="records", indent=4, force_ascii=False),
        "to_jsonl": lambda index=False: to_jsonl(dataframe, index=index),
        "to_yaml": lambda index=False: yaml.dump(rows(dataframe, index=index).to_dict("records"), default_flow_style=False, sort_keys=False),
        "to_python_records": lambda index=False: to_python_records(dataframe, index=index),
        "to_kv": lambda index=False: to_kv_rows(dataframe, index=index),
    }


def split_table(dataframe, n):
    n = max(1, min(n, len(dataframe) or 1))
    q, r = divmod(len(dataframe), n)
    out = []
    start = 0
    for i in range(n):
        stop = start + q + (i < r)
        out.append(dataframe.iloc[start:stop])
        start = stop
    return out


AGGS = ["SUM", "AVG", "MIN", "MAX"]
OPS = ["+", "-", "*"]


def sample_complexity(config):
    c = config.complexity
    return {
        "expr_depth": random.randint(0, c),
        "n_predicates": random.randint(0, c),
        "n_group_keys": min(random.randint(0, c), random.randint(0, 2)),
    }


def ident(c):
    return f'"{c}"'


def column_roles(df):
    dates = date_columns(df)
    return {
        "id": [c for c in ["row_id", "customer"] if c in df.columns],
        "num": [c for c in ["qty", "unit_price", "discount", "gross", "net"] if c in df.columns],
        "group": [c for c in ["country", "segment", "category", "status"] if c in df.columns],
        "date": [c for c in dates],
        "bool": [c for c in ["is_refund"] if c in df.columns],
    }


def num_expr(nums, depth):
    expr = ident(random.choice(nums))
    for _ in range(depth):
        expr = f"({expr} {random.choice(OPS)} {ident(random.choice(nums))})"
    return expr


def literal(x):
    if pd.isna(x):
        return "NULL"
    if hasattr(x, "isoformat"):
        return f"DATE '{x.isoformat()}'"
    if isinstance(x, str):
        return "'" + x.replace("'", "''") + "'"
    if isinstance(x, (float, np.floating)):
        return str(float(x))
    return str(x)


def predicate(df, roles):
    choices = []
    if roles["num"]:
        c = random.choice(roles["num"])
        q = df[c].quantile(random.choice([0.25, 0.5, 0.75]))
        if pd.notna(q):
            choices.append(f"{ident(c)} {random.choice(['>', '<', '>=', '<='])} {literal(q)}")
    if roles["group"]:
        c = random.choice(roles["group"])
        values = df[c].dropna().drop_duplicates()
        if len(values):
            vals = values.sample(min(2, len(values))).tolist()
            choices.append(f"{ident(c)} IN ({', '.join(literal(v) for v in vals)})")
    if roles["date"]:
        c = random.choice(roles["date"])
        values = df[c].dropna()
        if len(values):
            choices.append(f"{ident(c)} > {literal(values.sample(1).iloc[0])}")
    if roles["bool"]:
        c = random.choice(roles["bool"])
        choices.append(f"{ident(c)} = {random.choice(['TRUE', 'FALSE'])}")
    nullables = [c for c in ["segment", "discount"] if c in df.columns]
    if nullables:
        c = random.choice(nullables)
        choices.append(f"{ident(c)} IS {random.choice(['', 'NOT '])}NULL")
    return random.choice(choices) if choices else "TRUE"


def group_key_candidates(roles):
    out = [(ident(c), ident(c), ident(c)) for c in roles["group"]]
    for c in roles["date"]:
        expr = f"CAST(DATE_TRUNC('month', {ident(c)}) AS DATE)"
        alias = ident(f"{c}_month")
        out.append((f"{expr} AS {alias}", expr, alias))
    return out


def tie_breaker(df):
    if "row_id" in df.columns:
        return ident("row_id")
    return ident(df.columns[0])


def synthesize_query(df, spec):
    roles = column_roles(df)
    nums = roles["num"]
    if not nums and not roles["group"] and not roles["date"] and not roles["bool"]:
        return "SELECT COUNT(*) FROM dataframe"

    predicates = []
    for _ in range(spec["n_predicates"]):
        p = predicate(df, roles)
        if p not in predicates:
            predicates.append(p)
    where_sql = " AND ".join(predicates) if predicates else "TRUE"
    candidates = group_key_candidates(roles)
    group_keys = random.sample(candidates, min(spec["n_group_keys"], len(candidates)))

    if nums:
        value = num_expr(nums, spec["expr_depth"])
        agg = random.choice(AGGS)
    else:
        value = None
        agg = "COUNT"

    if group_keys:
        select_key, group_sql, order_key = group_keys[0]
        order_value = "COUNT(*)" if agg == "COUNT" else f"{agg}({value})"
        return f"""
        SELECT {select_key}
        FROM dataframe
        WHERE {where_sql}
        GROUP BY {group_sql}
        ORDER BY {order_value} {random.choice(["ASC", "DESC"])}, {order_key} ASC
        LIMIT 1
        """.strip()

    if nums and random.random() < 0.35:
        c = random.choice(nums)
        threshold = df[c].quantile(random.choice([0.25, 0.5, 0.75]))
        return f"""
        SELECT {agg}({value}) {random.choice([">", "<", ">=", "<="])} {literal(threshold)}
        FROM dataframe
        WHERE {where_sql}
        """.strip()

    if random.random() < 0.45:
        return f"""
        SELECT COUNT(*)
        FROM dataframe
        WHERE {where_sql}
        """.strip()

    if random.random() < 0.55:
        return f"""
        SELECT COUNT(*) > 0
        FROM dataframe
        WHERE {where_sql}
        """.strip()

    allowed = roles["id"] + roles["group"] + roles["date"] + roles["bool"]
    orderable = roles["num"] + roles["date"] + roles["group"] + roles["bool"]
    col = random.choice(allowed)
    order = random.choice(orderable)
    return f"""
    SELECT {ident(col)}
    FROM dataframe
    WHERE {where_sql}
    ORDER BY {ident(order)} {random.choice(["ASC", "DESC"])}, {tie_breaker(df)} ASC
    LIMIT 1
    """.strip()


def interesting_result(result):
    if result.empty:
        return False
    if result.shape != (1, 1):
        return False
    if result.shape == (1, 1):
        x = str(result.iloc[0, 0])
        return x not in {"0", "0.0", "1", "1.0", "nan", "None"}
    return False


def sample_query(df, conn, config, max_tries=80):
    for _ in range(max_tries):
        spec = sample_complexity(config)
        q = synthesize_query(df, spec)
        try:
            result = conn.execute(q).df()
        except Exception:
            continue
        if interesting_result(result):
            return q, result, spec
    raise RuntimeError("Could not synthesize interesting table QA query")


class TableQA(Task):
    summary = "Answer queries on tabular data by executing SQL queries over dataframes."
    def __init__(self, config=TableQAConfig()):
        super().__init__(config=config)
        self.balancing_key_ratio = 0.25

    def _query_family(self, query):
        q = " ".join(str(query).upper().split())
        return "+".join([
            "group" if " GROUP BY " in q else "nogroup",
            "limit" if " LIMIT " in q else "nolimit",
            "scalar" if "ROUND(" in q and " GROUP BY " not in q else "table",
        ])

    def _result_bucket(self, result):
        if result.shape != (1, 1):
            return f"rows={min(len(result), 4)}"
        try:
            x = float(result.iloc[0, 0])
            return "0" if x == 0 else "1" if x == 1 else "2-3" if x <= 3 else "4+"
        except Exception:
            return "text"
    
    def generate_entry(self):
        semantic_df = generate_tableqa_dataframe(self.config)
        display_df, display_meta = make_display_dataframe(
            semantic_df,
            number_formats=TABLEQA_NUMBER_FORMATS,
            number_locales=["en_US"],
        )

        conn = duckdb.connect()
        conn.register("dataframe", semantic_df)
        q, result, query_spec = sample_query(semantic_df, conn, self.config)
        renderers = get_renderers(display_df)
        fmt_name = random.choice(list(renderers))
        render_func = renderers[fmt_name]
        is_scalar = result.shape == (1, 1)
        answer_df = result if is_scalar else apply_display_formats(result, display_meta)
        
        tables = [render_func(index=False)]
        if self.config.num_tables > 1:
            tables = [
                get_renderers(part)[fmt_name](index=False)
                for part in split_table(display_df, self.config.num_tables)
            ]

        return Entry(
            metadata={
                "table": tables[0],
                "tables": tables,
                "query": q,
                "query_spec": query_spec,
                "query_family": self._query_family(q),
                "result_bucket": self._result_bucket(result),
                "is_scalar": is_scalar,
                "table_format": fmt_name,
                **display_meta,
            },
            answer=answer_df.to_csv(index=False, header=False).strip()
        )

    def render_prompt(self, m):
        fmt = "single value" if m['is_scalar'] else "CSV format (rows separated by newlines, values by commas). Do not include column headers."
        tables = m.get('tables') or [m['table']]
        if len(tables) == 1:
            preamble = "Execute this SQL query on the table named dataframe:"
        else:
            preamble = "The following tables are row-wise shards of one logical table named dataframe. Concatenate them in order to reconstruct dataframe, then execute the SQL query:"
        presentation = "\n\n".join(f"Table {i}:\n{table}" for i, table in enumerate(tables, 1))
        return f"{preamble}\n\n{presentation}\n\nSQL: {m['query']}\n\nThe answer is the result as {fmt}."

    def score_answer(self, ans, entry):
        def isnumeric(x):
            try: float(x); return True
            except: return False
                
        if entry.metadata['is_scalar'] and isnumeric(entry.answer):
            return score_scalar(ans, entry)
        
        # Strip potential header line: if first line matches column names from query, remove it
        def strip_header(s, reference):
            lines = s.strip().splitlines()
            ref_lines = reference.strip().splitlines()
            if len(lines) == len(ref_lines) + 1:
                # First line might be a header — check if remaining lines match
                candidate = "\n".join(lines[1:])
                if candidate.strip():
                    return candidate
            return s
        
        ans = strip_header(ans, entry.answer)
        
        if ans.strip() == entry.answer.strip(): return 1.0
        
        try:
            parse = lambda s: list(csv.reader(io.StringIO(s.strip())))
            a, e = parse(ans), parse(entry.answer)
            
            if len(a) != len(e): return 0.0
            for ar, er in zip(a, e):
                if len(ar) != len(er): return 0.0
                for av, ev in zip(ar, er):
                    try:
                        if abs(float(av) - float(ev)) > 0.01: return 0.0
                    except:
                        # Normalize date formats before comparing
                        av_clean = av.strip().replace("T00:00:00.000", "").replace("T00:00:00", "")
                        ev_clean = ev.strip().replace("T00:00:00.000", "").replace("T00:00:00", "")
                        if av_clean != ev_clean: return 0.0
            return 1.0
        except:
            return 0.0

    def balancing_key(self, problem):
        m = problem.metadata
        s = m.query_spec
        return (
            f"depth={s['expr_depth']}:pred={s['n_predicates']}:"
            f"group={s['n_group_keys']}:scalar={int(m.is_scalar)}:"
            f"bucket={m.result_bucket}"
        )

EQUIV_RENDERERS = [
    "to_csv", "to_tsv", "to_markdown", "to_grid", "to_html", "to_latex",
    "to_json", "to_jsonl", "to_yaml", "to_python_records", "to_kv",
]

STAT_RENDERERS = [
    "to_csv", "to_tsv", "to_markdown", "to_grid", "to_html",
    "to_json", "to_jsonl", "to_yaml", "to_python_records", "to_kv",
]


def permute_table(dataframe):
    df = dataframe.copy()
    cols = list(df.columns)
    random.shuffle(cols)
    df = df[cols]
    return df.sample(frac=1).reset_index(drop=True) if len(df) > 1 else df


def canonical_table(dataframe):
    df = dataframe.copy()
    df.columns = [str(c) for c in df.columns]
    cols = tuple(sorted(df.columns))
    df = df.reindex(cols, axis=1)
    body = sorted(tuple(str(row[c]) for c in cols) for _, row in df.iterrows())
    return cols, tuple(body)


def mutate_cell(x):
    if pd.isna(x):
        return "not missing"
    s = str(x)
    try:
        return str(float(s.replace(",", "")) + random.choice([-1, 1, 10]))
    except Exception:
        pass
    if len(s) >= 3:
        i = random.randrange(len(s))
        choices = [ch for ch in "abcdefghijklmnopqrstuvwxyz" if ch != s[i].lower()]
        return s[:i] + random.choice(choices) + s[i + 1:]
    return s + "_x"


def add_noise_row(df):
    row = {c: mutate_cell(random.choice(df[c].tolist())) if len(df[c]) else "x" for c in df.columns}
    return pd.concat([df, pd.DataFrame([row])], ignore_index=True)


def corrupt_table(dataframe):
    df = dataframe.copy()
    choices = ["cell", "column_name", "drop_row", "add_row", "drop_column", "add_column", "duplicate_row"]
    if len(df) <= 1:
        choices.remove("drop_row")
    if len(df.columns) <= 1:
        choices.remove("drop_column")

    kind = random.choice(choices)
    if kind == "cell":
        r, c = random.randrange(len(df)), random.choice(list(df.columns))
        df.loc[df.index[r], c] = mutate_cell(df.loc[df.index[r], c])
    elif kind == "column_name":
        c = random.choice(list(df.columns))
        df = df.rename(columns={c: f"{c}_x"})
    elif kind == "drop_row":
        df = df.drop(df.index[random.randrange(len(df))]).reset_index(drop=True)
    elif kind == "add_row":
        df = add_noise_row(df)
    elif kind == "drop_column":
        df = df.drop(columns=[random.choice(list(df.columns))])
    elif kind == "add_column":
        name = "extra"
        while name in df.columns:
            name += "_x"
        df[name] = [f"x{i}" for i in range(len(df))]
    elif kind == "duplicate_row":
        df = pd.concat([df, df.iloc[[random.randrange(len(df))]]], ignore_index=True)
    return df, kind


class TableEquivalence(Task):
    summary = "Decide if two rendered tables are semantically equivalent under mutations."
    def __init__(self, config=TableQAConfig()):
        super().__init__(config=config)
        self.balancing_key_ratio = 0.5
        self._same_next = False

    def generate_entry(self):
        semantic_df = generate_random_table(self.config)
        display_df, display_meta = make_display_dataframe(semantic_df)
        self._same_next = not self._same_next

        if self._same_next:
            other_df, answer, mutation = permute_table(display_df), "yes", "none"
        else:
            for _ in range(20):
                other_df, mutation = corrupt_table(display_df)
                other_df = permute_table(other_df)
                if canonical_table(other_df) != canonical_table(display_df):
                    break
            answer = "no"

        fmt_a, fmt_b = random.sample(EQUIV_RENDERERS, 2)
        return Entry(
            metadata={
                "table_a": get_renderers(display_df)[fmt_a](index=False),
                "table_b": get_renderers(other_df)[fmt_b](index=False),
                "format_a": fmt_a,
                "format_b": fmt_b,
                "mutation": mutation,
                **display_meta,
            },
            answer=answer,
        )

    def render_prompt(self, m):
        return (
            "Do these tables contain the same data?\n"
            "Ignore row order, column order, and table syntax. Match values by column name.\n\n"
            f"Table A:\n{m['table_a']}\n\n"
            f"Table B:\n{m['table_b']}\n\n"
            "Answer yes or no."
        )

    def score_answer(self, answer, entry):
        ans = str(answer).strip().lower().strip(".")
        if ans in {"yes", "y", "true", "same"}:
            ans = "yes"
        elif ans in {"no", "n", "false", "different"}:
            ans = "no"
        return float(ans == entry.answer)

    def balancing_key(self, problem):
        m = problem.metadata
        return f"{m.mutation}:formats={m.format_a}->{m.format_b}:answer={problem.answer}"


def pearson(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return 0.0 if np.std(a) == 0 or np.std(b) == 0 else float(np.corrcoef(a, b)[0, 1])


def abs_pearson(a, b):
    return abs(pearson(a, b))


def eta_squared(values, labels):
    values, labels = np.asarray(values, dtype=float), np.asarray(labels)
    mean, total = values.mean(), ((values - values.mean()) ** 2).sum()
    if total == 0:
        return 0.0
    return float(sum((labels == g).sum() * (values[labels == g].mean() - mean) ** 2 for g in set(labels)) / total)


def winner_with_margin(scores, need):
    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    margin = ordered[0][1] - ordered[1][1] if len(ordered) > 1 else ordered[0][1]
    return (ordered[0][0], margin) if margin >= need else (None, margin)


def gen_column_pearson(config):
    n, p = max(8, config.num_rows), max(4, config.num_numeric)
    for _ in range(100):
        x0 = np.random.normal(size=n)
        data = {"x0": np.round(x0, 2), "x1": np.round(x0 + np.random.normal(0, 0.06, n), 2)}
        for i in range(2, p):
            data[f"x{i}"] = np.round(0.25 * x0 + np.random.normal(0, 1.2, n), 2)
        df = pd.DataFrame(data)
        scores = {c: abs_pearson(df["x0"], df[c]) for c in df.columns if c != "x0"}
        answer, margin = winner_with_margin(scores, config.margin)
        if answer == "x1":
            return df, {
                "find": "column name most associated with column x0",
                "metric": "absolute Pearson correlation",
                "answer": answer, "family": "column_pearson", "margin": margin,
            }
    raise RuntimeError("Could not generate column Pearson table with sufficient margin")


def gen_row_pearson(config):
    n, p = max(8, config.num_rows), max(4, config.num_numeric)
    for _ in range(100):
        target = np.random.normal(size=p)
        rows = [target, target + np.random.normal(0, 0.06, p)]
        rows += [0.2 * target + np.random.normal(0, 1.3, p) for _ in range(n - 2)]
        df = pd.DataFrame(np.round(rows, 2), columns=[f"x{i}" for i in range(p)])
        df.insert(0, "row_id", [f"R{i}" for i in range(n)])
        scores = {r.row_id: pearson(df.loc[0, df.columns[1:]], r[df.columns[1:]]) for _, r in df.iloc[1:].iterrows()}
        answer, margin = winner_with_margin(scores, config.margin)
        if answer == "R1":
            return df, {
                "find": "row_id most associated with row R0",
                "metric": "Pearson correlation over numeric columns",
                "answer": answer, "family": "row_pearson", "margin": margin,
            }
    raise RuntimeError("Could not generate row Pearson table with sufficient margin")


def gen_label_eta2(config):
    n, p, k = max(9, config.num_rows), max(4, config.num_numeric), max(3, config.num_categories)
    for _ in range(100):
        labels = np.array([f"L{i % k}" for i in range(n)])
        np.random.shuffle(labels)
        group = {g: i * 3.0 for i, g in enumerate(sorted(set(labels)))}
        data = {"label": labels, "x0": np.round([group[g] + np.random.normal(0, 0.25) for g in labels], 2)}
        for i in range(1, p):
            data[f"x{i}"] = np.round(np.random.normal(0, 1.2, n), 2)
        df = pd.DataFrame(data)
        scores = {c: eta_squared(df[c], df["label"]) for c in df.columns if c != "label"}
        answer, margin = winner_with_margin(scores, config.margin)
        if answer == "x0":
            return df, {
                "find": "numeric column name most associated with column label",
                "metric": "eta squared",
                "answer": answer, "family": "label_eta2", "margin": margin,
            }
    raise RuntimeError("Could not generate eta squared table with sufficient margin")


def gen_categorical_nmi(config):
    if normalized_mutual_info_score is None:
        raise RuntimeError("scikit-learn is required for categorical NMI generation")
    n, p, k = max(9, config.num_rows), max(4, config.num_categories), max(3, config.num_categories)
    for _ in range(100):
        label = np.array([f"L{i % k}" for i in range(n)])
        np.random.shuffle(label)
        c0 = label.copy()
        for i in random.sample(range(n), max(1, n // 12)):
            c0[i] = f"L{random.randrange(k)}"
        data = {"label": label, "c0": c0}
        for i in range(1, p):
            data[f"c{i}"] = np.random.choice([f"L{j}" for j in range(k)], size=n)
        df = pd.DataFrame(data)
        scores = {c: normalized_mutual_info_score(df["label"], df[c]) for c in df.columns if c != "label"}
        answer, margin = winner_with_margin(scores, config.margin)
        if answer == "c0":
            return df, {
                "find": "categorical column name most associated with column label",
                "metric": "normalized mutual information",
                "answer": answer, "family": "categorical_nmi", "margin": margin,
            }
    raise RuntimeError("Could not generate categorical NMI table with sufficient margin")


class TableStatistics(Task):
    summary = "Compute statistical metrics (Pearson correlation, eta2, NMI) on tables."
    def __init__(self, config=TableStatisticsConfig()):
        super().__init__(config=config)
        self.balancing_key_ratio = 0.5

    def generate_entry(self):
        generators = [gen_column_pearson, gen_row_pearson, gen_label_eta2]
        if normalized_mutual_info_score is not None:
            generators.append(gen_categorical_nmi)
        semantic_df, spec = random.choice(generators)(self.config)
        display_df, display_meta = make_statistics_display_dataframe(semantic_df)
        fmt = random.choice(STAT_RENDERERS)
        table = get_renderers(display_df)[fmt](index=False)

        return Entry(
            metadata={
                "table": table,
                "find": spec["find"],
                "metric": spec["metric"],
                "payload": {"table": table, "find": spec["find"], "metric": spec["metric"]},
                "family": spec["family"],
                "margin": spec["margin"],
                "table_format": fmt,
                **display_meta,
            },
            answer=spec["answer"],
        )

    def render_prompt(self, m):
        return (
            f"{render_payload(m.payload)}\n\n"
            "Answer with only the identifier."
        )

    def score_answer(self, answer, entry):
        clean = lambda s: str(s).strip().strip("`'\"").lower()
        return float(clean(answer) == clean(entry.answer))

    def balancing_key(self, problem):
        m = problem.metadata
        return f"{m.family}:format={m.table_format}"
