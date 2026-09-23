import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class ParkingFunctionSimConfig(Config):
    max_spaces: int = 6
    min_spaces: int = 3
    cars_ratio: float = 1.2
    count: int = 5

    def apply_difficulty(self, level):
        self.min_spaces = 3 + level
        self.max_spaces = 6 + int(level * 1.5) + level
        self.cars_ratio = 1.2
        self.count = stochastic_rounding(self.count + level)


def _simulate(spaces, cars):
    occ = [False] * spaces
    failures = []
    displacement_sum = 0
    for pref in cars:
        if pref >= spaces:
            failures.append(len(failures))
            continue
        spot = pref
        while spot < spaces and occ[spot]:
            spot += 1
        if spot >= spaces:
            failures.append(len(failures))
        else:
            occ[spot] = True
            displacement_sum += spot - pref
    return occ, displacement_sum, failures


def _answer_of(spaces, cars, requested):
    occ, displacement_sum, failures = _simulate(spaces, cars)
    if requested == "occupancy":
        return "".join("1" if o else "0" for o in occ)
    if requested == "displacement":
        return str(displacement_sum)
    if requested == "first_failure":
        return str(failures[0] + 1) if failures else "none"
    if requested == "parkable":
        return "yes" if not failures else "no"


def _parse_spaces(spaces_repr):
    return spaces_repr


class ParkingFunctionSimulation(Task):
    summary = "Drive cars one at a time onto a one-way street: each takes its preferred space or the next free space beyond; answers are the final occupancy list, total displacement, the index of the first car that fails, or a parkable/not verdict."
    design_choice = "Vary the number of cars relative to the number of spaces, sometimes exceeding it, so the answer includes the failure index when applicable."
    config_cls = ParkingFunctionSimConfig

    def generate_entry(self):
        spaces = random.randint(self.config.min_spaces, self.config.max_spaces)
        cars = int(spaces * self.config.cars_ratio) + random.randint(-2, 1)
        cars = max(0, cars)
        cars = [random.randint(0, spaces - 1) for _ in range(cars)]
        requested = random.choice(
            ["occupancy", "displacement", "first_failure", "parkable"])
        answer = _answer_of(spaces, cars, requested)
        if requested == "first_failure" or requested == "parkable":
            assert answer in ("yes", "no", "none") or answer != "none"
        occ, displacement_sum, failures = _simulate(spaces, cars)
        if requested == "occupancy":
            assert _answer_of(spaces, cars, "occupancy") == answer
        elif requested == "displacement":
            assert _answer_of(spaces, cars, "displacement") == answer
        elif requested == "parkable":
            assert (answer == "yes") == (not failures)
        else:
            assert answer == "none" or (int(answer) - 1) == failures[0]
        return Entry(metadata={
            "spaces": spaces,
            "cars": cars,
            "requested": requested,
        }, answer=answer)

    def render_prompt(self, metadata):
        spaces = metadata["spaces"]
        cars = metadata["cars"]
        requested = metadata["requested"]
        asked = {
            "occupancy": f"the list of spaces that end up occupied, as a string of 1s (occupied) and 0s (free) of length {spaces}",
            "displacement": "the total number of spaces moved past preferred spots summed over all cars that found a spot",
            "first_failure": "the position (1-indexed) of the first car that fails to find a spot, or the word none if every car parks",
            "parkable": "whether every car can park, as the single word yes or no",
        }[requested]
        prefs = " ".join(str(c) for c in cars)
        return (
            f"Cars arrive one at a time onto a one-way street with {spaces} parking "
            f"spaces numbered 0 to {spaces - 1}. Each car states its preferred spot. "
            f"A car parks at its preferred spot if it is free; otherwise it moves "
            f"forward to the next free spot beyond (there is no backing up). "
            f"After the car with preferred spot {spaces - 1}, a car that finds no free "
            f"spot at or beyond its preference fails and does not park.\n"
            f"The cars arrive in this order with these preferred spots: {prefs}.\n"
            f"What is {asked}? Answer with the required value only."
        )

    def score_answer(self, answer, entry):
        spaces = entry.metadata["spaces"]
        requested = entry.metadata["requested"]
        if requested == "occupancy":
            return 1.0 if isinstance(answer, str) and answer == _answer_of(
                spaces, entry.metadata["cars"], "occupancy") else 0.0
        if requested == "parkable":
            return 1.0 if answer == _answer_of(
                spaces, entry.metadata["cars"], "parkable") else 0.0
        if requested == "first_failure":
            return 1.0 if isinstance(answer, str) and answer.strip() == _answer_of(
                spaces, entry.metadata["cars"], "first_failure") else 0.0
        norm = str(float(answer)) if isinstance(answer, (int, float)) else None
        gold = _answer_of(spaces, entry.metadata["cars"], "displacement")
        if isinstance(answer, str):
            norm = answer.strip()
        return 1.0 if norm == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'parking_function_simulation (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_surface_invariance_r4/parking_function_simulation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
