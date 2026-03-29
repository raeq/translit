#!/usr/bin/env python3
"""Generate TSV entries for Unicode coverage expansion (Tier 1 + Tier 2).

Outputs tab-separated lines: HEX_CODEPOINT<TAB>ASCII_VALUE
All values are pure ASCII. Empty values mean "map to nothing" (strip character).
"""

import re
import sys
import unicodedata
from pathlib import Path

# ── Existing data ──────────────────────────────────────────────────────────


def load_existing_tsv(path):
    """Load existing TSV entries as {codepoint_int: ascii_value}."""
    existing = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split("\t")
                cp = int(parts[0], 16)
                val = parts[1] if len(parts) > 1 else ""
                existing[cp] = val
    return existing


def load_hanzi_pinyin(path):
    """Load hanzi_pinyin.tsv as {codepoint_int: pinyin}."""
    pinyin = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split("\t")
                if len(parts) >= 2:
                    cp = int(parts[0], 16)
                    pinyin[cp] = parts[1]
    return pinyin


# ── Helpers ────────────────────────────────────────────────────────────────


def is_assigned(cp):
    """Check if a codepoint is assigned (has a Unicode name)."""
    try:
        unicodedata.name(chr(cp))
        return True
    except ValueError:
        return False


def entry(cp, val):
    """Format a TSV entry."""
    assert all(ord(c) < 128 for c in val), f"Non-ASCII in value for U+{cp:04X}: {val!r}"
    return (cp, val)


# ── BATCH 1A: Mechanical mappings ──────────────────────────────────────────


def gen_fullwidth(existing):
    """Fullwidth ASCII variants FF01-FF5E → ASCII by subtracting 0xFEE0."""
    entries = []
    for cp in range(0xFF01, 0xFF5F):
        if cp not in existing and is_assigned(cp):
            ascii_cp = cp - 0xFEE0
            entries.append(entry(cp, chr(ascii_cp)))
    return entries


def gen_halfwidth_hangul(existing):
    """Halfwidth Hangul FFA0-FFDC → romanization matching compat jamo."""
    # Halfwidth jamo map to fullwidth compat jamo equivalents
    # FFA0 = HALFWIDTH HANGUL FILLER (no mapping needed, but assign empty)
    # FFA1-FFBE = consonants, FFBF-FFC1 undefined, FFC2-FFC7 vowels, etc.

    # Map halfwidth to compat jamo (fullwidth) equivalents
    hw_to_compat = {
        0xFFA0: None,  # filler
        0xFFA1: 0x3131,
        0xFFA2: 0x3132,
        0xFFA3: 0x3133,
        0xFFA4: 0x3134,
        0xFFA5: 0x3135,
        0xFFA6: 0x3136,
        0xFFA7: 0x3137,
        0xFFA8: 0x3138,
        0xFFA9: 0x3139,
        0xFFAA: 0x313A,
        0xFFAB: 0x313B,
        0xFFAC: 0x313C,
        0xFFAD: 0x313D,
        0xFFAE: 0x313E,
        0xFFAF: 0x313F,
        0xFFB0: 0x3140,
        0xFFB1: 0x3141,
        0xFFB2: 0x3142,
        0xFFB3: 0x3143,
        0xFFB4: 0x3144,
        0xFFB5: 0x3145,
        0xFFB6: 0x3146,
        0xFFB7: 0x3147,
        0xFFB8: 0x3148,
        0xFFB9: 0x3149,
        0xFFBA: 0x314A,
        0xFFBB: 0x314B,
        0xFFBC: 0x314C,
        0xFFBD: 0x314D,
        0xFFBE: 0x314E,
        # vowels
        0xFFC2: 0x314F,
        0xFFC3: 0x3150,
        0xFFC4: 0x3151,
        0xFFC5: 0x3152,
        0xFFC6: 0x3153,
        0xFFC7: 0x3154,
        0xFFCA: 0x3155,
        0xFFCB: 0x3156,
        0xFFCC: 0x3157,
        0xFFCD: 0x3158,
        0xFFCE: 0x3159,
        0xFFCF: 0x315A,
        0xFFD2: 0x315B,
        0xFFD3: 0x315C,
        0xFFD4: 0x315D,
        0xFFD5: 0x315E,
        0xFFD6: 0x315F,
        0xFFD7: 0x3160,
        0xFFDA: 0x3161,
        0xFFDB: 0x3162,
        0xFFDC: 0x3163,
    }

    # Compat jamo romanizations (from hangul.rs)
    compat_jamo = {
        0x3131: "g",
        0x3132: "kk",
        0x3133: "gs",
        0x3134: "n",
        0x3135: "nj",
        0x3136: "nh",
        0x3137: "d",
        0x3138: "tt",
        0x3139: "r",
        0x313A: "lg",
        0x313B: "lm",
        0x313C: "lb",
        0x313D: "ls",
        0x313E: "lt",
        0x313F: "lp",
        0x3140: "lh",
        0x3141: "m",
        0x3142: "b",
        0x3143: "pp",
        0x3144: "bs",
        0x3145: "s",
        0x3146: "ss",
        0x3147: "",
        0x3148: "j",
        0x3149: "jj",
        0x314A: "ch",
        0x314B: "k",
        0x314C: "t",
        0x314D: "p",
        0x314E: "h",
        0x314F: "a",
        0x3150: "ae",
        0x3151: "ya",
        0x3152: "yae",
        0x3153: "eo",
        0x3154: "e",
        0x3155: "yeo",
        0x3156: "ye",
        0x3157: "o",
        0x3158: "wa",
        0x3159: "wae",
        0x315A: "oe",
        0x315B: "yo",
        0x315C: "u",
        0x315D: "wo",
        0x315E: "we",
        0x315F: "wi",
        0x3160: "yu",
        0x3161: "eu",
        0x3162: "ui",
        0x3163: "i",
    }

    entries = []
    for cp in range(0xFFA0, 0xFFEF):
        if cp not in existing and is_assigned(cp):
            compat = hw_to_compat.get(cp)
            if compat is not None:
                val = compat_jamo.get(compat, "")
                entries.append(entry(cp, val))
            elif cp == 0xFFA0:
                entries.append(entry(cp, ""))  # filler

    # Also handle halfwidth symbols FFEE etc if assigned
    # FFE0-FFEE: halfwidth/fullwidth forms (cent, pound, etc.)
    hw_symbols = {
        0xFFE0: "c",  # FULLWIDTH CENT SIGN
        0xFFE1: "GBP",  # FULLWIDTH POUND SIGN
        0xFFE2: "-",  # FULLWIDTH NOT SIGN
        0xFFE3: "-",  # FULLWIDTH MACRON
        0xFFE4: "|",  # FULLWIDTH BROKEN BAR
        0xFFE5: "JPY",  # FULLWIDTH YEN SIGN
        0xFFE6: "KRW",  # FULLWIDTH WON SIGN
        0xFFE8: "|",  # HALFWIDTH FORMS LIGHT VERTICAL
        0xFFE9: "<-",  # HALFWIDTH LEFTWARDS ARROW
        0xFFEA: "^",  # HALFWIDTH UPWARDS ARROW
        0xFFEB: "->",  # HALFWIDTH RIGHTWARDS ARROW
        0xFFEC: "v",  # HALFWIDTH DOWNWARDS ARROW
        0xFFED: "#",  # HALFWIDTH BLACK SQUARE
        0xFFEE: "o",  # HALFWIDTH WHITE CIRCLE
    }
    for cp, val in hw_symbols.items():
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    return entries


def gen_enclosed_circled(existing):
    """Enclosed Alphanumerics 2460-24FF → extract number/letter."""
    entries = []
    for cp in range(0x2460, 0x2500):
        if cp not in existing and is_assigned(cp):
            unicodedata.name(chr(cp), "")
            val = None

            # Circled digits: ① ② ... ⑳ (2460-2473)
            if 0x2460 <= cp <= 0x2473:
                val = str(cp - 0x2460 + 1)
            # Parenthesized digits: ⑴ ⑵ ... ⒇ (2474-2487)
            elif 0x2474 <= cp <= 0x2487:
                val = f"({cp - 0x2474 + 1})"
            # Period digits: ⒈ ⒉ ... ⒛ (2488-249B)
            elif 0x2488 <= cp <= 0x249B:
                val = f"{cp - 0x2488 + 1}."
            # Circled Latin capital: Ⓐ Ⓑ ... Ⓩ (24B6-24CF)
            elif 0x24B6 <= cp <= 0x24CF:
                val = chr(cp - 0x24B6 + ord("A"))
            # Circled Latin small: ⓐ ⓑ ... ⓩ (24D0-24E9)
            elif 0x24D0 <= cp <= 0x24E9:
                val = chr(cp - 0x24D0 + ord("a"))
            # Double circled digits: ⓵ ⓶ ... ⓾ (24F5-24FE)
            elif 0x24F5 <= cp <= 0x24FE:
                val = str(cp - 0x24F5 + 1)
            # Circled digit zero: ⓪ (24EA)
            elif cp == 0x24EA:
                val = "0"
            # Negative circled digits: ⓫ ⓬ ... ⓴ (24EB-24F4)
            elif 0x24EB <= cp <= 0x24F4:
                val = str(cp - 0x24EB + 11)
            # Circled number 0: ⓿ (24FF)
            elif cp == 0x24FF:
                val = "0"

            if val is not None:
                entries.append(entry(cp, val))
    return entries


