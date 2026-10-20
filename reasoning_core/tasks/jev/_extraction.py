"""Shared pieces of the extraction tasks: a text builder that records gold offsets, and small vocabularies."""
import re

from reasoning_core.decision import Extraction
from reasoning_core.template import Entry

FIRST = ["Ana", "Ben", "Chloe", "Daniel", "Elena", "Farid", "Grace", "Hugo", "Ines", "Jonas", "Kemi", "Lucas",
         "Maya", "Nikolai", "Olga", "Pedro", "Rania", "Sami", "Tara", "Viktor", "Wen", "Yusuf", "Zoe", "Amir"]
LAST = ["Ruiz", "Okafor", "Lindqvist", "Moreau", "Tanaka", "Haddad", "Novak", "Fischer", "Costa", "Mensah",
        "Ibrahim", "Kowalski", "Silva", "Larsen", "Petrov", "Nguyen", "Rossi", "Dubois", "Weber", "Sato"]
CITIES = ["Oslo", "Lima", "Accra", "Hanoi", "Quito", "Porto", "Dakar", "Perth", "Tunis", "Osaka",
          "Bergen", "Cusco", "Lagos", "Hue", "Cuenca", "Braga", "Darwin", "Sfax", "Kobe", "Graz"]
COMPANIES = ["Norvik Labs", "Altamar Freight", "Bluefin Analytics", "Cedar & Moss", "Quillon Bank",
             "Halvard Energy", "Pexis Robotics", "Torrent Media", "Sunvale Foods", "Arcadia Health",
             "Kestrel Air", "Lumen Textiles", "Orrin Software", "Bramble Insurance"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


class Doc:
    """Text assembled from templates whose {slots} take plain strings or (string, mark) pairs; the offsets of
    marked strings are kept under their mark, so gold spans are exact by construction."""

    def __init__(self):
        self.parts, self.size, self.marks = [], 0, {}

    def add(self, template="", **slots):
        for piece in re.split(r"(\{\w+\})", template):
            value = slots[piece[1:-1]] if re.fullmatch(r"\{\w+\}", piece) else piece
            text, mark = value if isinstance(value, tuple) else (value, None)
            if mark is not None:
                self.marks.setdefault(mark, []).append((self.size, self.size + len(text)))
            self.parts.append(text)
            self.size += len(text)
        return self

    @property
    def text(self):
        return "".join(self.parts)


def extraction_entry(text, fields, spans, state_seed, **metadata):
    """The Entry of one extraction request: the text as payload, the fields and gold offsets as metadata."""
    answer = Extraction(text, fields, spans)
    return Entry({"payload": text, "state_seed": state_seed, "extraction": answer.to_dict(), **metadata}, answer)


def article(word):
    return "an" if word[0] in "aeiou" else "a"
