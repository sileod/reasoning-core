"""Surface forms of typed values: one latent value, many renderings that a reader can map back to it.

Generators keep values latent (a ``Fraction`` in a base unit, a ``datetime.date``, minutes after midnight) and
render them here; solvers never read the text. Every renderer is exact or says it is not: number and quantity
renderers return ``None`` when a value cannot be written exactly in the asked precision, and ``rounding_error``
bounds the error of a rounded rendering, so a generator can keep comparisons away from boundaries. Styles that a
reader cannot resolve alone (``1.234`` in English and European notation, ``03/04`` day-first or month-first) carry
a ``convention`` sentence that the document must state.

    >>> format_number(Fraction(12345, 10), "eu")
    '1.234,5'
    >>> render_quantity(Fraction("1.5"), "g", "mass")
    '1,500 g'
    >>> render_quantity(Fraction("1.5"), "kg", "mass")
    '1.5 kg'
    >>> render_date(datetime.date(2024, 3, 5), "dmy_numeric")
    '05/03/2024'
"""
import datetime
from dataclasses import dataclass
from fractions import Fraction

# ---- numbers ------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class NumberStyle:
    group: str        # thousands separator ("" for none)
    decimal: str      # decimal separator
    convention: str   # what a document states so the style is unambiguous ("" when it needs no statement)
    indian: bool = False


NUMBER_STYLES = {
    "en": NumberStyle(",", ".", "numbers use ',' between thousands and '.' before decimals"),
    "plain": NumberStyle("", ".", ""),
    "eu": NumberStyle(".", ",", "numbers use '.' between thousands and ',' before decimals"),
    "si": NumberStyle(" ", ",", "numbers use a space between thousands and ',' before decimals"),
    "si_point": NumberStyle(" ", ".", ""),
    "swiss": NumberStyle("'", ".", "numbers use an apostrophe between thousands and '.' before decimals"),
    "indian": NumberStyle(",", ".", "numbers use Indian digit grouping (1,00,000 is one lakh)", indian=True),
}
SMALL = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
         "seventeen eighteen nineteen").split()
TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()


def decimals_needed(x, max_decimals):
    """The fewest decimals (at most ``max_decimals``) that write ``x`` exactly, or None."""
    x = Fraction(x)
    for d in range(max_decimals + 1):
        if (x * 10 ** d).denominator == 1:
            return d
    return None


