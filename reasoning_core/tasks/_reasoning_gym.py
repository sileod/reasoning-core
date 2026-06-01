from reasoning_core.template import Task, Problem, Config
from dataclasses import dataclass
try:
    import reasoning_gym
except ImportError:
    reasoning_gym = None
import random
import json


@dataclass
class RGConfig(Config):
    rg_task: str = ""
    rg_level: int = 1

    def update(self, c):
        self.rg_level+=c

class Reasoning_Gym(Task):
    def __init__(self, config=RGConfig()):
        if reasoning_gym is None:
            raise ImportError("reasoning_gym is not installed.")
        self.datasets = [d for d in reasoning_gym.factory.DATASETS.keys() if d != 'composite']
        super().__init__(config)

    def generate(self):
        d = self.config.rg_task or random.choice(self.datasets)
        t, c_cls = reasoning_gym.factory.DATASETS[d]

        if d in reasoning_gym.factory.CURRICULA:
            cl = reasoning_gym.factory.CURRICULA[d]()
            cl.set_global_level(int(self.config.rg_level))
            c = cl.generate_configuration()
        else:
            c = c_cls()
            self.config.level = 0

        entry = t(c)[0]
        meta = entry['metadata'] | dict(task_name=f"RG.{d}", _question=entry['question'])
        return Problem(json.loads(json.dumps(meta, default=str)), str(entry['answer']))

    def score_answer(self, answer, entry):
        sd=entry['metadata']['source_dataset']
        scorer = reasoning_gym.get_score_answer_fn(sd)
        try:
            score = scorer(answer,entry)
        except Exception as e:
            print(f"Error scoring, T={entry['metadata']['task_name']} answer: {e}")
            score = 0
        return score

    def prompt(self, metadata):
        return metadata._question
