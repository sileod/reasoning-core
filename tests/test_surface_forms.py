import datetime
import doctest
from fractions import Fraction

import pytest

import reasoning_core.surface_forms as sf


def test_doctests():
    assert doctest.testmod(sf).failed == 0


@pytest.mark.parametrize("style,text", [("en", "1,234,567.5"), ("eu", "1.234.567,5"), ("si", "1 234 567,5"),
                                        ("swiss", "1'234'567.5"), ("indian", "12,34,567.5"), ("plain", "1234567.5")])
def test_number_styles(style, text):
    assert sf.format_number(Fraction("1234567.5"), style) == text


def test_numbers_are_exact_or_none():
    assert sf.format_number(Fraction(1, 3), "en") is None
    assert sf.format_number(Fraction(1, 3), "en", round_to=2) == "0.33"
    assert sf.format_number(1500, "compact") == "1.5k" and sf.format_number(1234, "compact") is None
    assert sf.format_number(1250, "words") == "one thousand two hundred fifty"
    assert sf.format_number(Fraction("0.1"), "scientific") == "1 × 10^-1"
    assert sf.format_number(12500, "scientific") == "1.25 × 10^4"


def test_quantities_round_trip_through_base_units():
    for dimension, units in sf.UNITS.items():
        for u in units:
            base = sf.to_base(Fraction(37, 2), u.symbol, dimension)
            assert sf.to_unit(base, u.symbol, dimension) == Fraction(37, 2)
    assert sf.render_quantity(sf.to_base(100, "°C", "temperature"), "°F", "temperature") == "212 °F"
    assert sf.render_quantity(sf.to_base(2, "lb", "mass"), "kg", "mass", max_decimals=8) == "0.90718474 kg"
    assert sf.render_quantity(Fraction(129900), "$", "money") == "$1,299"
    assert sf.render_quantity(Fraction(1), "kg", "mass", long=True) == "1 kilogram"
    assert set(sf.exact_units(Fraction("0.3048"), "length")) == {"mm", "cm", "in", "ft"}
    assert sf.mixed(sf.to_base(63, "in", "length"), ["ft", "in"], "length") == "5 ft 3 in"
    assert sf.mixed(8100, ["h", "min"], "time") == "2 h 15 min"


def test_dates_and_times():
    day = datetime.date(2024, 3, 5)
    assert sf.render_date(day, "mdy_numeric") == "03/05/2024" and sf.render_date(day, "ordinal") == "the 5th of March 2024"
    assert sf.render_date(day, "day_month", weekday=True) == "Tuesday 5 March"
    assert sf.date_convention("day_month", 2024) == "dates without a year are in 2024"
    assert all(sf.date_convention(f) == "" for f in sf.UNAMBIGUOUS_DATES)
    assert [sf.relative_days(d) for d in (1, 7, 14, 9)] == ["one day", "a week", "two weeks", "nine days"]
    assert [sf.render_time(m, "12h") for m in (0, 720, 845, 61)] == ["midnight", "noon", "2:05 pm", "1:01 am"]
