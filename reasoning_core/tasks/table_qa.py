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
from reasoning_core.template import Task, DevTask, Problem, Config, Payload, stochastic_rounding as sround
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
    num_rows: int = 5
    num_columns: int = 2
    num_tables: int = 1
    def update(self, c):
        self.num_rows = int(self.num_rows * (1+c))
        self.num_columns += c
        self.num_tables = min(self.num_tables+c, 2)

    def apply_difficulty(self, level):
        self.num_rows = sround(self.num_rows * (2 ** level))
        self.num_columns = sround(self.num_columns + level)
        self.num_tables = sround(min(self.num_tables + level, 2))


@dataclass
class TableStatisticsConfig(Config):
    num_rows: int = 9
    num_numeric: int = 4
    num_categories: int = 3
    margin: float = 0.45
    def update(self, c):
        self.num_rows = int(self.num_rows * (1 + c / 2))
        self.num_numeric += c
        self.num_categories += c
        self.margin = max(0.08, self.margin * (0.85 ** c))

    def apply_difficulty(self, level):
        self.num_rows = sround(self.num_rows * (1.5 ** level))
        self.num_numeric = sround(self.num_numeric + level)
        self.num_categories = sround(self.num_categories + level)
        self.margin = max(0.08, self.margin * (0.85 ** level))


_faker = Faker()

LOCALES = ["en_US", "fr_FR"]
DATE_FORMATS = ["yyyy-MM-dd", "d MMM yyyy", "MMM d, yyyy", "yyyy/MM/dd"]
NUMBER_FORMATS = ["#,##0.##", "#,##0.00", "#,##0.##", "#,##0.00", "0.###E0"]
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

def is_date_series(s):
    xs = s.dropna()
    return len(xs) and xs.map(lambda x: hasattr(x, "strftime")).all()


def date_columns(dataframe):
    return [c for c in dataframe.columns if is_date_series(dataframe[c])]


def render_date_series(s):
    locale, fmt = random.choice(LOCALES), random.choice(DATE_FORMATS)
    out = s.map(lambda x: format_date(x, fmt, locale=locale) if pd.notna(x) else x)
    return out, {"kind": "date", "format": fmt, "locale": locale}


def render_number_series(s):
    locale, fmt = random.choice(LOCALES), random.choice(NUMBER_FORMATS)
    out = s.map(lambda x: format_decimal(x, format=fmt, locale=locale) if pd.notna(x) else x)
    return out, {"kind": "number", "format": fmt, "locale": locale}


def render_bool_series(s):
    mapping = random.choice(BOOL_FORMATS)
    return s.map(lambda x: mapping.get(x, x)), {"kind": "bool", "mapping": mapping}


def render_nulls(s):
    token = random.choice(NULL_TOKENS)
    return s.map(lambda x: token if pd.isna(x) else x), {"null": token}


def make_display_dataframe(dataframe):
    df, meta = dataframe.copy(), {}
    for c in df.columns:
        s = df[c]
        if is_date_series(s):
            df[c], meta[c] = render_date_series(s)
        elif pd.api.types.is_bool_dtype(s):
            df[c], meta[c] = render_bool_series(s)
        elif pd.api.types.is_numeric_dtype(s):
            df[c], meta[c] = render_number_series(s)
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
            df[c] = df[c].map(lambda x: spec["mapping"].get(x, x))
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