def _group(digits, style):
    if not style.group or len(digits) <= 3:
        return digits
    if style.indian:
        head, tail = digits[:-3], digits[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        return style.group.join(([head] if head else []) + parts + [tail])
    parts = []
    while digits:
        parts.insert(0, digits[-3:])
        digits = digits[:-3]
    return style.group.join(parts)


def words(n):
    """A whole number below a billion in English words: 1250 -> 'one thousand two hundred fifty'."""
    if not 0 <= n < 10 ** 9 or n != int(n):
        raise ValueError(n)
    n = int(n)
    if n < 20:
        return SMALL[n]
    if n < 100:
        return TENS[n // 10 - 2] + ("-" + SMALL[n % 10] if n % 10 else "")
    for size, name in ((10 ** 6, "million"), (1000, "thousand"), (100, "hundred")):
        if n >= size:
            head, rest = divmod(n, size)
            return f"{words(head)} {name}" + (f" {words(rest)}" if rest else "")


def format_number(x, style="en", max_decimals=2, round_to=None):
    """``x`` in ``style``: a NUMBER_STYLES key, 'compact' (1.5k, 2M), 'words' or 'scientific' (1.25 × 10^4).

    Exact or None, unless ``round_to`` decimals are asked: then rounded half-up, see ``rounding_error``."""
    x = Fraction(x)
    if style == "words":
        return words(x) if x.denominator == 1 and 0 <= x < 10 ** 9 else None
    if style == "compact":
        for size, suffix in ((10 ** 9, "B"), (10 ** 6, "M"), (10 ** 3, "k")):
            if abs(x) >= size:
                text = format_number(x / size, "plain", 1)
                return text and text + suffix
        return format_number(x, "plain", max_decimals)
    if style == "scientific":
        if x == 0:
            return "0"
        exponent, mantissa = 0, x
        while abs(mantissa) >= 10:
            mantissa, exponent = mantissa / 10, exponent + 1
        while abs(mantissa) < 1:
            mantissa, exponent = mantissa * 10, exponent - 1
        mantissa = format_number(mantissa, "plain", max_decimals + 2)
        return mantissa and f"{mantissa} × 10^{exponent}"
    s = NUMBER_STYLES[style]
    if round_to is None:
        d = decimals_needed(x, max_decimals)
        if d is None:
            return None
    else:
        d = round_to
        scaled = x * 10 ** d
        x = Fraction(int(scaled + Fraction(1, 2)) if scaled >= 0 else -int(-scaled + Fraction(1, 2)), 10 ** d)
    sign, x = ("-" if x < 0 else ""), abs(x)
    whole, frac = divmod(x * 10 ** d, 10 ** d)
    text = sign + _group(str(int(whole)), s)
    return text + (s.decimal + str(int(frac)).zfill(d) if d else "")


def rounding_error(decimals, factor=1):
    """The largest error, in base units, of a value rounded to ``decimals`` in a unit of size ``factor``."""
    return Fraction(factor) / 2 / 10 ** decimals


# ---- units --------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Unit:
    symbol: str
    singular: str
    plural: str
    factor: Fraction            # base units per unit
    offset: Fraction = Fraction(0)   # base = value * factor + offset (temperatures)
    prefix: bool = False        # symbol written before the number ($5)
    system: str = "metric"


def _u(symbol, singular, factor, plural=None, **kw):
    return Unit(symbol, singular, plural or singular + "s", Fraction(factor), **kw)


# Base units: m, kg, s, m/s, K, J, W, Pa, byte, m², m³, US dollar cents. Imperial factors are exact by definition.
UNITS = {
    "length": [_u("mm", "millimeter", "0.001"), _u("cm", "centimeter", "0.01"), _u("m", "meter", 1),
               _u("km", "kilometer", 1000), _u("in", "inch", "0.0254", "inches", system="imperial"),
               _u("ft", "foot", "0.3048", "feet", system="imperial"), _u("yd", "yard", "0.9144", system="imperial"),
               _u("mi", "mile", "1609.344", system="imperial")],
    "mass": [_u("mg", "milligram", "0.000001"), _u("g", "gram", "0.001"), _u("kg", "kilogram", 1),
             _u("t", "tonne", 1000), _u("oz", "ounce", "0.028349523125", system="imperial"),
             _u("lb", "pound", "0.45359237", system="imperial")],
    "volume": [_u("mL", "milliliter", "0.000001"), _u("L", "liter", "0.001"), _u("m³", "cubic meter", 1, "cubic meters"),
               _u("fl oz", "fluid ounce", "0.0000295735295625", system="imperial"),
               _u("gal", "gallon", "0.003785411784", system="imperial")],
    "area": [_u("m²", "square meter", 1, "square meters"), _u("ha", "hectare", 10000),
             _u("km²", "square kilometer", 1000000, "square kilometers"),
             _u("acre", "acre", "4046.8564224", system="imperial")],
    "time": [_u("s", "second", 1), _u("min", "minute", 60), _u("h", "hour", 3600), _u("d", "day", 86400),
             _u("wk", "week", 604800)],
    "speed": [_u("m/s", "meter per second", 1, "meters per second"),
              _u("km/h", "kilometer per hour", Fraction(1000, 3600), "kilometers per hour"),
              _u("mph", "mile per hour", Fraction(1609344, 3600000), "miles per hour", system="imperial"),
              _u("kn", "knot", Fraction(1852, 3600))],
    "temperature": [_u("K", "kelvin", 1, "kelvins"), _u("°C", "degree Celsius", 1, "degrees Celsius",
                                                        offset=Fraction("273.15")),
                    _u("°F", "degree Fahrenheit", Fraction(5, 9), "degrees Fahrenheit",
                       offset=Fraction("273.15") - Fraction(32 * 5, 9), system="imperial")],
    "energy": [_u("J", "joule", 1), _u("kJ", "kilojoule", 1000), _u("Wh", "watt-hour", 3600),
               _u("kWh", "kilowatt-hour", 3600000), _u("cal", "calorie", "4.184"), _u("kcal", "kilocalorie", 4184)],
    "power": [_u("W", "watt", 1), _u("kW", "kilowatt", 1000), _u("MW", "megawatt", 1000000)],
    "pressure": [_u("Pa", "pascal", 1), _u("kPa", "kilopascal", 1000), _u("bar", "bar", 100000, "bar"),
                 _u("atm", "atmosphere", 101325), _u("psi", "psi", "6894.757293168361", "psi", system="imperial")],
    "data": [_u("B", "byte", 1), _u("kB", "kilobyte", 1000), _u("MB", "megabyte", 10 ** 6),
             _u("GB", "gigabyte", 10 ** 9), _u("TB", "terabyte", 10 ** 12), _u("KiB", "kibibyte", 1024),
             _u("MiB", "mebibyte", 1024 ** 2), _u("GiB", "gibibyte", 1024 ** 3), _u("TiB", "tebibyte", 1024 ** 4)],
    "money": [_u("$", "dollar", 100, prefix=True), _u("¢", "cent", 1)],
}
UNIT = {(dimension, u.symbol): u for dimension, units in UNITS.items() for u in units}


def to_unit(base, unit, dimension):
    """A base-unit value in ``unit`` (exact Fraction)."""
    u = UNIT[dimension, unit]
    return (Fraction(base) - u.offset) / u.factor


def to_base(value, unit, dimension):
    u = UNIT[dimension, unit]
    return Fraction(value) * u.factor + u.offset


def render_quantity(base, unit, dimension, style="en", max_decimals=2, long=False, round_to=None):
    """A base-unit value written in ``unit`` ('1.5 kg', '$1,299', '1.5 kilograms'); None when not exact
    (unless ``round_to``)."""
    u = UNIT[dimension, unit]
    number = format_number(to_unit(base, unit, dimension), style, max_decimals, round_to)
    if number is None:
        return None
    if u.prefix:
        return number[:1] + u.symbol + number[1:] if number.startswith("-") else u.symbol + number
    if long:
        return f"{number} {u.singular if to_unit(base, unit, dimension) == 1 else u.plural}"
    return f"{number} {u.symbol}"


def exact_units(base, dimension, max_decimals=2, system=None):
    """Units of ``dimension`` (optionally of one system) that write ``base`` exactly."""
    return [u.symbol for u in UNITS[dimension] if (system is None or u.system == system)
            and decimals_needed(to_unit(base, u.symbol, dimension), max_decimals) is not None]


def mixed(base, units, dimension, style="en"):
    """A base-unit value as descending whole parts ('5 ft 3 in', '2 h 15 min'); None if the smallest unit leaves
    a remainder. Zero parts are left out."""
    parts, rest = [], Fraction(base)
    for symbol in units:
        u = UNIT[dimension, symbol]
        count, rest = divmod(rest, u.factor)
        if count:
            parts.append(f"{format_number(count, style)} {symbol}")
    return " ".join(parts) if parts and rest == 0 else None


# ---- dates and times ----------------------------------------------------------------------------------------

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# name: (renderer, convention a document states, whether the year is written)
DATE_FORMATS = {
    "iso": (lambda d: d.isoformat(), "", True),
    "dmy_numeric": (lambda d: f"{d.day:02d}/{d.month:02d}/{d.year}", "numeric dates are day/month/year", True),
    "dmy_short": (lambda d: f"{d.day}/{d.month}/{d.year}", "numeric dates are day/month/year", True),
    "mdy_numeric": (lambda d: f"{d.month:02d}/{d.day:02d}/{d.year}", "numeric dates are month/day/year", True),
    "mdy_short": (lambda d: f"{d.month}/{d.day}/{d.year}", "numeric dates are month/day/year", True),
    "dmy_dots": (lambda d: f"{d.day:02d}.{d.month:02d}.{d.year}", "numeric dates are day.month.year", True),
    "day_month_year": (lambda d: f"{d.day} {MONTHS[d.month - 1]} {d.year}", "", True),
    "month_day_year": (lambda d: f"{MONTHS[d.month - 1]} {d.day}, {d.year}", "", True),
    "day_mon_year": (lambda d: f"{d.day} {MONTHS[d.month - 1][:3]} {d.year}", "", True),
    "ordinal": (lambda d: f"the {ordinal(d.day)} of {MONTHS[d.month - 1]} {d.year}", "", True),
    "day_month": (lambda d: f"{d.day} {MONTHS[d.month - 1]}", "dates without a year are in {year}", False),
    "month_day": (lambda d: f"{MONTHS[d.month - 1]} {d.day}", "dates without a year are in {year}", False),
}
UNAMBIGUOUS_DATES = [name for name, (_, convention, year) in DATE_FORMATS.items() if not convention]


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def render_date(day, fmt, weekday=False):
    """``day`` in DATE_FORMATS[fmt], optionally preceded by its weekday ('Tuesday 5 March 2024')."""
    text = DATE_FORMATS[fmt][0](day)
    return f"{WEEKDAYS[day.weekday()]} {text}" if weekday else text


def date_convention(fmt, year=None):
    """The sentence a document states for ``fmt`` ('' when the format needs none)."""
    return DATE_FORMATS[fmt][1].format(year=year)


def relative_days(days):
    """A positive day offset in words: 1 -> 'one day', 7 -> 'a week', 14 -> 'two weeks', 9 -> 'nine days'."""
    if days == 7:
        return "a week"
    if days % 7 == 0 and days <= 28:
        return f"{words(days // 7)} weeks"
    return "one day" if days == 1 else f"{words(days)} days"


def render_time(minutes, fmt="24h"):
    """Minutes after midnight as '14:05' (24h) or '2:05 pm' (12h; 'noon' and 'midnight' spelled out)."""
    h, m = divmod(int(minutes) % 1440, 60)
    if fmt == "24h":
        return f"{h:02d}:{m:02d}"
    if m == 0 and h in (0, 12):
        return "midnight" if h == 0 else "noon"
    return f"{(h - 1) % 12 + 1}:{m:02d} {'am' if h < 12 else 'pm'}"