def gen_super_subscript(existing):
    """Superscripts and Subscripts 2070-209F."""
    mappings = {
        0x2070: "0",  # ⁰
        0x2071: "i",  # ⁱ
        0x2074: "4",  # ⁴
        0x2075: "5",  # ⁵
        0x2076: "6",  # ⁶
        0x2077: "7",  # ⁷
        0x2078: "8",  # ⁸
        0x2079: "9",  # ⁹
        0x207A: "+",  # ⁺
        0x207B: "-",  # ⁻
        0x207C: "=",  # ⁼
        0x207D: "(",  # ⁽
        0x207E: ")",  # ⁾
        0x207F: "n",  # ⁿ
        0x2080: "0",  # ₀
        0x2081: "1",  # ₁
        0x2082: "2",  # ₂
        0x2083: "3",  # ₃
        0x2084: "4",  # ₄
        0x2085: "5",  # ₅
        0x2086: "6",  # ₆
        0x2087: "7",  # ₇
        0x2088: "8",  # ₈
        0x2089: "9",  # ₉
        0x208A: "+",  # ₊
        0x208B: "-",  # ₋
        0x208C: "=",  # ₌
        0x208D: "(",  # ₍
        0x208E: ")",  # ₎
    }
    entries = []
    for cp, val in sorted(mappings.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))
    return entries


def gen_roman_numerals(existing):
    """Roman Numerals 2160-2188."""
    mappings = {
        # Uppercase Roman Numerals
        0x2160: "I",
        0x2161: "II",
        0x2162: "III",
        0x2163: "IV",
        0x2164: "V",
        0x2165: "VI",
        0x2166: "VII",
        0x2167: "VIII",
        0x2168: "IX",
        0x2169: "X",
        0x216A: "XI",
        0x216B: "XII",
        0x216C: "L",
        0x216D: "C",
        0x216E: "D",
        0x216F: "M",
        # Lowercase Roman Numerals
        0x2170: "i",
        0x2171: "ii",
        0x2172: "iii",
        0x2173: "iv",
        0x2174: "v",
        0x2175: "vi",
        0x2176: "vii",
        0x2177: "viii",
        0x2178: "ix",
        0x2179: "x",
        0x217A: "xi",
        0x217B: "xii",
        0x217C: "l",
        0x217D: "c",
        0x217E: "d",
        0x217F: "m",
        # Small Roman Numerals
        0x2180: "1000",  # ↀ ROMAN NUMERAL ONE THOUSAND C D
        0x2181: "5000",  # ↁ ROMAN NUMERAL FIVE THOUSAND
        0x2182: "10000",  # ↂ ROMAN NUMERAL TEN THOUSAND
        0x2183: "C",  # Ↄ ROMAN NUMERAL REVERSED ONE HUNDRED
        0x2184: "c",  # ↄ LATIN SMALL LETTER REVERSED C
        0x2185: "6",  # ↅ ROMAN NUMERAL SIX LATE FORM
        0x2186: "50",  # ↆ ROMAN NUMERAL FIFTY EARLY FORM
        0x2187: "50000",  # ↇ ROMAN NUMERAL FIFTY THOUSAND
        0x2188: "100000",  # ↈ ROMAN NUMERAL ONE HUNDRED THOUSAND
    }
    entries = []
    for cp, val in sorted(mappings.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))
    return entries


def gen_modifier_letters(existing):
    """Spacing Modifier Letters 02B0-02FF."""
    mappings = {
        0x02B0: "h",
        0x02B1: "h",
        0x02B2: "j",
        0x02B3: "r",
        0x02B4: "r",
        0x02B5: "r",
        0x02B6: "r",
        0x02B7: "w",
        0x02B8: "y",
        0x02B9: "'",
        0x02BA: '"',
        0x02BB: "'",
        0x02BC: "'",
        0x02BD: "'",
        0x02BE: "'",
        0x02BF: "'",
        0x02C0: "'",
        0x02C1: "'",
        0x02C2: "<",
        0x02C3: ">",
        0x02C4: "^",
        0x02C5: "v",
        0x02C6: "^",
        0x02C7: "v",  # caron
        0x02C8: "'",
        0x02C9: "-",
        0x02CA: "'",
        0x02CB: "`",
        0x02CC: ",",
        0x02CD: "_",
        0x02CE: "`",
        0x02CF: "'",
        0x02D0: ":",
        0x02D1: ":",
        0x02D2: ">",
        0x02D3: "<",
        0x02D4: "^",
        0x02D5: "v",
        0x02D6: "+",
        0x02D7: "-",
        0x02D8: "~",
        0x02D9: ".",
        0x02DA: "o",
        0x02DB: ",",
        0x02DC: "~",
        0x02DD: '"',
        0x02DE: "r",
        0x02DF: "x",  # MODIFIER LETTER CROSS ACCENT
        0x02E0: "g",
        0x02E1: "l",
        0x02E2: "s",
        0x02E3: "x",
        0x02E4: "'",
        0x02E5: "|",
        0x02E6: "|",
        0x02E7: "|",
        0x02E8: "|",
        0x02E9: "|",
        0x02EA: "|",
        0x02EB: "|",
        0x02EC: "v",
        0x02ED: "=",
        0x02EE: '"',
        0x02EF: "v",
        0x02F0: "v",
        0x02F1: "v",
        0x02F2: "v",
        0x02F3: "o",
        0x02F4: "'",
        0x02F5: '"',
        0x02F6: '"',
        0x02F7: "~",
        0x02F8: ":",
        0x02F9: "!",
        0x02FA: "|",
        0x02FB: "|",
        0x02FC: "v",
        0x02FD: "=",
        0x02FE: "v",
        0x02FF: "'",
    }
    entries = []
    for cp, val in sorted(mappings.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))
    return entries


# ── BATCH 1B: Reference lookups ───────────────────────────────────────────


