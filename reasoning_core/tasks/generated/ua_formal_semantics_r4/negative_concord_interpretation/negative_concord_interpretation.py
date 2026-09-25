import random

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'negative_concord_interpretation (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_semantics_r4/negative_concord_interpretation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3713447331,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class ConcordConfig(Config):
    max_embedded: int = 1
    max_neg: int = 2

    def apply_difficulty(self, level):
        self.max_embedded = 1 + level // 3
        self.max_neg = 2 + level // 2


NEG_INDEF = ["nobody", "nothing", "no one", "none of the members"]
OVERT = ["did not", "never", "didn't"]
PREDS = ["approve", "submit", "review", "attend", "acknowledge"]
COMP = ["that", "if"]


def _clause_pol(num_neg, within):
    if within == 'concord':
        return 1 if num_neg >= 1 else 0
    return num_neg % 2


def _licensed(embedded_overt, matrix_neg):
    return embedded_overt or matrix_neg


def _overall(clause_negs, clause_overt, is_emb, within, barrier):
    matrix_neg = _clause_pol(clause_negs[0], within) == 1
    total_neg = sum(clause_negs)
    for k in range(1, len(clause_negs)):
        if is_emb[k] and not _licensed(clause_overt[k], matrix_neg):
            return 'unlicensed'
    if barrier == 'barrier_on':
        pol = 0
        for k in range(len(clause_negs)):
            pol ^= _clause_pol(clause_negs[k], within)
        return 'negated' if pol == 1 else 'asserted'
    else:
        return 'negated' if (total_neg % 2) == 1 else 'asserted'


def _clause_text(num_neg, has_overt):
    subj = random.choice(["the committee", "the reviewer", "the board", "it"])
    pred = random.choice(PREDS)
    tokens = []
    types = []
    if has_overt:
        tokens.append(random.choice(OVERT))
        types.append('overt')
    for _ in range(max(0, num_neg - (1 if has_overt else 0))):
        tokens.append(random.choice(NEG_INDEF))
        types.append('ni')
    if not tokens:
        return f"{subj} {pred}"
    head = tokens[0]
    rest_toks = tokens[1:]
    if types[0] == 'overt':
        base = f"{subj} {head} {pred}"
    else:
        base = f"{head} {pred}"
    if rest_toks:
        base = base + " " + " and ".join(f"also {t}" for t in rest_toks)
    return base


class NegativeConcordInterpretation(Task):
    summary = "Derive semantic negation from negative indefinites, overt negators, concord domains, and embedding barriers under stated dialect rules; return the resulting truth conditions or an unlicensed reading."
    config_cls = ConcordConfig

    def generate_entry(self):
        within = random.choice(['concord', 'double_neg'])
        barrier = random.choice(['barrier_on', 'barrier_off'])
        n_embedded = random.randrange(0, self.config.max_embedded + 1)
        comps = [random.choice(COMP) for _ in range(n_embedded)]

        clauses_negs = []
        clauses_overt = []
        is_emb = [False]

        m_negs = random.randrange(0, self.config.max_neg + 1)
        m_overt = random.choice([True, False])
        if m_negs == 0 and m_overt:
            m_negs = 1
        clauses_negs.append(m_negs)
        clauses_overt.append(m_overt)

        for _ in range(n_embedded):
            e_negs = random.randrange(1, self.config.max_neg + 1)
            e_overt = random.choice([True, False])
            clauses_negs.append(e_negs)
            clauses_overt.append(e_overt)
            is_emb.append(True)

        answer = _overall(clauses_negs, clauses_overt, is_emb, within, barrier)

        sentence = _render_sentence(clauses_negs, clauses_overt, is_emb, comps)

        metadata = {
            'clauses': [[clauses_negs[i], clauses_overt[i], is_emb[i]] for i in range(len(clauses_negs))],
            'within': within,
            'barrier': barrier,
            'comps': comps,
            'sentence': sentence,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        within_note = ("Within a clause, several negatives realize a single negation (negative concord)."
                       if metadata['within'] == 'concord'
                       else "Within a clause, negatives cancel in pairs: even many yield no negation, odd many one negation.")
        barrier_note = ("A complementizer boundary is a barrier: each clause's negation is counted separately and combined by parity across clauses."
                        if metadata['barrier'] == 'barrier_on'
                        else "A complementizer boundary is transparent: all negatives from every clause pool together into one global count.")
        lic_note = ("A negative indefinite in an embedded clause is licensed only when that clause also contains an overt negator or the matrix is negated; otherwise the reading is unlicensed.")
        return (f"Under these dialect rules: {within_note}\n"
                f"{barrier_note}\n"
                f"{lic_note}\n\n"
                f"Sentence: \"{metadata['sentence']}\"\n\n"
                "State the overall truth conditions of the sentence as exactly one of: 'negated', 'asserted', or 'unlicensed'.")

    def score_answer(self, answer, entry):
        gold = entry.answer
        if isinstance(answer, str):
            a = answer.strip().lower()
            if a in ('negated', 'asserted', 'unlicensed'):
                return 1.0 if a == gold else 0.0
        return 0.0


def _render_sentence(clause_negs, clause_overt, is_emb, comps):
    parts = []
    for i in range(len(clause_negs)):
        text = _clause_text(clause_negs[i], clause_overt[i])
        if is_emb[i]:
            text = f"{comps[i - 1]} {text}"
        parts.append(text)
    return " ".join(parts)
