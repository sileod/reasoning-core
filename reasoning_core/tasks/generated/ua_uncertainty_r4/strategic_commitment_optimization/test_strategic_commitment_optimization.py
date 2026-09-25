import random

from reasoning_core.tasks.generated.ua_uncertainty_r4.strategic_commitment_optimization.strategic_commitment_optimization import StrategicCommitmentOptimization


def test_module_level_sanity():
    task = StrategicCommitmentOptimization()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert ex.answer in ex.metadata["leader_actions"]
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) != 1.0
        assert task.score_answer("nonsense", ex) != 1.0


def test_solver_bruteforce_agreement():
    task = StrategicCommitmentOptimization()
    for _ in range(200):
        ex = task.generate_example()
        la = ex.metadata["leader_actions"]
        fa = ex.metadata["follower_actions"]
        lp = ex.metadata["leader_pay"]
        fp = ex.metadata["follower_pay"]
        best_com = None
        best_val = None
        for li, a in enumerate(la):
            best_f = None
            best_fv = None
            for fi in range(len(fa)):
                p = fp[li][fi]
                if best_fv is None or p > best_fv:
                    best_fv = p
                    best_f = fi
            eff = lp[li][best_f]
            if best_val is None or eff > best_val:
                best_val = eff
                best_com = a
        assert ex.answer == best_com


def test_deterministic_generation():
    random.seed(12345)
    task = StrategicCommitmentOptimization()
    a = [task.generate_example().answer for _ in range(5)]
    random.seed(12345)
    task2 = StrategicCommitmentOptimization()
    b = [task2.generate_example().answer for _ in range(5)]
    assert a == b