class TableQA(Task):
    def __init__(self, config=TableQAConfig()):
        super().__init__(config=config)
        self.balancing_key_ratio = 0.25

    def _query_family(self, query):
        q = " ".join(str(query).upper().split())
        rules = [
            ("count_distinct", "COUNT(DISTINCT" in q),
            ("count_like", "COUNT(*)" in q and "LIKE" in q),
            ("count_where", "COUNT(*)" in q and "WHERE" in q),
            ("aggregate", q.startswith("SELECT ROUND(")),
            ("group_limit", "GROUP BY" in q),
            ("order_limit", "ORDER BY" in q and "LIMIT" in q),
        ]
        for name, ok in rules:
            if ok:
                return name
        return "other"

    def _result_bucket(self, result):
        if result.shape != (1, 1):
            return f"rows={min(len(result), 4)}"
        try:
            x = float(result.iloc[0, 0])
            return "0" if x == 0 else "1" if x == 1 else "2-3" if x <= 3 else "4+"
        except Exception:
            return "text"
    
    def _query(self, dataframe):
        if len(dataframe) == 0: return "SELECT COUNT(*) FROM dataframe"

        dates = date_columns(dataframe)
        num = dataframe.select_dtypes('number').columns.tolist()
        cat = [c for c in dataframe.select_dtypes(exclude='number').columns if c not in dates]
        order = random.choice(['ASC', 'DESC'])
        esc = lambda s: str(s).replace("'", "''")
        
        queries = []
        if num:
            c = random.choice(num)
            queries += [
                f"SELECT ROUND({random.choice(['SUM', 'AVG', 'MAX', 'MIN'])}({c}), 2) FROM dataframe",
                f"SELECT COUNT(*) FROM dataframe WHERE {c} > {dataframe[c].quantile(random.choice([0.3, 0.5, 0.7]))}",
                f"SELECT * FROM dataframe ORDER BY {c} {order} LIMIT {random.randint(1, 3)}"
            ]
            if len(num) >= 2:
                n1, n2 = random.sample(num, 2)
                queries.append(f"SELECT ROUND(AVG({n1} * {n2}), 2) FROM dataframe")

        if dates:
            c = random.choice(dates)
            cutoff = dataframe[c].sample(1).iloc[0].isoformat()
            queries += [
                f"SELECT * FROM dataframe ORDER BY {c} {order} LIMIT {random.randint(1, 3)}",
                f"SELECT COUNT(DISTINCT {c}) FROM dataframe",
                f"SELECT COUNT(*) FROM dataframe WHERE {c} > DATE '{cutoff}'",
            ]

        if num and cat:
            n, c = random.choice(num), random.choice(cat)
            val = esc(dataframe[c].iloc[0])
            queries += [
                f"SELECT {c}, SUM({n}) as v FROM dataframe GROUP BY {c} ORDER BY v {order} LIMIT {random.randint(1, 3)}",
                f"SELECT COUNT(*) FROM dataframe WHERE {c} = '{val}' AND {n} > {dataframe[n].mean()}",
            ]

        if cat:
            c = random.choice(cat)
            val = esc(dataframe[c].iloc[random.randint(0, len(dataframe)-1)])
            queries += [
                f"SELECT COUNT(DISTINCT {c}) FROM dataframe",
                f"SELECT COUNT(*) FROM dataframe WHERE {c} = '{val}'",
            ]
            if len(val) > 1:
                queries.append(f"SELECT COUNT(*) FROM dataframe WHERE CAST({c} AS VARCHAR) LIKE '%{val[1:]}%'")

        return random.choice(queries) if queries else "SELECT COUNT(*) FROM dataframe"
    
    def generate(self):
        semantic_df = generate_random_table(self.config)
        display_df, display_meta = make_display_dataframe(semantic_df)

        q = self._query(semantic_df)
        conn = duckdb.connect()
        conn.register("dataframe", semantic_df)
        result = conn.execute(q).df()
        renderers = get_renderers(display_df)
        fmt_name = random.choice(list(renderers))
        render_func = renderers[fmt_name]
        is_scalar = result.shape == (1, 1)
        answer_df = result if is_scalar else apply_display_formats(result, display_meta)
        
        tables = [render_func(index=False)]
        if self.config.level > 0 and self.config.num_tables > 1:
            tables = [
                get_renderers(part)[fmt_name](index=False)
                for part in split_table(display_df, self.config.num_tables)
            ]

        return Problem(
            metadata={
                "table": tables[0],
                "tables": tables,
                "query": q,
                "query_family": self._query_family(q),
                "result_bucket": self._result_bucket(result),
                "is_scalar": is_scalar,
                "table_format": fmt_name,
                **display_meta,
            },
            answer=answer_df.to_csv(index=False, header=False).strip()
        )

    def prompt(self, m):
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
        return f"{m.query_family}:scalar={int(m.is_scalar)}:bucket={m.result_bucket}"

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
    def __init__(self, config=TableQAConfig()):
        super().__init__(config=config)
        self.balancing_key_ratio = 0.5
        self._same_next = False

    def generate(self):
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
        return Problem(
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

    def prompt(self, m):
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
    def __init__(self, config=TableStatisticsConfig()):
        super().__init__(config=config)
        self.balancing_key_ratio = 0.5

    def generate(self):
        generators = [gen_column_pearson, gen_row_pearson, gen_label_eta2]
        if normalized_mutual_info_score is not None:
            generators.append(gen_categorical_nmi)
        semantic_df, spec = random.choice(generators)(self.config)
        display_df, display_meta = make_statistics_display_dataframe(semantic_df)
        fmt = random.choice(STAT_RENDERERS)
        table = get_renderers(display_df)[fmt](index=False)

        return Problem(
            metadata={
                "table": table,
                "find": spec["find"],
                "metric": spec["metric"],
                "payload": Payload(table=table, find=spec["find"], metric=spec["metric"]),
                "family": spec["family"],
                "margin": spec["margin"],
                "table_format": fmt,
                **display_meta,
            },
            answer=spec["answer"],
        )

    def prompt(self, m):
        return (
            f"{Payload(m.payload)}\n\n"
            "Answer with only the identifier."
        )

    def score_answer(self, answer, entry):
        clean = lambda s: str(s).strip().strip("`'\"").lower()
        return float(clean(answer) == clean(entry.answer))

    def balancing_key(self, problem):
        m = problem.metadata
        return f"{m.family}:format={m.table_format}"
