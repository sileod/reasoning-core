"""Independent readers of rendered extraction documents (no generator helpers or latent metadata).

Forty seeds at each level: 200 documents per task. Unknown syntax fails loudly.
"""
import json
import re
import signal
from datetime import datetime
from functools import lru_cache
from html.parser import HTMLParser
from xml.etree import ElementTree as ET

import pytest

from reasoning_core import get_task
from reasoning_core.decision import score_extraction


@lru_cache(None)
def _task(name):
    return get_task(name + "_extraction")


def _value(v):
    return str(v).lower() if isinstance(v, bool) else str(v)


def _pack(field, values):
    values = list(dict.fromkeys(values))
    if field['type'] == 'list':
        return values or None
    assert len(values) <= 1, (field, values)
    return next(iter(values), None)


def _lookup(tree, path):
    for key in path.split('.'):
        tree = tree.get(key, {})
    return tree


def _yaml(text):
    """Small indentation reader for mappings and lists; leaves stay lexical strings."""
    lines = [(len(s) - len(s.lstrip()), s.strip()) for s in text.splitlines() if s.strip()]
    def read(i, indent):
        out = [] if lines[i][1].startswith('- ') else {}
        while i < len(lines) and lines[i][0] == indent:
            s = lines[i][1]
            if isinstance(out, list):
                # A list item is a mapping; consume it as its own indented document.
                end = i + 1
                while end < len(lines) and lines[end][0] > indent:
                    end += 1
                body = ' ' * (indent + 2) + s[2:] + '\n'
                body += '\n'.join(' ' * n + t for n, t in lines[i + 1:end])
                out.append(_yaml(body))
                i = end
            else:
                key, val = s.split(':', 1)
                i += 1
                if val.strip():
                    out[key] = val.strip()
                elif i < len(lines) and lines[i][0] > indent:
                    out[key], i = read(i, lines[i][0])
                else:
                    out[key] = [] if key == 'services' else {}
        return out, i
    return read(0, lines[0][0])[0] if lines else {}


def nested_structure(text, fields):
    if text.startswith('{'):
        d = json.loads(text, parse_int=str)
        layers = [d['base'], *d.get('overrides', [])]
    elif text.startswith('#'):
        layers = [_yaml(part) for part in text.split('\n', 1)[1].split('---\n')]
    else:
        def convert(el):
            if el.tag == 'services':
                return [dict(c.attrib) for c in el]
            return {c.tag: convert(c) for c in el} if len(el) else (el.text or '').strip()
        layers = [convert(el) for el in ET.fromstring(text)]
    def fold(a, b):
        for k, v in b.items():
            if 'deep-merged' in text and isinstance(v, dict) and isinstance(a.get(k), dict):
                fold(a[k], v)
            else:
                a[k] = v
    tree = {}
    for layer in layers:
        fold(tree, layer)
    answer = {}
    for f in fields:
        q = f['instruction']
        if 'at the path' in q:
            v = _lookup(tree, re.search(r'`([^`]+)`', q)[1])
            hits = [] if v == {} else [_value(v)]
        elif 'at any depth' in q:
            key, path = re.findall(r'`([^`]+)`', q)
            hits = []
            def visit(node):
                if isinstance(node, dict):
                    for k, v in node.items():
                        if k == key and not isinstance(v, (dict, list)):
                            hits.append(_value(v))
                        visit(v)
            visit(_lookup(tree, path))
        else:
            key = re.search(r'`([^`]+)`', q)[1]
            preds = re.findall(r'`(\w+)` is (at least \d+|"[^"]+"|true|false)', q)
            assert preds, q
            def holds(item):
                return all(k in item and (int(item[k]) >= int(v[9:]) if v.startswith('at least ')
                           else _value(item[k]) == v.strip('"')) for k, v in preds)
            hits = [_value(i[key]) for i in tree['services'] if holds(i) and key in i]
        answer[f['name']] = _pack(f, hits)
    return answer


