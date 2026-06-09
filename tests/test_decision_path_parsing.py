from easydict import EasyDict as edict
from nltk import CFG, ChartParser

from reasoning_core.tasks import grammar as grammar_tasks
from reasoning_core.tasks.grammar import (
    DecisionPathParsing,
    GrammarConfig,
    decision_chain,
    leaf_rule_path,
    mark_token,
    numbered_grammar,
    tree_production,
)


def _grammar_and_tree():
    grammar = CFG.fromstring(
        """
        S -> A B | C D
        A -> X | Y
        X -> 'x'
        Y -> 'y'
        B -> 'b'
        C -> 'c'
        D -> 'd'
        """
    )
    tree = next(ChartParser(grammar).parse(["x", "b"]))
    return grammar, tree


def test_decision_path_helpers():
    grammar, tree = _grammar_and_tree()
    grammar_text, prod_to_id, lhs_counts = numbered_grammar(grammar)
    leaf_pos = tree.treepositions("leaves")[0]

    assert grammar_text.splitlines()[:3] == [
        "R0: S -> A B",
        "R1: S -> C D",
        "R2: A -> X",
    ]
    assert tree_production(tree) == grammar.productions()[0]
    assert leaf_rule_path(tree, leaf_pos) == [
        grammar.productions()[0],
        grammar.productions()[2],
        grammar.productions()[4],
    ]
    assert decision_chain(tree, leaf_pos, prod_to_id, lhs_counts) == ["R0", "R2"]
    assert mark_token(["x", "b"], 0) == "<M> x </M> b"


def test_decision_chain_skips_lexical_choices():
    grammar = CFG.fromstring(
        """
        S -> L
        L -> 'x' | 'y'
        """
    )
    tree = next(ChartParser(grammar).parse(["x"]))
    _, prod_to_id, lhs_counts = numbered_grammar(grammar)
    leaf_pos = tree.treepositions("leaves")[0]

    assert decision_chain(tree, leaf_pos, prod_to_id, lhs_counts) == []
    assert decision_chain(
        tree, leaf_pos, prod_to_id, lhs_counts, skip_lexical=False
    ) == ["R1"]


def test_decision_path_parsing_generation_prompt_and_score(monkeypatch):
    grammar, tree = _grammar_and_tree()

    def fake_generate_parse(_config):
        return edict(
            label="unambiguous",
            tokens=["x", "b"],
            g="\n".join(str(prod) for prod in grammar.productions()),
            parses=[tree],
            cot="",
        )

    monkeypatch.setattr(grammar_tasks, "generate_parse", fake_generate_parse)
    task = DecisionPathParsing(GrammarConfig())
    problem = task.generate_example()

    assert problem.answer == "R0 R2"
    assert problem.metadata.marked_string == "<M> x </M> b"
    assert problem.prompt.startswith("(GRAMMAR)\nR0: S -> A B\nR1: S -> C D")
    assert "\n(STRING)\n<M> x </M> b\n" in problem.prompt
    assert "S -> A B\nS -> C D" not in problem.prompt
    assert task.score_answer("  R0   R2\n", problem) == 1.0
    assert task.score_answer("R2 R0", problem) == 0.0


def test_decision_path_parsing_none_fallback(monkeypatch):
    grammar = CFG.fromstring(
        """
        S -> L
        L -> 'x' | 'y'
        """
    )
    tree = next(ChartParser(grammar).parse(["x"]))

    def fake_generate_parse(_config):
        return edict(
            label="unambiguous",
            tokens=["x"],
            g="\n".join(str(prod) for prod in grammar.productions()),
            parses=[tree],
        )

    monkeypatch.setattr(grammar_tasks, "generate_parse", fake_generate_parse)
    problem = DecisionPathParsing(GrammarConfig()).generate_example()

    assert problem.answer == "NONE"
    assert problem.metadata.marked_string == "<M> x </M>"


def test_decision_path_parsing_can_include_lexical_decisions(monkeypatch):
    grammar = CFG.fromstring(
        """
        S -> L
        L -> 'x' | 'y'
        """
    )
    tree = next(ChartParser(grammar).parse(["x"]))

    def fake_generate_parse(_config):
        return edict(
            label="unambiguous",
            tokens=["x"],
            g="\n".join(str(prod) for prod in grammar.productions()),
            parses=[tree],
        )

    config = GrammarConfig()
    config.skip_lexical_decisions = False
    config.min_decision_path_len = 1
    monkeypatch.setattr(grammar_tasks, "generate_parse", fake_generate_parse)
    problem = DecisionPathParsing(config).generate_example()

    assert problem.answer == "R1"
