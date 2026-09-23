"""Replay add, drop, and swap registration requests over sections with seat caps
and FIFO waitlists.

A section seats up to its cap; a student who cannot get a seat is placed at the back
of that section's FIFO waitlist. Dropping a seated student promotes the front of the
section's waitlist (honouring their hold on the seat). Swapping exchanges two
students' full enrollment -- each moves to the other's section with the other's
seated-or-waiting status, a swapped-in student joining the back of any waitlist.

Three question modes share the same scenario: the final per-section roster (empty
sections omitted), a single student's final outcome, or one section's final waitlist
length.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import (
    Config,
    Entry,
    Task,
    stochastic_rounding as sround,
)

TASK_META = {'parent_source_id': None,
 'idea': 'registration_waitlist_replay (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_non_local_structured_r4/registration_waitlist_replay',
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

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@dataclass
class RegistrationWaitlistReplayConfig(Config):
    n_sections: int = 2
    cap_min: int = 1
    cap_max: int = 2
    n_students: int = 4
    n_ops: int = 3

    def apply_difficulty(self, level):
        self.n_sections = sround(self.n_sections + level)
        self.cap_min = sround(self.cap_min + level // 2)
        self.cap_max = self.cap_min + 2 + level
        self.n_students = sround(self.n_students + 2 * level)
        self.n_ops = sround(self.n_ops + 2 * level)


def _add(seated, wait, caps, sec, student):
    if len(seated[sec]) < caps[sec]:
        seated[sec].append(student)
    else:
        wait[sec].append(student)


def _drop(seated, wait, caps, sec, student):
    if student in seated[sec]:
        seated[sec].remove(student)
        while len(seated[sec]) < caps[sec] and wait[sec]:
            seated[sec].append(wait[sec].pop(0))
    elif student in wait[sec]:
        wait[sec].remove(student)


def _find_slot(seated, wait, sec, student):
    return 'seated' if student in seated[sec] else 'wait'


def _remove_slot(seated, wait, sec, slot, student):
    (seated[sec] if slot == 'seated' else wait[sec]).remove(student)


def _insert(seated, wait, sec, slot, student):
    (seated[sec] if slot == 'seated' else wait[sec]).append(student)


def _swap(seated, wait, s_a, sec_a, s_b, sec_b):
    slot_a = _find_slot(seated, wait, sec_a, s_a)
    slot_b = _find_slot(seated, wait, sec_b, s_b)
    _remove_slot(seated, wait, sec_a, slot_a, s_a)
    _remove_slot(seated, wait, sec_b, slot_b, s_b)
    _insert(seated, wait, sec_a, slot_a, s_b)
    _insert(seated, wait, sec_b, slot_b, s_a)


def _enrolled(seated, wait, sections):
    out = []
    for sec in sections:
        out.extend(seated[sec])
        out.extend(wait[sec])
    return out


def _pick_enrolled(seated, wait, sections):
    pool = []
    for sec in sections:
        for s in seated[sec]:
            pool.append(s)
        for s in wait[sec]:
            pool.append(s)
    s = random.choice(pool)
    for sec in sections:
        if s in seated[sec]:
            return s, sec
        if s in wait[sec]:
            return s, sec
    return s, sections[0]


def _swap_pairs(seated, wait, sections):
    nonempty = [sec for sec in sections if seated[sec] or wait[sec]]
    return [
        (a, b)
        for i, a in enumerate(nonempty)
        for b in nonempty[i + 1:]
    ]


def _locate(seated, wait, sections, student):
    for sec in sections:
        if student in seated[sec]:
            return sec, 'seated'
        if student in wait[sec]:
            return sec, 'wait'
    return None, None


def _gen_initial(sections, caps, students):
    seated = {sec: [] for sec in sections}
    wait = {sec: [] for sec in sections}
    for s in students:
        sec = random.choice(sections)
        if len(seated[sec]) < caps[sec]:
            seated[sec].append(s)
        else:
            wait[sec].append(s)
        if random.random() < 0.25:
            if s in seated[sec]:
                seated[sec].remove(s)
            elif s in wait[sec]:
                wait[sec].remove(s)
    return seated, wait


def _gen_ops(seated, wait, sections, caps, students, n_ops):
    ops = []
    for _ in range(n_ops):
        enrolled = _enrolled(seated, wait, sections)
        enrolled_set = set(enrolled)
        unenrolled = [s for s in students if s not in enrolled_set]
        swaps = _swap_pairs(seated, wait, sections)
        choices = []
        if unenrolled:
            choices.append('add')
        if enrolled:
            choices.append('drop')
        if swaps:
            choices.append('swap')
        if not choices:
            break
        kind = random.choice(choices)
        if kind == 'add':
            s = random.choice(unenrolled)
            sec = random.choice(sections)
            _add(seated, wait, caps, sec, s)
            ops.append(['add', s, sec])
        elif kind == 'drop':
            s, sec = _pick_enrolled(seated, wait, sections)
            _drop(seated, wait, caps, sec, s)
            ops.append(['drop', s, sec])
        else:
            a, b = random.choice(swaps)
            s_a = random.choice((seated[a] + wait[a]))
            s_b = random.choice((seated[b] + wait[b]))
            _swap(seated, wait, s_a, a, s_b, b)
            ops.append(['swap', s_a, a, s_b, b])
    return ops


def _roster_answer(seated, sections):
    pieces = []
    for sec in sections:
        if seated[sec]:
            pieces.append(f"{sec}:[{','.join(sorted(seated[sec]))}]")
    return '; '.join(pieces)


def _render_op(op):
    if op[0] == 'add':
        return f"add {op[1]} to section {op[2]}"
    if op[0] == 'drop':
        return f"drop {op[1]} from section {op[2]}"
    return f"swap {op[1]} (in section {op[2]}) with {op[3]} (in section {op[4]})"


def _parse_roster(text):
    out = {}
    for chunk in text.split(';'):
        chunk = chunk.strip()
        if not chunk or '[' not in chunk:
            continue
        letter, rest = chunk.split('[', 1)
        letter = letter.strip().rstrip(':').strip()
        rest = rest.rstrip(']')
        ids = [x.strip() for x in rest.split(',') if x.strip() != '']
        out[letter] = sorted(ids)
    return out


def _normalize_outcome(text):
    return ' '.join(text.strip().lower().split())


def _score_answer(answer, entry):
    mode = entry.metadata.get('mode')
    try:
        if mode == 'roster':
            return 1.0 if _parse_roster(answer) == _parse_roster(entry.answer) else 0.0
        if mode == 'outcome':
            return 1.0 if _normalize_outcome(answer) == _normalize_outcome(entry.answer) else 0.0
        if mode == 'waitsize':
            return 1.0 if int(answer.strip()) == int(entry.answer) else 0.0
    except (ValueError, TypeError, AttributeError):
        return 0.0
    return 0.0


class RegistrationWaitlistReplay(Task):
    summary = ("Replay add, drop, and swap requests over sections with seat caps and "
               "FIFO waitlists: failed adds queue, drops trigger promotion cascades "
               "honoring holds; answers give final rosters, one student's outcome, or "
               "waitlist sizes.")
    design_choice = ("Answer format: final roster as a canonical sorted list of student "
                     "IDs per section, with empty sections omitted.")
    config_cls = RegistrationWaitlistReplayConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        sections = list(_LETTERS[:cfg.n_sections])
        students = [f"s{i}" for i in range(cfg.n_students)]
        for _ in range(300):
            caps = {sec: random.randint(cfg.cap_min, cfg.cap_max) for sec in sections}
            seated, wait = _gen_initial(sections, caps, students)
            init_roster = [list(seated[sec]) for sec in sections]
            init_wait = [list(wait[sec]) for sec in sections]
            ops = _gen_ops(seated, wait, sections, caps, students, cfg.n_ops)
            mode = random.choice(['roster', 'roster', 'roster', 'outcome', 'waitsize'])
            enrolled = _enrolled(seated, wait, sections)
            enrolled_set = set(enrolled)
            unenrolled = [s for s in students if s not in enrolled_set]

            if mode == 'roster':
                if not any(seated[sec] for sec in sections):
                    continue
                answer = _roster_answer(seated, sections)
                target = None
            elif mode == 'waitsize':
                target = random.choice(sections)
                answer = str(len(wait[target]))
            else:
                if not enrolled:
                    continue
                if unenrolled and random.random() < 0.3:
                    target = random.choice(unenrolled)
                    answer = "not enrolled"
                else:
                    target = random.choice(enrolled)
                    sec, slot = _locate(seated, wait, sections, target)
                    answer = f"{slot} in {sec}"
            break
        else:
            raise RuntimeError("registration_waitlist_replay: failed to build instance")

        metadata = {
            'sections': sections,
            'caps': [caps[sec] for sec in sections],
            'init_roster': init_roster,
            'init_wait': init_wait,
            'students': students,
            'ops': ops,
            'mode': mode,
            'target': target,
            'answer': answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        sections = metadata['sections']
        caps = metadata['caps']
        lines = [
            "A university runs a course-registration system. Each section has a fixed "
            "number of seats. A student who cannot get a seat is placed at the back of "
            "that section's FIFO waitlist in arrival order; when a seated student is "
            "dropped, the freed seat goes to the front student on that section's "
            "waitlist. A swap exchanges the two chosen students' enrollments: each "
            "moves to the other's section with the other's seated-or-waiting status, "
            "joining the back of any waitlist.",
        ]
        cap_lines = [f"{sec}: {cap} seats" for sec, cap in zip(sections, caps)]
        lines.append("Sections and seat caps:\n" + "\n".join(cap_lines))
        init_lines = []
        for i, sec in enumerate(sections):
            init_lines.append(
                f"{sec}: roster {metadata['init_roster'][i]}, "
                f"waitlist {metadata['init_wait'][i]}"
            )
        lines.append("Enrollments at the start:\n" + "\n".join(init_lines))
        enrolled_initial = set()
        for i in range(len(sections)):
            enrolled_initial.update(metadata['init_roster'][i])
            enrolled_initial.update(metadata['init_wait'][i])
        not_enrolled = sorted(s for s in metadata['students'] if s not in enrolled_initial)
        lines.append("All other listed students are not enrolled: " + ", ".join(not_enrolled))
        ops_lines = "\n".join(
            f"{i}. {_render_op(op)}" for i, op in enumerate(metadata['ops'], 1)
        )
        lines.append("Registration requests, applied in order:\n" + ops_lines)
        if metadata['mode'] == 'roster':
            lines.append(
                "Give the final seated roster for every section. Format: for each "
                "non-empty section in alphabetical order, `Letter:[comma-separated "
                "sorted student IDs]`, empty sections omitted, sections joined by `; `, "
                "e.g. `A:[s1,s3]; B:[s2]`."
            )
        elif metadata['mode'] == 'outcome':
            lines.append(
                f"What is the final enrollment status of student {metadata['target']}? "
                "Answer `seated in <Letter>`, `waiting in <Letter>`, or `not enrolled`."
            )
        else:
            lines.append(
                f"What is the length of the FIFO waitlist for section "
                f"{metadata['target']} after all requests? Answer as a single integer."
            )
        return "\n\n".join(lines)

    def score_answer(self, answer, entry):
        return _score_answer(answer, entry)