def gen_ipa(existing):
    """IPA Extensions 0250-02AF → closest ASCII approximation."""
    mappings = {
        0x0250: "a",  # ɐ TURNED A
        0x0251: "a",  # ɑ ALPHA
        0x0252: "a",  # ɒ TURNED ALPHA
        0x0253: "b",  # ɓ HOOKTOP B
        0x0254: "o",  # ɔ OPEN O
        0x0255: "c",  # ɕ CURL C
        0x0256: "d",  # ɖ TAIL D
        0x0257: "d",  # ɗ HOOKTOP D
        0x0258: "e",  # ɘ REVERSED E
        0x0259: "e",  # ə SCHWA
        0x025A: "e",  # ɚ SCHWA WITH HOOK
        0x025B: "e",  # ɛ OPEN E
        0x025C: "e",  # ɜ REVERSED OPEN E
        0x025D: "e",  # ɝ REVERSED OPEN E WITH HOOK
        0x025E: "e",  # ɞ CLOSED REVERSED OPEN E
        0x025F: "j",  # ɟ BARRED DOTLESS J
        0x0260: "g",  # ɠ HOOKTOP G
        0x0261: "g",  # ɡ SCRIPT G
        0x0262: "G",  # ɢ SMALL CAPITAL G
        0x0263: "g",  # ɣ GAMMA
        0x0264: "o",  # ɤ RAMS HORN / BABY GAMMA
        0x0265: "h",  # ɥ TURNED H
        0x0266: "h",  # ɦ HOOKTOP H
        0x0267: "h",  # ɧ HENG WITH HOOK
        0x0268: "i",  # ɨ BARRED I
        0x0269: "i",  # ɩ IOTA
        0x026A: "I",  # ɪ SMALL CAPITAL I
        0x026B: "l",  # ɫ L WITH MIDDLE TILDE
        0x026C: "l",  # ɬ BELTED L
        0x026D: "l",  # ɭ TAIL L
        0x026E: "lz",  # ɮ LEZH
        0x026F: "m",  # ɯ TURNED M
        0x0270: "m",  # ɰ TURNED M WITH LONG LEG
        0x0271: "m",  # ɱ M WITH HOOK
        0x0272: "n",  # ɲ LEFT HOOK N (palatal nasal)
        0x0273: "n",  # ɳ TAIL N (retroflex nasal)
        0x0274: "N",  # ɴ SMALL CAPITAL N
        0x0275: "o",  # ɵ BARRED O
        0x0276: "OE",  # ɶ SMALL CAPITAL OE
        0x0277: "o",  # ɷ CLOSED OMEGA
        0x0278: "ph",  # ɸ PHI
        0x0279: "r",  # ɹ TURNED R
        0x027A: "r",  # ɺ TURNED R WITH LONG LEG
        0x027B: "r",  # ɻ TURNED R WITH HOOK
        0x027C: "r",  # ɼ LONG LEG R
        0x027D: "r",  # ɽ TAIL R
        0x027E: "r",  # ɾ FISHHOOK R
        0x027F: "r",  # ɿ REVERSED FISHHOOK R
        0x0280: "R",  # ʀ SMALL CAPITAL R
        0x0281: "R",  # ʁ INVERTED SMALL CAPITAL R
        0x0282: "s",  # ʂ TAIL S
        0x0283: "sh",  # ʃ ESH
        0x0284: "j",  # ʄ HOOKTOP BARRED DOTLESS J
        0x0285: "s",  # ʅ SQUAT REVERSED ESH
        0x0286: "sh",  # ʆ ESH WITH CURL
        0x0287: "t",  # ʇ TURNED T
        0x0288: "t",  # ʈ TAIL T
        0x0289: "u",  # ʉ BARRED U
        0x028A: "u",  # ʊ UPSILON
        0x028B: "v",  # ʋ SCRIPT V
        0x028C: "v",  # ʌ TURNED V (caret)
        0x028D: "w",  # ʍ TURNED W
        0x028E: "y",  # ʎ TURNED Y
        0x028F: "Y",  # ʏ SMALL CAPITAL Y
        0x0290: "z",  # ʐ TAIL Z
        0x0291: "z",  # ʑ CURL Z
        0x0292: "zh",  # ʒ EZH
        0x0293: "zh",  # ʓ EZH WITH CURL
        0x0294: "'",  # ʔ GLOTTAL STOP
        0x0295: "'",  # ʕ PHARYNGEAL VOICED FRICATIVE
        0x0296: "'",  # ʖ INVERTED GLOTTAL STOP
        0x0297: "!",  # ʗ STRETCHED C (click)
        0x0298: "!",  # ʘ BILABIAL CLICK
        0x0299: "B",  # ʙ SMALL CAPITAL B
        0x029A: "e",  # ʚ CLOSED OPEN E
        0x029B: "G",  # ʛ HOOKTOP SMALL CAPITAL G
        0x029C: "H",  # ʜ SMALL CAPITAL H
        0x029D: "j",  # ʝ CROSSED-TAIL J
        0x029E: "k",  # ʞ TURNED K
        0x029F: "L",  # ʟ SMALL CAPITAL L
        0x02A0: "q",  # ʠ HOOKTOP Q
        0x02A1: "'",  # ʡ BARRED GLOTTAL STOP
        0x02A2: "'",  # ʢ BARRED REVERSED GLOTTAL STOP
        0x02A3: "dz",  # ʣ DZ DIGRAPH
        0x02A4: "dz",  # ʤ DEZH DIGRAPH
        0x02A5: "dz",  # ʥ DZ DIGRAPH WITH CURL
        0x02A6: "ts",  # ʦ TS DIGRAPH
        0x02A7: "tsh",  # ʧ TESH DIGRAPH
        0x02A8: "tc",  # ʨ TC DIGRAPH WITH CURL
        0x02A9: "fn",  # ʩ FENG DIGRAPH
        0x02AA: "ls",  # ʪ LS DIGRAPH
        0x02AB: "lz",  # ʫ LZ DIGRAPH
        0x02AC: "w",  # ʬ BILABIAL PERCUSSIVE
        0x02AD: "!",  # ʭ BIDENTAL PERCUSSIVE
        0x02AE: "h",  # ʮ TURNED H WITH FISHHOOK
        0x02AF: "h",  # ʯ TURNED H WITH FISHHOOK AND TAIL
    }
    entries = []
    for cp, val in sorted(mappings.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))
    return entries


def gen_greek_extended(existing):
    """Greek Extended 1F00-1FFF → strip breathing/accent → base Greek."""
    # Map base Greek letters to their romanization
    greek_base_map = {
        "ALPHA": ("A", "a"),
        "BETA": ("B", "b"),
        "GAMMA": ("G", "g"),
        "DELTA": ("D", "d"),
        "EPSILON": ("E", "e"),
        "ZETA": ("Z", "z"),
        "ETA": ("I", "i"),
        "THETA": ("Th", "th"),
        "IOTA": ("I", "i"),
        "KAPPA": ("K", "k"),
        "LAMDA": ("L", "l"),
        "MU": ("M", "m"),
        "NU": ("N", "n"),
        "XI": ("X", "x"),
        "OMICRON": ("O", "o"),
        "PI": ("P", "p"),
        "RHO": ("R", "r"),
        "SIGMA": ("S", "s"),
        "TAU": ("T", "t"),
        "UPSILON": ("Y", "y"),
        "PHI": ("F", "f"),
        "CHI": ("Ch", "ch"),
        "PSI": ("Ps", "ps"),
        "OMEGA": ("O", "o"),
    }

    entries = []
    for cp in range(0x1F00, 0x2000):
        if cp not in existing and is_assigned(cp):
            name = unicodedata.name(chr(cp), "")
            if not name:
                continue

            # Determine if capital or small from name
            is_capital = "CAPITAL" in name

            # Find the base Greek letter
            val = None
            for greek_name, (cap_val, small_val) in greek_base_map.items():
                if greek_name in name:
                    val = cap_val if is_capital else small_val
                    break

            # Handle PROSGEGRAMMENI (iota subscript) → append "i"
            if val and "PROSGEGRAMMENI" in name:
                val += "i" if is_capital else "i"
            elif val and "YPOGEGRAMMENI" in name:
                val += "i"

            if val is not None:
                entries.append(entry(cp, val))
    return entries