# Label synonyms are document vocabulary, not a copy of the latent fact schema.
BUSINESS_LABELS = '''invoice number|Invoice number|Invoice No.
total due|Total due|Amount payable|Balance due
payment due date|Due date|Payment due
vendor|Vendor|Supplier|Issued by
customer|Customer|Bill to
billing address|Billing address|Invoice address
payment terms|Payment terms|Terms
hourly consulting rate|Consulting rate|Hourly rate
purchase order number|PO number|Purchase order no.
requester|Requested by|Requester
required delivery date|Required delivery date|Deliver by
delivery address|Ship to|Delivery address
supplier|Supplier|Vendor
unit price|Unit price
client|Client|Customer party
service provider|Service provider|Provider
commencement date|Commencement date|Start of services
termination notice period|Termination notice|Notice period
monthly fee|Monthly fee|Monthly charge
late payment fee|Late payment fee
policy number|Policy number|Policy no.
policyholder|Policyholder|Insured
insurer|Insurer|Underwriter
monthly premium|Monthly premium|Premium per month
deductible per claim|Deductible|Excess per claim
notice to cancel|Cancellation notice'''
DATE = r'\d{1,2} [A-Z][a-z]+ \d{4}'


def _date(s):
    return datetime.strptime(s, '%d %B %Y').date()


def business_document(text, fields):
    start = datetime.min.date()  # printed values hold from the start of the term; every query date is within it
    facts = []
    loc, label = 'body', None
    for line in text.splitlines()[3:]:
        if re.fullmatch(r'Schedule [A-H]', line):
            loc = line[-1]
        elif m := re.fullmatch(r'\w+ No\. (\d+) \(effective (' + DATE + r')(?: until (' + DATE + r'))?\): the (.+?)(?: in Schedule ([A-H]))? is (.+)\.', line):
            rank, a, b, noun, where, value = m.groups()
            facts.append((where or 'body', noun, int(rank), _date(a), _date(b) if b else datetime.max.date(), value))
        elif m := re.fullmatch(r'  - (' + DATE + ') to (' + DATE + '): (.+)', line):
            facts.append((loc, label, 0, _date(m[1]), _date(m[2]), m[3]))
        elif ': ' in line or line.endswith(':'):
            label, value = line.split(':', 1)
            if value.strip():
                facts.append((loc, label, 0, start, datetime.max.date(), value.strip()))
    answer = {}
    for f in fields:
        noun, day = re.match(r'(?:The|What is the) (.+?) (?:in force on|as of|that applies on|on) (' + DATE + r')[.?]',
                             f['instruction']).groups()
        aliases = next(row.split('|')[1:] for row in BUSINESS_LABELS.splitlines() if row.split('|')[0] == noun)
        def resolve(where, seen=()):
            assert where not in seen
            live = [x for x in facts if x[0] == where and x[1] in [noun, *aliases] and x[3] <= _date(day) <= x[4]]
            if not live:
                return None
            value = max(live, key=lambda x: x[2])[5]
            ref = re.fullmatch(r'(?:see Schedule ([A-H])\.|as set out in Schedule ([A-H]))', value)
            return resolve(next(g for g in ref.groups() if g), (*seen, where)) if ref else value
        answer[f['name']] = resolve('body')
    return answer


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def text(self):
        return ''.join(c.text() if isinstance(c, Node) else c for c in self.children).strip()


