"""Optimality-theoretic tableau ranking tasks.

Given a constraint ranking and a set of candidates each with a vector of
violation counts per constraint (lower is better), find the optimal winner by
comparing violation vectors under the ranking, resolve ties, and answer the
winning candidate, the eliminated set, or a reranking that changes the winner.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'optimality_theory_tableau_ranking (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_systematic_generalization_r4/optimality_theory_tableau_ranking',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_LABELS = ["A", "B", "C", "D", "E", "F"]
_QUERY_WINNER = "winner"
_QUERY_ELIM = "eliminated"
_QUERY_RERANK = "reranking"


def _score(vec, ranking):
    """Violation-vector score under ranking: tuple of counts, high-priority first."""
    return tuple(vec[i] for i in ranking)


def _winner(rows, ranking):
    """rows: list[(label, vec)]. Return winner label under ranking (lower score better)."""
    best_label = None
    best_score = None
    for label, vec in rows:
        sc = _score(vec, ranking)
        if best_score is None or sc < best_score:
            best_label = label
            best_score = sc
    return best_label


def _best_labels(rows, ranking):
    """List of labels tied for optimal (all with minimal score)."""
    scored = sorted((_score(vec, ranking), label) for label, vec in rows)
    best = scored[0][0]
    return [lb for sc, lb in scored if sc == best]


def _is_ranking(perm, n):
    return isinstance(perm, list) and len(perm) == n and sorted(perm) == list(range(n))


@dataclass
class OptimalityConfig(Config):
    level: int = 0
    n_constraints: int = 3
    n_candidates: int = 3
    max_viol: int = 1

    def apply_difficulty(self, level):
        self.level = level
        self.n_constraints = 3 + level // 2
        self.n_candidates = 3 + (level + 1) // 2
        self.max_viol = 2 if level >= 4 else 1


class OptimalityTheoryTableauRanking(Task):
    summary = "Evaluate optimality-theoretic tableaux: compare violation vectors under a constraint ranking, resolve ties, and answer the winning candidate, eliminated set, or reranking that changes the winner."
    config_cls = OptimalityConfig
    design_choice = "Answer format varies by query type: winner as candidate label, eliminated set as sorted list of labels, reranking as ordered constraint indices."

    def generate_entry(self):
        n_c = self.config.n_constraints
        n_cand = self.config.n_candidates
        max_v = self.config.max_viol
        labels = _LABELS[:n_cand]

        query = random.choice([_QUERY_WINNER, _QUERY_ELIM, _QUERY_RERANK])

        for _ in range(200):
            rows = [(lb, [random.randint(0, max_v) for _ in range(n_c)]) for lb in labels]
            ranking = list(range(n_c))
            random.shuffle(ranking)

            if query == _QUERY_WINNER:
                winners = _best_labels(rows, ranking)
                if len(winners) == 1:
                    return self._build(rows, ranking, query, winners[0])
            elif query == _QUERY_ELIM:
                winners = _best_labels(rows, ranking)
                elim = sorted(set(labels) - set(winners))
                if 0 < len(elim) < n_cand:
                    return self._build(rows, ranking, query, ",".join(elim))
            else:
                new_ranking = list(range(n_c))
                random.shuffle(new_ranking)
                w_old = _winner(rows, ranking)
                w_new = _winner(rows, new_ranking)
                if w_new != w_old:
                    return self._build(rows, ranking, query,
                                       ",".join(str(i) for i in new_ranking))

        raise RuntimeError("could not generate valid instance")

    def _build(self, rows, ranking, query, answer):
        metadata = {
            "rows": [[lb, list(vec)] for lb, vec in rows],
            "ranking": list(ranking),
            "query": query,
            "n_constraints": self.config.n_constraints,
            "n_candidates": self.config.n_candidates,
            "labels": [lb for lb, _ in rows],
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        n_c = metadata["n_constraints"]
        labels = metadata["labels"]
        lines = [
            "Optimality-theoretic tableau. The constraint ranking, highest priority first, is:",
            "  " + "  ".join(f"C{i}" for i in metadata["ranking"]),
            "",
            "Candidates: each '*' below a column counts as one violation of that "
            "constraint ('-' means zero violations). Columns are the constraints C0.."
            f"C{n_c-1} in that order.",
            "",
        ]
        for lb, vec in metadata["rows"]:
            cells = ["*" * v if v else "-" for v in vec]
            lines.append(f"  {lb}: {'  '.join(cells)}")
        lines.append("")
        lines.append("A candidate is optimal if no other candidate has fewer violations on the "
                     "highest-ranked constraint. Ties there are broken by the next constraint down "
                     "the ranking, and a candidate that ties on every constraint ties overall.")

        query = metadata["query"]
        if query == "winner":
            lines.append("")
            lines.append("Which candidate is the sole optimal winner? Answer with the single "
                         f"candidate label, chosen from {'/'.join(labels)}.")
        elif query == "eliminated":
            lines.append("")
            lines.append("All candidates except the optimal one(s) are eliminated. List the "
                         "eliminated candidate labels as a comma-separated, alphabetically sorted "
                         f"string, chosen from {'/'.join(labels)}. Example: if A is eliminated "
                         "but B is not, answer 'A'.")
        else:
            lines.append("")
            lines.append("Give a different permutation of the constraint order (highest priority "
                         "first) whose optimal winner differs from the winner under the ranking "
                         "shown above. Answer with the reranking as a comma-separated list of "
                         f"constraint indices from 0..{n_c-1}. Example: '1,0,2'.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        metadata = entry.metadata
        query = metadata["query"]
        rows = [(lb, list(vec)) for lb, vec in metadata["rows"]]
        ranking = list(metadata["ranking"])
        ans = answer.strip()

        if query in ("winner", "eliminated"):
            return 1.0 if ans == entry.answer else 0.0

        try:
            parsed = [int(x) for x in ans.split(",") if x != ""]
        except ValueError:
            return 0.0
        if _is_ranking(parsed, len(ranking)) and \
                _winner(rows, parsed) != _winner(rows, ranking):
            return 1.0
        return 0.0
