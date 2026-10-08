"""Filter one table by two conditions, join it with a second, and compare years.

From level 2 the person is identified through their manager (a join), and from level 3 also by start year,
with same-team, same-city colleagues who started later. Ported from tasksource.jev.procedural.table_lookup.
"""
import json
import random
from dataclasses import dataclass

from reasoning_core.decision import Decision, render_records
from reasoning_core.template import Config, Entry, Task, stochastic_rounding as sround

CITIES = ["Oslo", "Lima", "Accra", "Hanoi", "Quito", "Porto", "Dakar", "Perth", "Tunis", "Osaka",
          "Bergen", "Cusco", "Lagos", "Hue", "Cuenca", "Braga", "Thies", "Darwin", "Sfax", "Kobe"]
PEOPLE = ["Ada", "Bruno", "Chloe", "Dmitri", "Elif", "Farah", "Goran", "Hana", "Ines", "Jonas",
          "Kenji", "Lena", "Malik", "Nora", "Omar", "Priya", "Quinn", "Rosa", "Sven", "Tariq",
          "Uma", "Viktor", "Wen", "Ximena", "Yusuf", "Zoe", "Amir", "Bea", "Carlos", "Dara",
          "Emeka", "Freya", "Gil", "Hugo", "Ivy", "Jae", "Kofi", "Lucia", "Mei", "Nils"]
TEAMS = ["billing", "search", "mobile", "security", "data", "support"]
COUNTS = [str(i) for i in range(10)]  # Jev scores have at most 10 levels


@dataclass
class TableLookupConfig(Config):
    n_people: float = 6
    join: bool = False      # name the team by its manager
    by_year: bool = False   # also filter by start year, against same-team same-city colleagues

    def apply_difficulty(self, level):
        self.n_people = self.n_people * 1.5 ** level
        self.join, self.by_year = level >= 2, level >= 3


class TableLookup(Task):
    summary = "Look up, join and count over two small tables, asked as typed decisions over one shared state."
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or TableLookupConfig())

    def generate_entry(self, state_seed=None, question=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, c = random.Random(state_seed), self.config
        n = min(len(PEOPLE) - len(TEAMS), max(4, sround(c.n_people * rng.uniform(0.8, 1.2), seed=rng.random())))
        cities = rng.sample(CITIES, 4)
        people = [{"name": name, "team": rng.choice(TEAMS), "city": rng.choice(cities),
                   "start_year": rng.randint(2008, 2024)} for name in rng.sample(PEOPLE, n)]
        managers = rng.sample([p for p in PEOPLE if p not in {q["name"] for q in people}], len(TEAMS))
        teams = [{"team": team, "manager": manager} for team, manager in zip(TEAMS, managers)]

        person = rng.choice(people)
        cut = min(person["start_year"] + rng.randint(1, 3), 2025) if c.by_year else None
        peers = [p for p in people if p is not person and (p["team"], p["city"]) == (person["team"], person["city"])]
        if c.by_year:  # colleagues sharing team and city started too late to match
            for other in rng.sample([p for p in people if p is not person], min(2, len(people) - 1)):
                other.update(team=person["team"], city=person["city"])
            for other in people:
                if other is not person and (other["team"], other["city"]) == (person["team"], person["city"]):
                    other["start_year"] = rng.randint(cut, cut + 4)
        else:  # make the (team, city) pair unique to the chosen person
            for other in peers:
                other["city"] = rng.choice([x for x in cities if x != person["city"]])
        near = [p["name"] for p in people if p is not person and (p["team"] == person["team"] or p["city"] == person["city"])]
        rest = [p["name"] for p in people if p is not person and p["name"] not in near]
        n_options = rng.randint(6, 40)  # varied option counts, capped by the table
        options = sorted([person["name"], *(rng.sample(near, len(near)) + rest)[:n_options - 1]], key=lambda _: rng.random())

        subject = rng.choice(people)
        manager = {t["team"]: t["manager"] for t in teams}[subject["team"]]
        year = subject["start_year"] + rng.choice([-2, -1, 1, 2])
        while True:  # exact counts only: redraw rather than clip to the scale
            city, since = rng.choice(cities), rng.randint(2010, 2022)
            matches = sum(p["city"] == city and p["start_year"] >= since for p in people)
            if matches < len(COUNTS):
                break
        listed = rng.sample(managers, len(managers))
        team_manager = {t["team"]: t["manager"] for t in teams}[person["team"]]

        style = rng.choice(["json", "table", "csv"])
        state = (json.dumps({"people": people, "teams": teams}, ensure_ascii=False) if style == "json" else
                 f"people:\n{render_records(people, style)}\n\nteams:\n{render_records(teams, style)}")
        team = f"the team managed by {team_manager}" if c.join else f"the {person['team']} team"
        after = f" and started before {cut}" if c.by_year else ""
        questions = {
            "find_person": Decision(person["name"], criteria=dict.fromkeys(options), instructions=rng.choice([
                f"Who is on {team} and based in {person['city']}{after}?",
                f"Which person works in {person['city']} on {team}{after}?"])),
            "manager_of": Decision(manager, criteria=dict.fromkeys(listed), instructions=rng.choice([
                f"Who manages the team that {subject['name']} belongs to?",
                f"Who is the manager of {subject['name']}'s team?"])),
            "started_before": Decision(subject["start_year"] < year, type="noul", instructions=rng.choice([
                f"Did {subject['name']} start before {year}?",
                f"Is {subject['name']}'s start year earlier than {year}?"])),
            "count_matching": Decision(matches, type="score", criteria=COUNTS, instructions=rng.choice([
                f"How many people based in {city} started in {since} or later?",
                f"Count the people in {city} whose start year is {since} or later."])),
        }
        qid = question or random.choice(sorted(questions))   # the question, unlike the state, is not seeded
        return Entry({"payload": state, "state_seed": state_seed, "question_id": qid}, questions[qid])