class DOM(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in {'input', 'meta', 'link', 'br', 'img', 'hr'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        assert self.stack[-1].tag == tag
        self.stack.pop()

    def handle_data(self, text):
        self.stack[-1].children.append(text)


def _walk(node):
    yield node
    for c in node.children:
        if isinstance(c, Node):
            yield from _walk(c)


def html(text, fields):
    root = next(n for n in _walk(DOM(text).root) if n.attrs.get('id') == 'main-item')
    def prune(n):
        n.children = [c for c in n.children if not isinstance(c, Node) or
                      ('item' not in c.attrs.get('class', '').split() and 'hidden' not in c.attrs and
                       'display:none' not in c.attrs.get('style', '').replace(' ', '') and
                       c.tag not in {'template', 's', 'del'})]
        for c in n.children:
            if isinstance(c, Node):
                prune(c)
    prune(root)
    nodes = list(_walk(root))
    pairs, specs = {}, {}
    for parent in nodes:
        kids = [c for c in parent.children if isinstance(c, Node)]
        for i, n in enumerate(kids):
            if n.tag == 'label':
                target = next((x for x in nodes if x.attrs.get('id') == n.attrs.get('for')), None)
                if target:
                    pairs[n.text()] = target.attrs['value']
            elif n.tag in {'dt', 'th', 'span'} and i + 1 < len(kids):
                nxt = kids[i + 1]
                if nxt.tag == {'dt': 'dd', 'th': 'td', 'span': 'span'}[n.tag]:
                    pairs[n.text().rstrip(':')] = nxt.text()
        if parent.tag != 'table' or parent.attrs.get('class') != 'specs':
            continue
        # Expand spans into a rectangular grid, then associate data cells with row/column headers.
        grid = {}
        for r, tr in enumerate(kids):
            col = 0
            for cell in [c for c in tr.children if isinstance(c, Node)]:
                while (r, col) in grid:
                    col += 1
                for rr in range(r, r + int(cell.attrs.get('rowspan', 1))):
                    for cc in range(col, col + int(cell.attrs.get('colspan', 1))):
                        grid[rr, cc] = cell
                col += int(cell.attrs.get('colspan', 1))
        for (r, col), cell in grid.items():
            if cell.tag != 'td':
                continue
            headers = {n.text() for (rr, _), n in grid.items() if rr == r and n.tag == 'th'}
            for rr in range(r - 1, -1, -1):
                row = [n for (rownum, _), n in grid.items() if rownum == rr]
                if all(n.tag == 'th' for n in row) and (rr, col) in grid:
                    headers.add(grid[rr, col].text())
                    break
            for a in headers:
                for b in headers:
                    specs[a, b] = cell.text() or None
    answer = {}
    for f in fields:
        q = f['instruction']
        if 'spec-table' in q:
            value = specs.get(tuple(re.findall(r'"([^"]+)"', q)))
        elif 'value labelled' in q:
            value = pairs.get(re.search(r'"([^"]+)"', q)[1])
        elif 'current ' in q:
            hits = [n.text().split(':', 1)[1].strip() for n in nodes if n.attrs.get('class') == 'price']
            value = next(iter(hits), None)
        else:
            if 'mailto' in q:
                hits = [n.attrs['href'][7:] for n in nodes if n.attrs.get('href', '').startswith('mailto:')]
            elif 'tickets link' in q:
                hits = [n.attrs['href'] for n in nodes if n.attrs.get('class') == 'tickets']
            elif 'data-sku' in q:
                hits = [n.attrs['data-sku'] for n in nodes if 'data-sku' in n.attrs]
            else:
                cls = re.search(r'of the (\w+) <time>', q)[1]
                hits = [n.attrs['datetime'] for n in nodes if n.tag == 'time' and n.attrs.get('class') == cls]
            value = next(iter(hits), None)
        answer[f['name']] = value
    return answer


# Sentence recognizers specify semantic argument positions, independently of name pools.
CONTEXT = [
    ('person', r'(.+?) signed the agreement on Monday\.'),
    ('person', r'According to (.+?), the delay was minor\.'),
    ('person', r'(.+?) was promoted to team lead\.'),
    ('person', r'I asked (.+?) to review the draft\.'),
    ('person', r'(.+?) said she would call back\.'),
    ('place', r'The team flew to (.+?) on Tuesday\.'),
    ('place', r'Rents in (.+?) rose sharply this year\.'),
    ('place', r'The office in downtown (.+?) is closing\.'),
    ('place', r'Heavy snow closed the roads around (.+?)\.'),
    ('organization', r'Shares of (.+?) fell three percent\.'),
    ('organization', r'The board of (.+?) approved the merger\.'),
    ('organization', r'(.+?) announced its quarterly earnings\.'),
    ('organization', r'Regulators fined (.+?) for late filings\.'),
    ('product', r'The latest (.+?) release fixed the battery drain\.'),
    ('product', r'A firmware update for the (.+?) is available\.'),
    ('product', r'Reviewers praised the (.+?) for its price\.'),
    ('product', r'We returned two faulty (.+?) units\.'),
    ('person place', r'(.+?) moved to (.+?) last spring\.'),
    ('person organization', r'(.+?) joined (.+?) as an analyst\.'),
    ('organization place', r'(.+?) opened a plant near (.+?)\.'),
    ('person product', r'(.+?) reviewed the (.+?) for our blog\.'),
    ('organization product', r'(.+?) recalled the (.+?) after complaints\.'),
    ('place organization', r'Back in (.+?), (.+?) is the largest employer\.'),
]
# Every relation is normalized to (supplier/client/partner, other company, reference).
RELATIONS = [
    ('supplier', r'(.+?) ships components to (.+?)\.', False),
    ('supplier', r'(.+?) buys its packaging from (.+?)\.', True),
    ('supplier', r'(.+?) has supplied (.+?) since 2019\.', False),
    ('supplier', r"(.+?)'s main supplier of steel is (.+?)\.", True),
    ('supplier', r"Most parts in (.+?)'s new line come from (.+?)\.", True),
    ('supplier', r"Without deliveries from (.+?), (.+?)'s plant would stop\.", False),
    ('client', r'(.+?) sells its sensors to (.+?)\.', True),
    ('client', r'(.+?) is a long-standing customer of (.+?)\.', False),
    ('client', r'(.+?) placed a new order with (.+?)\.', False),
    ('client', r'(.+?) relies on (.+?) for its sensors\.', False),
    ('client', r"Orders from (.+?) make up a third of (.+?)'s revenue\.", False),
    ('client', r'(.+?) renewed its yearly purchase contract with (.+?)\.', False),
    ('partner', r'(.+?) and (.+?) co-develop a new platform\.', True),
    ('partner', r'(.+?) partners with (.+?) on battery research\.', False),
    ('partner', r"(.+?) is (.+?)'s co-developer on the new platform\.", False),
    ('partner', r'Engineers from (.+?) and (.+?) jointly develop the new sensor line\.', False),
]


def typed_mention(text, fields):
    if 'whole token' in fields[0]['instruction']:
        answer = {}
        for f in fields:
            q = f['instruction']
            if 'two capital letters' in q:
                pattern = r'[A-Z]{2}-[0-9]{4}'
            elif 'ORD followed' in q:
                pattern = r'ORD[0-9]{6}'
            elif 'INV, a dash' in q:
                pattern = r'INV-[0-9]{4}-[0-9]{3}'
            elif 'lowercase v' in q:
                pattern = r'v[0-9]+\.[0-9]+\.[0-9]+'
            else:
                assert 'real month and day' in q
                pattern = r'[0-9]{4}-[0-9]{2}-[0-9]{2}'
            # Isolate the entire code, including dots inside versions, from its carrier.
            tokens = re.findall(r'(?:Please check |Reference |See |The customer quoted |Escalate )([^ ]+)|(?:^|(?<=\. ))([^ ]+) was updated', text)
            # The carriers with trailing punctuation never attach punctuation to their code.
            hits = []
            for token in (a or b for a, b in tokens):
                if re.fullmatch(pattern, token):
                    if 'real month and day' in q:
                        try:
                            datetime.strptime(token, '%Y-%m-%d')
                        except ValueError:
                            continue
                    hits.append(token)
            answer[f['name']] = _pack(f, hits)
        return answer
    sentences = re.split(r'(?<=\.) ', text)
    if 'Every mention of a company' not in fields[0]['instruction']:
        mentions = []
        for sentence in sentences:
            found = [(types.split(), re.fullmatch(pattern, sentence)) for types, pattern in CONTEXT]
            found = [(types, m) for types, m in found if m]
            assert len(found) == 1, sentence
            types, m = found[0]
            mentions.extend(zip(types, m.groups()))
        return {f['name']: _pack(f, [v for t, v in mentions if t == f['name']]) for f in fields}
    # Discover full company names from the rendered prose and resolve first-word references.
    names = set(re.findall(r'\b[A-Z][a-z]+ (?:Labs|Freight|Analytics|Bank|Energy|Robotics|Media|Foods|Health|Air|Textiles|Software|Insurance)\b|Cedar & Moss', text))
    for f in fields:
        names.add(re.search(r'(?:goods to|buys from|jointly with) (.+), as written', f['instruction'])[1])
    def canonical(name):
        matches = [n for n in names if n == name or n.split()[0] == name]
        assert len(matches) == 1, (name, names)
        return matches[0]
    relations = []
    for s in sentences:
        for role, pattern, reverse in RELATIONS:
            m = re.fullmatch(pattern, s)
            if m:
                x, u = m.groups()[::-1] if reverse else m.groups()
                relations.append((role, canonical(x), canonical(u)))
    answer = {}
    for f in fields:
        reference = re.search(r'(?:goods to|buys from|jointly with) (.+), as written', f['instruction'])[1]
        role = f['name'][:-1]
        members = {x for r, x, u in relations if r == role and u == reference}
        if role == 'partner':
            members |= {u for r, x, u in relations if r == role and x == reference}
        # All mentions count, including former/unrelated relations involving a current member.
        pattern = '|'.join(re.escape(n) for n in sorted(names | {n.split()[0] for n in names}, key=len, reverse=True))
        hits = [m[0] for m in re.finditer(r'\b(?:' + pattern + r')\b', text) if canonical(m[0]) in members]
        answer[f['name']] = _pack(f, hits)
    return answer


def lookalike_field(text, fields):
    """Reads (label, value) pairs off any layout; only the role lexicon comes from the generator."""
    from reasoning_core.tasks.jev.lookalike_field_extraction import ROLES
    role_of = {}
    for roles in ROLES.values():
        for role, (nouns, labels) in roles.items():
            for word in nouns + labels:
                for key in {word.lower(), word.lower().replace('.', '').replace(' ', '_')}:
                    assert role_of.setdefault(key, role) == role, word
    lines = text.split('\n')
    pairs = []
    if '| Field | Value |' in text:
        pairs = [tuple(c.strip() for c in line.strip('|').split('|')) for line in lines
                 if line.startswith('| ') and '---' not in line][1:]
    elif any(line.startswith('|') for line in lines):
        rows = [[c.strip() for c in line.strip('|').split('|')] for line in lines if line.startswith('|')]
        pairs = list(zip(rows[0], rows[2]))
    elif ' INFO ' in text:
        pairs = [re.fullmatch(r'\S+ INFO \S+ set "(.+)" to (.+)', line).groups() for line in lines if ' INFO ' in line]
    elif text.startswith('Subject:') or ': ' not in text:
        for sentence in re.split(r'(?<=\.) |\n', text):
            if m := re.fullmatch(r'The (.+?) is (.+)\.', sentence):
                pairs.append(m.groups())
            elif m := re.fullmatch(r'It lists (.+) as the (.+)\.', sentence) or re.fullmatch(r'(.+) is the (.+)\.', sentence):
                pairs.append(m.groups()[::-1])
    else:
        pairs = [tuple(x.strip() for x in line.split(': ', 1)) for line in lines if ': ' in line]
    answer = {}
    for f in fields:
        values = [v for label, v in pairs if role_of.get(label.lower()) == f['name']]
        assert len(values) <= 1, (f, values)
        answer[f['name']] = _pack(f, [v for v in values if v not in {'pending', 'not yet assigned', 'to be confirmed',
                                                                      'unknown', 'N/A', 'TBD', '-'}])
    return answer


SOLVERS = {'typed_mention': typed_mention, 'business_document': business_document,
           'nested_structure': nested_structure, 'html': html, 'lookalike_field': lookalike_field}

# Handwritten semantic assertions; confusers do not match these positive statements.
RECORD_ASSERTIONS = {
    'city': [r'(.+?) lives in (.+)', r'(.+?) is based in (.+)', r'These days (.+?) lives in (.+)'],
    'employer': [r'(.+?) works for (.+)', r'(.+?) is employed by (.+)', r'(.+?) joined (.+) two years ago and is still there'],
    'job_title': [r'(.+?) works as an? (.+)', r'(.+?) is an? (.+) by profession'],
    'phone': [r"(.+?)'s phone number is (.+)", r'(.+?) can be reached at (.+)'],
    'email': [r"(.+?)'s email address is (.+)", r'(.+?) reads mail at (.+)'],
    'birth_date': [r'(.+?) was born on (.+)', r"(.+?)'s date of birth is (.+)"],
}
RECORD_SAME = {
    'city': r'(.+?) lives in the same city as (.+)',
    'employer': r'(.+?) works at the same company as (.+)',
    'job_title': r'(.+?) has the same job as (.+)',
    'phone': r'(.+?) shares a phone line with (.+)',
    'birth_date': r'(.+?) was born on the same day as (.+), a twin',
}


def record_field(text, fields):
    target = re.search(r'(?:where |company |title of |number of |address of |birth of )(.+?)(?: currently|\.$)', fields[0]['instruction'])[1]
    # Only positive assertion subjects and same-as arguments establish people; this avoids
    # mistaking a relative, a city, or an email local-part for a person.
    statements, names = [], {target}
    names.update(re.findall(r"\b([A-Z][a-z]+ [A-Z][a-z]+)(?='s | (?:lives|is|works|was|has|joined|left|turned|never|trained|hopes|does|lived|spent|stopped|closed|got|moved|can|reads|shares)\b)", text))
    for sentence in re.split(r'\. (?=[A-Z])', text.rstrip('.')):
        sentence = sentence.removeprefix('These days ')
        for key, patterns in RECORD_ASSERTIONS.items():
            for pattern in patterns:
                m = re.fullmatch(pattern, sentence)
                if m and "'s " not in m[1] and 'same day as' not in sentence and 'same city as' not in sentence:
                    statements.append((key, m[1], m[2], False))
                    if len(m[1].split()) == 2:
                        names.add(m[1])
        for key, pattern in RECORD_SAME.items():
            if m := re.fullmatch(pattern, sentence):
                statements.append((key, m[1], m[2], True))
                names.update(n for n in m.groups() if len(n.split()) == 2)
    def person(s):
        found = [n for n in names if s == n or s in n.split()]
        assert len(found) == 1, (s, names, text)
        return found[0]
    values, links = {}, {}
    for key, who, value, same in statements:
        (links if same else values)[person(who), key] = person(value) if same else value
    def resolve(who, key, seen=()):
        assert who not in seen
        return resolve(links[who, key], key, (*seen, who)) if (who, key) in links else values.get((who, key))
    return {f['name']: resolve(target, f['name']) for f in fields}


SOLVERS['record_field'] = record_field


def _generation_timeout(*_):
    raise TimeoutError("generation exceeded two seconds (possible exhausted value pool)")


def _check_case(name, level, seed):
    task = _task(name)
    task.config.set_level(level)
    # Call the public generator directly: token accounting and behavior hashing are
    # irrelevant here. A deadline also makes a generator's unbounded retry testable.
    previous = signal.signal(signal.SIGALRM, _generation_timeout)
    signal.setitimer(signal.ITIMER_REAL, 2)
    try:
        entry = task.generate_entry(state_seed=seed)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
    assert entry is not None, (name, level, seed)
    text, fields = entry.metadata.payload, entry.answer.fields
    predicted = SOLVERS[name](text, fields)
    gold = json.loads(entry.answer)
    if name == 'typed_mention' and fields[0]['name'] in {'person', 'place', 'organization', 'product'}:
        # Values alone cannot distinguish two occurrences of the same ambiguous name.
        # Verify each marked occurrence's semantic argument position as well.
        expected = {f['name']: set() for f in fields}
        offset = 0
        for sentence in re.split(r'(?<=\.) ', text):
            for types, pattern in CONTEXT:
                if m := re.fullmatch(pattern, sentence):
                    for group, kind in enumerate(types.split(), 1):
                        if kind in expected:
                            a, b = m.span(group)
                            expected[kind].add((offset + a, offset + b))
            offset += len(sentence) + 1
        for key, spans in expected.items():
            assert {tuple(s) for s in entry.answer.spans[key]} == spans, (name, level, seed, key, text)
    for f in fields:
        key = f['name']
        assert score_extraction(json.dumps({key: predicted[key]}), json.dumps({key: gold[key]})) == 1, (
            name, level, seed, key, gold[key], predicted[key], text)
    assert score_extraction(json.dumps(predicted), entry.answer) == 1


@pytest.mark.parametrize('name', tuple(SOLVERS))
@pytest.mark.parametrize('level', range(5))
def test_rendered_extraction_oracle(name, level):
    for seed in range(40):
        _check_case(name, level, seed)