def gen_hangul_jamo(existing):
    """Hangul Jamo 1100-11FF → same values as CHOSEONG/JUNGSEONG/JONGSEONG."""
    # Choseong (initial consonants) 1100-1112 (19 entries)
    choseong = [
        "g",
        "kk",
        "n",
        "d",
        "tt",
        "r",
        "m",
        "b",
        "pp",
        "s",
        "ss",
        "",
        "j",
        "jj",
        "ch",
        "k",
        "t",
        "p",
        "h",
    ]

    # Jungseong (medial vowels) 1161-1175 (21 entries)
    jungseong = [
        "a",
        "ae",
        "ya",
        "yae",
        "eo",
        "e",
        "yeo",
        "ye",
        "o",
        "wa",
        "wae",
        "oe",
        "yo",
        "u",
        "wo",
        "we",
        "wi",
        "yu",
        "eu",
        "ui",
        "i",
    ]

    # Jongseong (final consonants) 11A8-11C2 (27 entries, no empty slot 0)
    jongseong = [
        "g",
        "kk",
        "gs",
        "n",
        "nj",
        "nh",
        "d",
        "l",
        "lg",
        "lm",
        "lb",
        "ls",
        "lt",
        "lp",
        "lh",
        "m",
        "b",
        "bs",
        "s",
        "ss",
        "ng",
        "j",
        "ch",
        "k",
        "t",
        "p",
        "h",
    ]

    entries = []

    # Choseong 1100-1112
    for i, val in enumerate(choseong):
        cp = 0x1100 + i
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # Extended choseong 1113-115F (old/archaic)
    # Map these based on Unicode names - combine constituent jamo
    archaic_choseong = {
        0x1113: "n-g",
        0x1114: "nn",
        0x1115: "n-d",
        0x1116: "n-b",
        0x1117: "dd",
        0x1118: "r-n",
        0x1119: "rr",
        0x111A: "r-h",
        0x111B: "r-",
        0x111C: "mb",
        0x111D: "m-",
        0x111E: "b-g",
        0x111F: "b-n",
        0x1120: "b-d",
        0x1121: "bs",
        0x1122: "b-sg",
        0x1123: "b-sd",
        0x1124: "b-sb",
        0x1125: "b-ss",
        0x1126: "b-sj",
        0x1127: "b-j",
        0x1128: "b-ch",
        0x1129: "b-t",
        0x112A: "b-p",
        0x112B: "b-",
        0x112C: "bb-",
        0x112D: "s-g",
        0x112E: "s-n",
        0x112F: "s-d",
        0x1130: "s-r",
        0x1131: "s-m",
        0x1132: "s-b",
        0x1133: "sb-g",
        0x1134: "ss-s",
        0x1135: "s-",
        0x1136: "s-j",
        0x1137: "s-ch",
        0x1138: "s-k",
        0x1139: "s-t",
        0x113A: "s-p",
        0x113B: "s-h",
        0x113C: "ss-",
        0x113D: "ss-",
        0x113E: "ss-",
        0x113F: "ss-",
        0x1140: "z",
        0x1141: "-g",
        0x1142: "-d",
        0x1143: "-m",
        0x1144: "-b",
        0x1145: "-s",
        0x1146: "-z",
        0x1147: "ng",
        0x1148: "j-",
        0x1149: "jj-",
        0x114A: "j-",
        0x114B: "ch-",
        0x114C: "ng",
        0x114D: "j",
        0x114E: "ch",
        0x114F: "ch",
        0x1150: "ch",
        0x1151: "ch-k",
        0x1152: "ch-h",
        0x1153: "ch-",
        0x1154: "ch",
        0x1155: "p-b",
        0x1156: "p-",
        0x1157: "h",
        0x1158: "h",
        0x1159: "ng",
        0x115A: "g-d",
        0x115B: "n-s",
        0x115C: "n-j",
        0x115D: "n-h",
        0x115E: "d-r",
    }
    for cp, val in sorted(archaic_choseong.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # Also 115F: Choseong filler
    if 0x115F not in existing and is_assigned(0x115F):
        entries.append(entry(0x115F, ""))
    # 1160: Jungseong filler
    if 0x1160 not in existing and is_assigned(0x1160):
        entries.append(entry(0x1160, ""))

    # Jungseong 1161-1175
    for i, val in enumerate(jungseong):
        cp = 0x1161 + i
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # Extended jungseong 1176-11A7 (archaic vowels)
    archaic_jungseong = {
        0x1176: "a-o",
        0x1177: "a-u",
        0x1178: "ya-o",
        0x1179: "ya-yo",
        0x117A: "eo-o",
        0x117B: "eo-u",
        0x117C: "eo-eu",
        0x117D: "yeo-o",
        0x117E: "yeo-u",
        0x117F: "o-eo",
        0x1180: "o-e",
        0x1181: "o-ye",
        0x1182: "o-o",
        0x1183: "o-u",
        0x1184: "yo-ya",
        0x1185: "yo-yae",
        0x1186: "yo-yeo",
        0x1187: "yo-o",
        0x1188: "yo-i",
        0x1189: "u-a",
        0x118A: "u-ae",
        0x118B: "u-eo-eu",
        0x118C: "u-ye",
        0x118D: "u-u",
        0x118E: "yu-a",
        0x118F: "yu-eo",
        0x1190: "yu-e",
        0x1191: "yu-yeo",
        0x1192: "yu-ye",
        0x1193: "yu-u",
        0x1194: "yu-i",
        0x1195: "eu-u",
        0x1196: "eu-eu",
        0x1197: "yi",
        0x1198: "i-a",
        0x1199: "i-ya",
        0x119A: "i-o",
        0x119B: "i-u",
        0x119C: "i-eu",
        0x119D: "i-",
        0x119E: "a",
        0x119F: "a-eo",
        0x11A0: "a-u",
        0x11A1: "a-i",
        0x11A2: "a-",
        0x11A3: "a-e",
        0x11A4: "a-o",
        0x11A5: "a-u",
        0x11A6: "a-eu",
        0x11A7: "i-ya-o",
    }
    for cp, val in sorted(archaic_jungseong.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # Jongseong 11A8-11C2
    for i, val in enumerate(jongseong):
        cp = 0x11A8 + i
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # Extended jongseong 11C3-11FF (archaic finals)
    archaic_jongseong = {
        0x11C3: "g-r",
        0x11C4: "g-sg",
        0x11C5: "n-g",
        0x11C6: "n-d",
        0x11C7: "n-s",
        0x11C8: "n-z",
        0x11C9: "n-t",
        0x11CA: "d-g",
        0x11CB: "d-r",
        0x11CC: "r-gs",
        0x11CD: "r-n",
        0x11CE: "r-d",
        0x11CF: "r-dh",
        0x11D0: "rr",
        0x11D1: "r-mb",
        0x11D2: "r-bs",
        0x11D3: "r-b-s",
        0x11D4: "r-b-h",
        0x11D5: "r-b-",
        0x11D6: "r-ss",
        0x11D7: "r-z",
        0x11D8: "r-k",
        0x11D9: "r-",
        0x11DA: "m-g",
        0x11DB: "m-r",
        0x11DC: "m-b",
        0x11DD: "m-s",
        0x11DE: "m-ss",
        0x11DF: "m-z",
        0x11E0: "m-ch",
        0x11E1: "m-h",
        0x11E2: "m-",
        0x11E3: "b-r",
        0x11E4: "b-ph",
        0x11E5: "b-h",
        0x11E6: "b-",
        0x11E7: "s-g",
        0x11E8: "s-d",
        0x11E9: "s-r",
        0x11EA: "s-b",
        0x11EB: "z",
        0x11EC: "ng-g",
        0x11ED: "ng-gg",
        0x11EE: "ng-ng",
        0x11EF: "ng-k",
        0x11F0: "ng",
        0x11F1: "ng-s",
        0x11F2: "ng-z",
        0x11F3: "p-b",
        0x11F4: "p-",
        0x11F5: "h-n",
        0x11F6: "h-r",
        0x11F7: "h-m",
        0x11F8: "h-b",
        0x11F9: "ng",
        0x11FA: "g-n",
        0x11FB: "g-b",
        0x11FC: "g-ch",
        0x11FD: "g-k",
        0x11FE: "g-h",
        0x11FF: "nn",
    }
    for cp, val in sorted(archaic_jongseong.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    return entries


def _parse_decomposition_target(decomp):
    """Extract the target codepoint from a Unicode decomposition string.

    Handles formats like '4E00', '<compat> 4E00', '<font> 4E00', etc.
    Returns the integer codepoint or None if unparseable.
    """
    if not decomp:
        return None
    # Strip decomposition type tags like <compat>, <font>, etc.
    parts = decomp.strip().split()
    # Take the last hex value (skip tags)
    for part in reversed(parts):
        if not part.startswith("<"):
            try:
                return int(part, 16)
            except ValueError:
                continue
    return None


def gen_kangxi_radicals(existing, hanzi_pinyin):
    """Kangxi Radicals 2F00-2FD5 → canonical CJK equivalent → pinyin."""
    entries = []
    for cp in range(0x2F00, 0x2FD6):
        if cp not in existing and is_assigned(cp):
            decomp = unicodedata.decomposition(chr(cp))
            target_cp = _parse_decomposition_target(decomp)
            if target_cp is not None:
                pinyin = hanzi_pinyin.get(target_cp, "")
                if pinyin:
                    entries.append(entry(cp, pinyin))
    return entries


def gen_cjk_compat(existing, hanzi_pinyin):
    """CJK Compatibility Ideographs F900-FAFF → canonical equivalent → pinyin."""
    entries = []
    for cp in range(0xF900, 0xFB00):
        if cp not in existing and is_assigned(cp):
            decomp = unicodedata.decomposition(chr(cp))
            target_cp = _parse_decomposition_target(decomp)
            if target_cp is not None:
                pinyin = hanzi_pinyin.get(target_cp, "")
                if pinyin:
                    entries.append(entry(cp, pinyin))
    return entries


# ── TIER 2: Living scripts ────────────────────────────────────────────────


def gen_tier2_gap_filling(existing):
    """Gap-filling for partially covered scripts (Batch 2A)."""
    entries = []

    # Canadian Syllabics gaps (only 2)
    for cp in range(0x1400, 0x1680):
        if cp not in existing and is_assigned(cp):
            name = unicodedata.name(chr(cp), "")
            # These are typically separators or rare syllabics
            if "HYPHEN" in name or "SEPARATOR" in name:
                entries.append(entry(cp, "-"))
            # Otherwise skip - we only need the 2 missing ones

    # Cherokee gaps (6)
    for cp in range(0x13A0, 0x1400):
        if cp not in existing and is_assigned(cp):
            name = unicodedata.name(chr(cp), "")
            # Try to find the transliteration from the name
            if "CHEROKEE" in name:
                # Cherokee letters are named "CHEROKEE LETTER X" or "CHEROKEE SMALL LETTER X"
                m = re.search(r"LETTER\s+(\w+)", name)
                if m:
                    syllable = m.group(1).lower()
                    # Cherokee syllabary values
                    val = syllable[:3] if len(syllable) > 3 else syllable
                    entries.append(entry(cp, val))

    # N'Ko gaps (9)
    nko_map = {
        0x07C0: "0",
        0x07C1: "1",
        0x07C2: "2",
        0x07C3: "3",
        0x07C4: "4",
        0x07C5: "5",
        0x07C6: "6",
        0x07C7: "7",
        0x07C8: "8",
        0x07C9: "9",
        0x07CA: "a",
        0x07CB: "ee",
        0x07CC: "i",
        0x07CD: "e",
        0x07CE: "u",
        0x07CF: "oo",
        0x07D0: "o",
        0x07D1: "da",
        0x07D2: "ba",
        0x07D3: "pa",
        0x07D4: "ta",
        0x07D5: "ja",
        0x07D6: "cha",
        0x07D7: "ra",
        0x07D8: "rra",
        0x07D9: "sa",
        0x07DA: "gba",
        0x07DB: "fa",
        0x07DC: "ka",
        0x07DD: "la",
        0x07DE: "na",
        0x07DF: "ma",
        0x07E0: "nya",
        0x07E1: "na2",
        0x07E2: "ha",
        0x07E3: "wa",
        0x07E4: "ya",
        0x07E5: "nta",
        0x07E6: "nda",
        0x07E7: "nba",
        0x07E8: "nga",
        0x07E9: "nka",
        0x07EA: "ya2",
        0x07EB: "",
        0x07EC: "",
        0x07ED: "",
        0x07EE: "",
        0x07EF: "",
        0x07F0: "",
        0x07F1: "",
        0x07F2: "",
        0x07F3: "",
        0x07F4: "'",
        0x07F5: "'",
        0x07F6: "o",
        0x07F7: ".",
        0x07F8: ",",
        0x07F9: "!",
        0x07FA: "la",
    }
    for cp, val in sorted(nko_map.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # Syriac gaps (6)
    syriac_map = {
        0x0700: "",
        0x0701: "",
        0x0702: "",
        0x0703: ":",
        0x0704: ":",
        0x0705: ".",
        0x0706: ".",
        0x0707: ".",
        0x0708: "+",
        0x0709: "-",
        0x070A: "+",
        0x070B: "'",
        0x070C: ",",
        0x070D: "!",
        0x070F: "",  # SAM
        0x0710: "'",  # ALAPH
        0x0711: "",  # superscript alaph
        0x0712: "b",
        0x0713: "g",
        0x0714: "g",
        0x0715: "d",
        0x0716: "d",
        0x0717: "h",
        0x0718: "w",
        0x0719: "z",
        0x071A: "ch",
        0x071B: "t",
        0x071C: "t",
        0x071D: "y",
        0x071E: "yh",
        0x071F: "k",
        0x0720: "l",
        0x0721: "m",
        0x0722: "n",
        0x0723: "s",
        0x0724: "s",
        0x0725: "'",
        0x0726: "p",
        0x0727: "p",
        0x0728: "ts",
        0x0729: "q",
        0x072A: "r",
        0x072B: "sh",
        0x072C: "t",
        0x072D: "p",
        0x072E: "p",
        0x072F: "zh",
        0x0730: "",
        0x0731: "",
        0x0732: "",
        0x0733: "",
        0x0734: "",
        0x0735: "",
        0x0736: "",
        0x0737: "",
        0x0738: "",
        0x0739: "",
        0x073A: "",
        0x073B: "",
        0x073C: "",
        0x073D: "",
        0x073E: "",
        0x073F: "",
        0x0740: "",
        0x0741: "",
        0x0742: "",
        0x0743: "",
        0x0744: "",
        0x0745: "",
        0x0746: "",
        0x0747: "",
        0x0748: "",
        0x0749: "",
        0x074A: "",
        0x074D: "zh",
        0x074E: "k",
        0x074F: "hn",
    }
    for cp, val in sorted(syriac_map.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # Vai gaps (30)
    # Vai is a syllabary - each character represents a syllable
    # We need to find the 30 gaps and map them
    for cp in range(0xA500, 0xA640):
        if cp not in existing and is_assigned(cp):
            name = unicodedata.name(chr(cp), "")
            if "VAI" in name:
                # Extract syllable from name: "VAI SYLLABLE X" → "x"
                m = re.search(r"SYLLABLE\s+(.+)", name)
                if m:
                    syl = m.group(1).lower()
                    # Clean up multi-word
                    syl = syl.replace(" ", "")
                    if syl.isascii():
                        entries.append(entry(cp, syl))
                    else:
                        entries.append(entry(cp, syl[:3]))
                elif "DIGIT" in name:
                    m2 = re.search(r"DIGIT\s+(\w+)", name)
                    if m2:
                        digit_names = {
                            "ZERO": "0",
                            "ONE": "1",
                            "TWO": "2",
                            "THREE": "3",
                            "FOUR": "4",
                            "FIVE": "5",
                            "SIX": "6",
                            "SEVEN": "7",
                            "EIGHT": "8",
                            "NINE": "9",
                        }
                        entries.append(entry(cp, digit_names.get(m2.group(1), "?")))
                elif "COMMA" in name:
                    entries.append(entry(cp, ","))
                elif "FULL STOP" in name:
                    entries.append(entry(cp, "."))

    # Coptic gaps (59) - map remaining based on Greek equivalents
    coptic_remaining = {
        0x2CC0: "sh",
        0x2CC1: "sh",  # OLD COPTIC SHEI
        0x2CC2: "f",
        0x2CC3: "f",  # OLD COPTIC ESH
        0x2CC4: "kh",
        0x2CC5: "kh",  # OLD COPTIC AKHMIMIC KHEI
        0x2CC6: "h",
        0x2CC7: "h",  # OLD COPTIC HORI
        0x2CC8: "j",
        0x2CC9: "j",  # OLD COPTIC GANGIA
        0x2CCA: "c",
        0x2CCB: "c",  # OLD COPTIC SHIMA
        0x2CCC: "ti",
        0x2CCD: "ti",  # OLD COPTIC DEI
        0x2CCE: "k",
        0x2CCF: "k",  # OLD COPTIC HAT
        0x2CD0: "g",
        0x2CD1: "g",  # OLD COPTIC GANGIA
        0x2CD2: "s",
        0x2CD3: "s",  # OLD COPTIC SAMPI
        0x2CD4: "t",
        0x2CD5: "t",  # OLD COPTIC TAU
        0x2CD6: "sh",
        0x2CD7: "sh",  # COPTIC CAPITAL/SMALL LETTER OLD COPTIC SHEI
        0x2CD8: "ch",
        0x2CD9: "ch",  # COPTIC SHE/CHE
        0x2CDA: "a",
        0x2CDB: "a",  # COPTIC AKHMIMIC ALEF
        0x2CDC: "i",
        0x2CDD: "i",  # COPTIC IAUDA
        0x2CDE: "kh",
        0x2CDF: "kh",  # COPTIC KHEI
        0x2CE0: "sh",
        0x2CE1: "sh",  # COPTIC CRYPTOGRAMMIC SHEI
        0x2CE2: "r",
        0x2CE3: "r",  # COPTIC CRYPTOGRAMMIC GANGIA
        0x2CE4: "",  # COPTIC COMBINING NI ABOVE
        0x2CE5: "",
        0x2CE6: "",
        0x2CE7: "",
        0x2CE8: "",
        0x2CE9: "",  # Coptic symbols
        0x2CEA: "",
        0x2CEB: "j",
        0x2CEC: "j",  # COPTIC CAPITAL/SMALL LETTER CRYPTOGRAMMIC SHEI
        0x2CED: "sh",
        0x2CEE: "sh",
        0x2CEF: "",
        0x2CF0: "",
        0x2CF1: "",  # Coptic combining marks
        0x2CF2: "",
        0x2CF3: "",  # COPTIC CAPITAL/SMALL BOHAIRIC KHEI
    }
    for cp, val in sorted(coptic_remaining.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # Balinese gaps (40)
    balinese_gaps = {
        0x1B00: "",
        0x1B01: "",
        0x1B02: "",
        0x1B03: "",
        0x1B04: "",  # signs
        0x1B05: "a",
        0x1B06: "a",
        0x1B07: "i",
        0x1B08: "i",
        0x1B09: "u",
        0x1B0A: "u",
        0x1B0B: "r",
        0x1B0C: "r",
        0x1B0D: "l",
        0x1B0E: "l",
        0x1B0F: "e",
        0x1B10: "ai",
        0x1B11: "o",
        0x1B12: "au",
        # 1B13-1B33 consonants already covered, 1B35-1B44 vowels/virama already covered
        0x1B45: "ka",
        0x1B46: "sa",
        0x1B47: "ta",
        0x1B48: "na",
        0x1B49: "pa",
        0x1B4A: "da",
        0x1B4B: "ra",
        # digits
        0x1B50: "0",
        0x1B51: "1",
        0x1B52: "2",
        0x1B53: "3",
        0x1B54: "4",
        0x1B55: "5",
        0x1B56: "6",
        0x1B57: "7",
        0x1B58: "8",
        0x1B59: "9",
        # punctuation
        0x1B5A: ".",
        0x1B5B: ".",
        0x1B5C: ".",
        0x1B5D: ",",
        0x1B5E: ".",
        0x1B5F: ".",
        0x1B60: "",  # BALINESE PAMENENG
        0x1B61: "0",
        0x1B62: "1",
        0x1B63: "2",
        0x1B64: "3",
        0x1B65: "4",
        0x1B66: "5",
        0x1B67: "6",
        0x1B68: "7",
        0x1B69: "8",
        0x1B6A: "9",
        0x1B6B: "",
        0x1B6C: "",
        0x1B6D: "",
        0x1B6E: "",
        0x1B6F: "",
        0x1B70: "",
        0x1B71: "",
        0x1B72: "",
        0x1B73: "",
        0x1B74: "",
        0x1B75: "",
        0x1B76: "",
        0x1B77: "",
        0x1B78: "",
        0x1B79: "",
        0x1B7A: "",
        0x1B7B: "",
        0x1B7C: "",
    }
    for cp, val in sorted(balinese_gaps.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    return entries


def gen_new_abugida_scripts(existing):
    """New abugida scripts needing code + TSV (Batch 2B)."""
    entries = []

    # ── Sundanese 1B80-1BBF ──
    sundanese = {
        0x1B80: "",
        0x1B81: "",
        0x1B82: "",  # signs
        # Independent vowels
        0x1B83: "a",
        0x1B84: "i",
        0x1B85: "u",
        0x1B86: "ae",
        0x1B87: "o",
        0x1B88: "e",
        0x1B89: "eu",
        # Consonants (with inherent "a")
        0x1B8A: "ka",
        0x1B8B: "qa",
        0x1B8C: "ga",
        0x1B8D: "nga",
        0x1B8E: "ca",
        0x1B8F: "ja",
        0x1B90: "za",
        0x1B91: "nya",
        0x1B92: "ta",
        0x1B93: "da",
        0x1B94: "na",
        0x1B95: "pa",
        0x1B96: "fa",
        0x1B97: "ba",
        0x1B98: "ma",
        0x1B99: "ya",
        0x1B9A: "ra",
        0x1B9B: "la",
        0x1B9C: "wa",
        0x1B9D: "sa",
        0x1B9E: "ha",
        0x1B9F: "sa",
        0x1BA0: "xa",  # additional consonants
        # Dependent vowels
        0x1BA1: "i",
        0x1BA2: "u",
        0x1BA3: "eu",
        0x1BA4: "i",
        0x1BA5: "u",
        0x1BA6: "e",
        0x1BA7: "o",
        0x1BA8: "",
        0x1BA9: "",  # combining marks
        0x1BAA: "r",  # SUNDANESE SIGN PANYECEK (final r)
        0x1BAB: "",  # SUNDANESE SIGN VIRAMA
        0x1BAC: "",
        0x1BAD: "",  # subjoined
        # Digits
        0x1BB0: "0",
        0x1BB1: "1",
        0x1BB2: "2",
        0x1BB3: "3",
        0x1BB4: "4",
        0x1BB5: "5",
        0x1BB6: "6",
        0x1BB7: "7",
        0x1BB8: "8",
        0x1BB9: "9",
        # Avagraha etc
        0x1BBA: "",
        0x1BBB: "",
        0x1BBC: "",
        0x1BBD: "",
        0x1BBE: "",
        0x1BBF: "",
    }
    for cp, val in sorted(sundanese.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # ── Tai Tham 1A20-1AAF ──
    tai_tham = {
        # Consonants (with inherent "a")
        0x1A20: "ka",
        0x1A21: "kha",
        0x1A22: "kha",
        0x1A23: "ga",
        0x1A24: "gha",
        0x1A25: "nga",
        0x1A26: "ca",
        0x1A27: "sa",
        0x1A28: "cha",
        0x1A29: "ja",
        0x1A2A: "ha",
        0x1A2B: "nya",
        0x1A2C: "da",
        0x1A2D: "na",
        0x1A2E: "da",
        0x1A2F: "tha",
        0x1A30: "tha",
        0x1A31: "da",
        0x1A32: "dha",
        0x1A33: "na",
        0x1A34: "ba",
        0x1A35: "pa",
        0x1A36: "pha",
        0x1A37: "fa",
        0x1A38: "pha",
        0x1A39: "ba",
        0x1A3A: "bha",
        0x1A3B: "ma",
        0x1A3C: "ya",
        0x1A3D: "ra",
        0x1A3E: "la",
        0x1A3F: "wa",
        0x1A40: "sa",
        0x1A41: "ha",
        0x1A42: "la",
        0x1A43: "a",  # independent a
        0x1A44: "ha",
        0x1A45: "a",
        0x1A46: "sa",
        0x1A47: "sa",
        0x1A48: "ha",
        0x1A49: "ha",
        0x1A4A: "la",
        0x1A4B: "a",
        0x1A4C: "a",
        # High consonants
        0x1A4D: "ka",
        0x1A4E: "kha",
        0x1A4F: "kha",
        0x1A50: "ga",
        0x1A51: "nga",
        0x1A52: "ca",
        0x1A53: "sa",
        # Dependent vowels
        0x1A54: "i",
        0x1A55: "a",
        0x1A56: "a",
        0x1A57: "",  # subjoined
        0x1A58: "",
        0x1A59: "",
        0x1A5A: "",
        0x1A5B: "",
        0x1A5C: "",
        0x1A5D: "",
        0x1A5E: "",  # combining marks
        0x1A60: "",  # VIRAMA (sakot)
        0x1A61: "i",
        0x1A62: "i",
        0x1A63: "aa",
        0x1A64: "aa",
        0x1A65: "i",
        0x1A66: "ii",
        0x1A67: "u",
        0x1A68: "uu",
        0x1A69: "u",
        0x1A6A: "uu",
        0x1A6B: "o",
        0x1A6C: "oa",
        0x1A6D: "oy",
        0x1A6E: "e",
        0x1A6F: "ae",
        0x1A70: "o",
        0x1A71: "ai",
        0x1A72: "ao",
        0x1A73: "",
        0x1A74: "",
        0x1A75: "",
        0x1A76: "",
        0x1A77: "",
        0x1A78: "",
        0x1A79: "",
        0x1A7A: "",
        0x1A7B: "",
        0x1A7C: "",
        0x1A7F: "",  # combining mark
        # Digits (hora)
        0x1A80: "0",
        0x1A81: "1",
        0x1A82: "2",
        0x1A83: "3",
        0x1A84: "4",
        0x1A85: "5",
        0x1A86: "6",
        0x1A87: "7",
        0x1A88: "8",
        0x1A89: "9",
        # Digits (tham)
        0x1A90: "0",
        0x1A91: "1",
        0x1A92: "2",
        0x1A93: "3",
        0x1A94: "4",
        0x1A95: "5",
        0x1A96: "6",
        0x1A97: "7",
        0x1A98: "8",
        0x1A99: "9",
        # Signs
        0x1AA0: ".",
        0x1AA1: ".",
        0x1AA2: ".",
        0x1AA3: ".",
        0x1AA4: ".",
        0x1AA5: ".",
        0x1AA6: "",
        0x1AA7: "",  # letter
        0x1AA8: ".",
        0x1AA9: ".",
        0x1AAA: ".",
        0x1AAB: ".",
        0x1AAC: "",
        0x1AAD: "",
    }
    for cp, val in sorted(tai_tham.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # ── Cham AA00-AA5F ──
    cham = {
        # Consonants (with inherent "a")
        0xAA00: "ka",
        0xAA01: "kha",
        0xAA02: "ga",
        0xAA03: "gha",
        0xAA04: "ngha",
        0xAA05: "nga",
        0xAA06: "cha",
        0xAA07: "chha",
        0xAA08: "ja",
        0xAA09: "jha",
        0xAA0A: "nhja",
        0xAA0B: "nha",
        0xAA0C: "nhra",
        0xAA0D: "a",
        0xAA0E: "ta",
        0xAA0F: "tha",
        0xAA10: "da",
        0xAA11: "dha",
        0xAA12: "nra",
        0xAA13: "na",
        0xAA14: "dda",
        0xAA15: "pa",
        0xAA16: "ppa",
        0xAA17: "pha",
        0xAA18: "ba",
        0xAA19: "bha",
        0xAA1A: "mba",
        0xAA1B: "ma",
        0xAA1C: "bba",
        0xAA1D: "ya",
        0xAA1E: "ra",
        0xAA1F: "la",
        0xAA20: "va",
        0xAA21: "sha",
        0xAA22: "sa",
        0xAA23: "ha",
        0xAA24: "la",
        0xAA25: "wa",
        0xAA26: "a",
        0xAA27: "a",
        0xAA28: "a",
        # Dependent vowels
        0xAA29: "i",
        0xAA2A: "i",
        0xAA2B: "ei",
        0xAA2C: "u",
        0xAA2D: "oe",
        0xAA2E: "o",
        0xAA2F: "ai",
        0xAA30: "au",
        0xAA31: "e",
        0xAA32: "o",
        # Consonant signs
        0xAA33: "ya",
        0xAA34: "ra",
        0xAA35: "",
        0xAA36: "",
        # Digits
        0xAA40: "la",
        0xAA41: "la",
        0xAA42: "la",
        0xAA43: "",  # consonant sign
        0xAA44: "la",
        0xAA45: "la",
        0xAA46: "la",
        0xAA47: "la",
        0xAA48: "la",
        0xAA49: "la",
        0xAA4A: "la",
        0xAA4B: "la",
        0xAA4C: "",  # sign
        0xAA4D: "",  # VIRAMA
        0xAA50: "0",
        0xAA51: "1",
        0xAA52: "2",
        0xAA53: "3",
        0xAA54: "4",
        0xAA55: "5",
        0xAA56: "6",
        0xAA57: "7",
        0xAA58: "8",
        0xAA59: "9",
        0xAA5C: ".",
        0xAA5D: ".",
        0xAA5E: ".",
        0xAA5F: ".",
    }
    for cp, val in sorted(cham.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # ── Batak 1BC0-1BFF ──
    batak = {
        # Consonants (with inherent "a")
        0x1BC0: "a",
        0x1BC1: "ha",
        0x1BC2: "ha",
        0x1BC3: "ba",
        0x1BC4: "ba",
        0x1BC5: "pa",
        0x1BC6: "pa",
        0x1BC7: "na",
        0x1BC8: "na",
        0x1BC9: "na",
        0x1BCA: "wa",
        0x1BCB: "wa",
        0x1BCC: "ga",
        0x1BCD: "ga",
        0x1BCE: "ja",
        0x1BCF: "da",
        0x1BD0: "da",
        0x1BD1: "ra",
        0x1BD2: "ra",
        0x1BD3: "ma",
        0x1BD4: "ma",
        0x1BD5: "ta",
        0x1BD6: "ta",
        0x1BD7: "sa",
        0x1BD8: "sa",
        0x1BD9: "sa",
        0x1BDA: "ya",
        0x1BDB: "ya",
        0x1BDC: "nga",
        0x1BDD: "nga",
        0x1BDE: "la",
        0x1BDF: "la",
        0x1BE0: "la",
        0x1BE1: "la",
        0x1BE2: "ca",
        0x1BE3: "ca",
        # Independent vowels
        0x1BE4: "i",
        0x1BE5: "u",
        # Dependent vowels
        0x1BE6: "",  # sign
        0x1BE7: "e",
        0x1BE8: "i",
        0x1BE9: "i",
        0x1BEA: "u",
        0x1BEB: "u",
        0x1BEC: "u",
        0x1BED: "o",
        0x1BEE: "e",
        0x1BEF: "",
        0x1BF0: "",
        0x1BF1: "",  # combining marks
        # Virama
        0x1BF2: "",
        0x1BF3: "",  # VIRAMA (pangolat)
        # Punctuation
        0x1BFC: ".",
        0x1BFD: ".",
        0x1BFE: ".",
        0x1BFF: ".",
    }
    for cp, val in sorted(batak.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # ── Buginese 1A00-1A1F ──
    buginese = {
        # Consonants (with inherent "a")
        0x1A00: "ka",
        0x1A01: "ga",
        0x1A02: "nga",
        0x1A03: "ngka",
        0x1A04: "pa",
        0x1A05: "ba",
        0x1A06: "ma",
        0x1A07: "mpa",
        0x1A08: "ta",
        0x1A09: "da",
        0x1A0A: "na",
        0x1A0B: "nra",
        0x1A0C: "ca",
        0x1A0D: "ja",
        0x1A0E: "nya",
        0x1A0F: "nyca",
        0x1A10: "ya",
        0x1A11: "ra",
        0x1A12: "la",
        0x1A13: "wa",
        0x1A14: "sa",
        0x1A15: "a",
        0x1A16: "ha",
        # Dependent vowels
        0x1A17: "i",
        0x1A18: "u",
        0x1A19: "e",
        0x1A1A: "o",
        0x1A1B: "e",
        # Punctuation
        0x1A1E: ".",
        0x1A1F: ".",
    }
    for cp, val in sorted(buginese.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # ── Tagalog 1700-171F ──
    tagalog = {
        0x1700: "a",
        0x1701: "i",
        0x1702: "u",
        # Consonants (with inherent "a")
        0x1703: "ka",
        0x1704: "ga",
        0x1705: "nga",
        0x1706: "ta",
        0x1707: "da",
        0x1708: "na",
        0x1709: "pa",
        0x170A: "ba",
        0x170B: "ma",
        0x170C: "ya",
        0x170D: "ra",
        0x170E: "la",
        0x170F: "wa",
        0x1710: "sa",
        0x1711: "ha",
        # Dependent vowels
        0x1712: "i",
        0x1713: "u",
        # Virama
        0x1714: "",
        0x1715: "",  # sign pamudpod
        # New additions in later Unicode
        0x171F: "ra",
    }
    for cp, val in sorted(tagalog.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # ── Hanunoo 1720-173F ──
    hanunoo = {
        0x1720: "a",
        0x1721: "i",
        0x1722: "u",
        # Consonants (with inherent "a")
        0x1723: "ka",
        0x1724: "ga",
        0x1725: "nga",
        0x1726: "ta",
        0x1727: "da",
        0x1728: "na",
        0x1729: "pa",
        0x172A: "ba",
        0x172B: "ma",
        0x172C: "ya",
        0x172D: "ra",
        0x172E: "la",
        0x172F: "wa",
        0x1730: "sa",
        0x1731: "ha",
        # Dependent vowels
        0x1732: "i",
        0x1733: "u",
        # Virama
        0x1734: "",
        # Philippine punctuation
        0x1735: ".",
        0x1736: ".",
    }
    for cp, val in sorted(hanunoo.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # ── Buhid 1740-175F ──
    buhid = {
        0x1740: "a",
        0x1741: "i",
        0x1742: "u",
        # Consonants (with inherent "a")
        0x1743: "ka",
        0x1744: "ga",
        0x1745: "nga",
        0x1746: "ta",
        0x1747: "da",
        0x1748: "na",
        0x1749: "pa",
        0x174A: "ba",
        0x174B: "ma",
        0x174C: "ya",
        0x174D: "ra",
        0x174E: "la",
        0x174F: "wa",
        0x1750: "sa",
        0x1751: "ha",
        # Dependent vowels
        0x1752: "i",
        0x1753: "u",
    }
    for cp, val in sorted(buhid.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # ── Tagbanwa 1760-177F ──
    tagbanwa = {
        0x1760: "a",
        0x1761: "i",
        0x1762: "u",
        # Consonants (with inherent "a")
        0x1763: "ka",
        0x1764: "ga",
        0x1765: "nga",
        0x1766: "ta",
        0x1767: "da",
        0x1768: "na",
        0x1769: "pa",
        0x176A: "ba",
        0x176B: "ma",
        0x176C: "ya",
        0x176E: "la",
        0x176F: "wa",
        0x1770: "sa",
        # Dependent vowels
        0x1772: "i",
        0x1773: "u",
    }
    for cp, val in sorted(tagbanwa.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # ── Meetei Mayek ABC0-ABFF + AAE0-AAFF ──
    meetei = {
        # Main block ABC0-ABFF
        0xABC0: "ka",
        0xABC1: "kha",
        0xABC2: "ga",
        0xABC3: "gha",
        0xABC4: "nga",
        0xABC5: "cha",
        0xABC6: "chha",
        0xABC7: "ja",
        0xABC8: "jha",
        0xABC9: "nya",
        0xABCA: "ta",
        0xABCB: "tha",
        0xABCC: "da",
        0xABCD: "dha",
        0xABCE: "na",
        0xABCF: "ta",
        0xABD0: "tha",
        0xABD1: "da",
        0xABD2: "dha",
        0xABD3: "na",
        0xABD4: "pa",
        0xABD5: "pha",
        0xABD6: "ba",
        0xABD7: "bha",
        0xABD8: "ma",
        0xABD9: "ya",
        0xABDA: "ra",
        0xABDB: "la",
        0xABDC: "wa",
        0xABDD: "sha",
        0xABDE: "sa",
        0xABDF: "ha",
        0xABE0: "kha",
        0xABE1: "sa",
        0xABE2: "sa",
        # Dependent vowels
        0xABE3: "aa",
        0xABE4: "ei",
        0xABE5: "i",
        0xABE6: "oo",
        0xABE7: "ou",
        0xABE8: "u",  # combining
        0xABE9: "ei",
        0xABEA: "ou",
        # Signs
        0xABEB: ".",  # CHEIKHEI (punctuation)
        0xABEC: "",  # LUM
        0xABED: "",  # VIRAMA (apun)
        # Digits
        0xABF0: "0",
        0xABF1: "1",
        0xABF2: "2",
        0xABF3: "3",
        0xABF4: "4",
        0xABF5: "5",
        0xABF6: "6",
        0xABF7: "7",
        0xABF8: "8",
        0xABF9: "9",
        # Extension block AAE0-AAFF
        0xAAE0: "e",
        0xAAE1: "o",  # vowels
        0xAAE2: "a",
        0xAAE3: "a",
        0xAAE4: "a",
        0xAAE5: "a",
        0xAAE6: "a",
        0xAAE7: "a",
        0xAAE8: "a",
        0xAAE9: "a",
        0xAAEA: "a",
        0xAAEB: "i",
        0xAAEC: "u",
        0xAAED: "e",
        0xAAEE: "o",
        0xAAEF: "ou",
        0xAAF0: ".",
        0xAAF1: ".",  # punctuation
        0xAAF2: "a",
        0xAAF3: "",
        0xAAF4: "",  # letters/signs
        0xAAF5: "",
        0xAAF6: "",  # virama/sign
    }
    for cp, val in sorted(meetei.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    return entries


def gen_alphabetic_scripts(existing):
    """Alphabetic/syllabic scripts, TSV-only (Batch 2C)."""
    entries = []

    # ── Tifinagh 2D30-2D7F (IRCAM standard) ──
    # Actually, Tifinagh letters are named "TIFINAGH LETTER YA", etc.
    # The romanization should just be the phonetic value
    tifinagh_corrected = {}
    for cp in range(0x2D30, 0x2D80):
        if cp not in existing and is_assigned(cp):
            name = unicodedata.name(chr(cp), "")
            if not name:
                continue
            if "SEPARATOR" in name:
                tifinagh_corrected[cp] = "."
            elif "MODIFIER" in name:
                tifinagh_corrected[cp] = "+"
            elif "JOINER" in name:
                tifinagh_corrected[cp] = ""
            elif "LETTER" in name:
                # Extract letter value from name
                m = re.search(r"LETTER\s+(.+)", name)
                if m:
                    letter_name = m.group(1).lower()
                    # Map Tifinagh letter names to IRCAM romanization
                    tif_map = {
                        "ya": "a",
                        "yab": "b",
                        "yabh": "bh",
                        "yag": "g",
                        "yaghh": "ghh",
                        "berber academy yaj": "j",
                        "yaj": "j",
                        "yad": "d",
                        "yadh": "dh",
                        "yadd": "dd",
                        "yaddh": "ddh",
                        "yey": "ey",
                        "ye": "e",
                        "yaf": "f",
                        "yak": "k",
                        "tuareg yak": "k",
                        "yakh": "kh",
                        "yah": "h",
                        "berber academy yah": "h",
                        "tuareg yah": "h",
                        "yahh": "hh",
                        "ya'": "'",
                        "tuareg yakh": "kh",
                        "akhh": "khh",
                        "yaq": "q",
                        "tuareg yaq": "q",
                        "yi": "i",
                        "yazh": "zh",
                        "tuareg yazh": "zh",
                        "ahaggar yazh": "zh",
                        "yal": "l",
                        "yam": "m",
                        "yan": "n",
                        "tuareg yagn": "gn",
                        "tuareg yang": "ng",
                        "yany": "ny",
                        "yang": "ng",
                        "yap": "p",
                        "yu": "u",
                        "yar": "r",
                        "yarr": "rr",
                        "yagh": "gh",
                        "tuareg yagh": "gh",
                        "ayer yagh": "gh",
                        "yas": "s",
                        "yass": "ss",
                        "yash": "sh",
                        "yat": "t",
                        "yath": "th",
                        "yach": "ch",
                        "yatt": "tt",
                        "yav": "v",
                        "yaw": "w",
                        "yay": "y",
                        "yaz": "z",
                        "yazz": "zz",
                        "tawellemet yaz": "z",
                        "yer": "e",
                        "yo": "o",
                    }
                    val = tif_map.get(letter_name)
                    if val is None:
                        # Try partial match
                        for k, v in tif_map.items():
                            if letter_name.endswith(k):
                                val = v
                                break
                    if val is None:
                        # Fallback: use first consonant/vowel from name
                        val = (
                            letter_name.replace("ya", "")
                            .replace("berber academy ", "")
                            .replace("tuareg ", "")[:3]
                        )
                        if not val:
                            val = letter_name[:2]
                    if val.isascii():
                        tifinagh_corrected[cp] = val

    for cp, val in sorted(tifinagh_corrected.items()):
        entries.append(entry(cp, val))

    # ── Lisu A4D0-A4FF (Fraser script — designed from Latin) ──
    lisu = {
        0xA4D0: "ba",
        0xA4D1: "pa",
        0xA4D2: "pha",
        0xA4D3: "da",
        0xA4D4: "ta",
        0xA4D5: "tha",
        0xA4D6: "ga",
        0xA4D7: "ka",
        0xA4D8: "kha",
        0xA4D9: "ja",
        0xA4DA: "ca",
        0xA4DB: "cha",
        0xA4DC: "dza",
        0xA4DD: "tsa",
        0xA4DE: "tsha",
        0xA4DF: "ma",
        0xA4E0: "na",
        0xA4E1: "la",
        0xA4E2: "sa",
        0xA4E3: "zha",
        0xA4E4: "za",
        0xA4E5: "nga",
        0xA4E6: "ha",
        0xA4E7: "xa",
        0xA4E8: "hha",
        0xA4E9: "fa",
        0xA4EA: "wa",
        0xA4EB: "sha",
        0xA4EC: "ya",
        0xA4ED: "gha",
        0xA4EE: "a",
        0xA4EF: "ae",
        0xA4F0: "e",
        0xA4F1: "eu",
        0xA4F2: "i",
        0xA4F3: "o",
        0xA4F4: "u",
        0xA4F5: "ue",
        0xA4F6: "uh",
        0xA4F7: "oe",
        0xA4F8: ".",
        0xA4F9: "-",
        0xA4FA: ":",
        0xA4FB: ".",
        0xA4FC: ".",
        0xA4FD: ".",
        0xA4FE: ".",
        0xA4FF: ".",
    }
    for cp, val in sorted(lisu.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # ── Ol Chiki 1C50-1C7F (Santali) ──
    ol_chiki = {
        # Digits
        0x1C50: "0",
        0x1C51: "1",
        0x1C52: "2",
        0x1C53: "3",
        0x1C54: "4",
        0x1C55: "5",
        0x1C56: "6",
        0x1C57: "7",
        0x1C58: "8",
        0x1C59: "9",
        # Letters
        0x1C5A: "la",
        0x1C5B: "at",
        0x1C5C: "ag",
        0x1C5D: "ang",
        0x1C5E: "al",
        0x1C5F: "laa",
        0x1C60: "aak",
        0x1C61: "aaj",
        0x1C62: "aam",
        0x1C63: "aaw",
        0x1C64: "li",
        0x1C65: "is",
        0x1C66: "ih",
        0x1C67: "iny",
        0x1C68: "ir",
        0x1C69: "lu",
        0x1C6A: "uc",
        0x1C6B: "ud",
        0x1C6C: "unn",
        0x1C6D: "unny",
        0x1C6E: "le",
        0x1C6F: "ep",
        0x1C70: "edd",
        0x1C71: "en",
        0x1C72: "err",
        0x1C73: "lo",
        0x1C74: "ott",
        0x1C75: "ob",
        0x1C76: "ov",
        0x1C77: "oh",
        # Modifier letters
        0x1C78: "",
        0x1C79: "",
        0x1C7A: "",
        0x1C7B: "",
        0x1C7C: "",
        0x1C7D: "ah",
        # Punctuation
        0x1C7E: ".",
        0x1C7F: ".",
    }
    for cp, val in sorted(ol_chiki.items()):
        if cp not in existing and is_assigned(cp):
            entries.append(entry(cp, val))

    # ── Bamum A6A0-A6FF (Syllabary) ──
    bamum_entries = []
    for cp in range(0xA6A0, 0xA700):
        if cp not in existing and is_assigned(cp):
            name = unicodedata.name(chr(cp), "")
            if not name:
                continue
            if "BAMUM LETTER" in name:
                # Extract syllable value from Unicode name
                m = re.search(r"LETTER\s+(.+)", name)
                if m:
                    syl = m.group(1).lower()
                    # Capitalize mapping: use the syllable name
                    # Many Bamum letters are named with their syllable value
                    # e.g. "BAMUM LETTER A" → "a", "BAMUM LETTER KA" → "ka"
                    syl = syl.replace("phase-", "").strip()
                    # Clean up common patterns
                    if "small" in syl:
                        syl = syl.replace("small ", "")
                    # Take just the syllable part
                    parts = syl.split()
                    if parts:
                        val = parts[-1] if parts[-1].isascii() else parts[0]
                        if val.isascii() and len(val) <= 6:
                            bamum_entries.append(entry(cp, val))
            elif "BAMUM COMMA" in name:
                bamum_entries.append(entry(cp, ","))
            elif "BAMUM SEMICOLON" in name:
                bamum_entries.append(entry(cp, ";"))
            elif "BAMUM COLON" in name:
                bamum_entries.append(entry(cp, ":"))
            elif "BAMUM FULL STOP" in name:
                bamum_entries.append(entry(cp, "."))
            elif "BAMUM QUESTION" in name:
                bamum_entries.append(entry(cp, "?"))
    entries.extend(bamum_entries)

    return entries


# ── Main ──────────────────────────────────────────────────────────────────


def main():
    base = Path(__file__).parent.parent / "src" / "tables" / "data"
    tsv_path = base / "translit_default.tsv"
    hanzi_path = base / "hanzi_pinyin.tsv"

    existing = load_existing_tsv(tsv_path)
    hanzi_pinyin = load_hanzi_pinyin(hanzi_path)

    all_entries = []

    # Batch 1A: Mechanical mappings
    print("Generating Batch 1A: Mechanical mappings...", file=sys.stderr)
    all_entries.extend(gen_fullwidth(existing))
    all_entries.extend(gen_halfwidth_hangul(existing))
    all_entries.extend(gen_enclosed_circled(existing))
    all_entries.extend(gen_super_subscript(existing))
    all_entries.extend(gen_roman_numerals(existing))
    all_entries.extend(gen_modifier_letters(existing))

    # Batch 1B: Reference lookups
    print("Generating Batch 1B: Reference lookups...", file=sys.stderr)
    all_entries.extend(gen_ipa(existing))
    all_entries.extend(gen_greek_extended(existing))
    all_entries.extend(gen_hangul_jamo(existing))
    all_entries.extend(gen_kangxi_radicals(existing, hanzi_pinyin))
    all_entries.extend(gen_cjk_compat(existing, hanzi_pinyin))

    # Batch 2A: Gap filling
    print("Generating Batch 2A: Gap filling...", file=sys.stderr)
    all_entries.extend(gen_tier2_gap_filling(existing))

    # Batch 2B: New abugida scripts
    print("Generating Batch 2B: New abugida scripts...", file=sys.stderr)
    all_entries.extend(gen_new_abugida_scripts(existing))

    # Batch 2C: Alphabetic/syllabic scripts
    print("Generating Batch 2C: Alphabetic/syllabic scripts...", file=sys.stderr)
    all_entries.extend(gen_alphabetic_scripts(existing))

    # Deduplicate (prefer first occurrence) and sort by codepoint
    seen = set()
    unique = []
    for cp, val in all_entries:
        if cp not in seen and cp not in existing:
            seen.add(cp)
            unique.append((cp, val))
    unique.sort(key=lambda x: x[0])

    print(f"Generated {len(unique)} new entries", file=sys.stderr)

    # Output TSV
    for cp, val in unique:
        print(f"{cp:04X}\t{val}")


if __name__ == "__main__":
    main()
