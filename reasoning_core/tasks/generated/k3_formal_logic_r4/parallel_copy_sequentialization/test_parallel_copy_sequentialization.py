import random
import unittest

from reasoning_core.template import Task
from reasoning_core.tasks.generated.k3_formal_logic_r4.parallel_copy_sequentialization.parallel_copy_sequentialization import (
    ParallelCopySequentialization,
    _emit_moves,
    _parse_moves,
    _verify,
)


class TestParallelCopy(unittest.TestCase):
    def test_roundtrip_gold(self):
        for level in (0, 2, 5, 6):
            for _ in range(20):
                cfg = ParallelCopySequentialization.config_cls()
                cfg.set_level(level)
                task = ParallelCopySequentialization(config=cfg)
                entry = task.generate_example()
                self.assertEqual(task.score_answer(entry.answer, entry), 1.0)

    def test_junk_scores_low(self):
        cfg = ParallelCopySequentialization.config_cls()
        task = ParallelCopySequentialization(config=cfg)
        entry = task.generate_example()
        self.assertLess(task.score_answer("", entry), 1.0)
        self.assertLess(task.score_answer("hello world", entry), 1.0)

    def test_verify_simulation(self):
        transfers = {1: 0, 2: 1}
        moves, _ = _emit_moves(transfers, 4, False)
        self.assertTrue(_verify(transfers, moves, 4))

    def test_two_cycle_swap(self):
        transfers = {0: 1, 1: 0}
        moves, _ = _emit_moves(transfers, 3, False)
        moves_str = "".join(moves)
        self.assertTrue("r0=r1;" in moves_str and "r1=r0;" in moves_str)
        self.assertNotIn("t=", moves_str)

    def test_chain_deep_first(self):
        transfers = {1: 0, 2: 1}
        moves, _ = _emit_moves(transfers, 3, False)
        moves_str = "".join(moves)
        self.assertLess(moves_str.index("r2=r1"), moves_str.index("r1=r0"))

    def test_long_cycle_uses_scratch(self):
        transfers = {0: 1, 1: 2, 2: 0}
        moves, _ = _emit_moves(transfers, 3, True)
        moves_str = "".join(moves)
        self.assertIn("t=r", moves_str)
        self.assertTrue(_verify(transfers, moves, 3))

    def test_wrong_moves_do_not_score_one(self):
        cfg = ParallelCopySequentialization.config_cls()
        cfg.set_level(2)
        task = ParallelCopySequentialization(config=cfg)
        entry = task.generate_example()
        n_regs = entry.metadata["n_regs"]
        gold_moves = _parse_moves(entry.answer)
        for a, b in gold_moves:
            if a == "t":
                continue
            wrong = "r0=r1"  # an overwrite that usually breaks correctness
            self.assertLess(task.score_answer(wrong, entry), 1.0)
            break


if __name__ == "__main__":
    unittest.main()
