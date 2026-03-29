#!/usr/bin/env python3
"""Build Persian context dictionary from common word lists + rules.

Persian lacks a large diacritized corpus like Arabic's Tashkeela. Instead,
this builder creates a dictionary from:

1. A curated list of common Persian words with their known romanizations
2. Persian words that appear in the Arabic Tashkeela corpus (Arabic loanwords)
3. Rule-based expansion for common morphological patterns

The output format is identical to the Arabic dictionary (TRLD v1) so the
same Rust ContextDict reader handles both.

Usage:
    python scripts/build_persian_dict.py -o data/persian_dict.bin
    python scripts/build_persian_dict.py -o data/persian_dict.bin --stats
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Persian diacritic handling (same marks as Arabic)
# ---------------------------------------------------------------------------

PERSIAN_DIACRITICS = frozenset(
    "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0653\u0654\u0655\u0670"
)
TATWEEL = "\u0640"


def strip_diacritics(word: str) -> str:
    return "".join(c for c in word if c not in PERSIAN_DIACRITICS and c != TATWEEL)


# ---------------------------------------------------------------------------
# Core Persian vocabulary with diacritized forms
#
# This is the source of truth for Persian context-aware transliteration.
# Each entry maps a consonant skeleton to its diacritized form(s).
# The diacritized form uses Arabic tashkeel marks (fatha=a, kasra=e/i,
# damma=o/u, shadda=gemination, sukun=no vowel).
#
# Sources: Dehkhoda dictionary, Wiktionary Persian entries, common usage.
# Format: (unpointed_skeleton, diacritized_form, frequency_weight)
# ---------------------------------------------------------------------------

# Common Persian words with diacritics applied.
# Using actual Arabic diacritical marks for consistency with the transliteration engine.
# \u064e = fatha (a/æ), \u0650 = kasra (e/i), \u064f = damma (o/u)
# \u0651 = shadda (gemination), \u0652 = sukun (no vowel)

_FA = "\u064e"  # fatha → a
_KA = "\u0650"  # kasra → e (Persian) / i
_DA = "\u064f"  # damma → o (Persian) / u
_SH = "\u0651"  # shadda
_SU = "\u0652"  # sukun

PERSIAN_VOCAB: list[tuple[str, str, int]] = [
    # --- Greetings & common phrases ---
    ("سلام", f"س{_FA}لا{_SU}م", 10000),
    ("خداحافظ", f"خ{_DA}دا{_SU}حاف{_KA}ظ", 5000),
    # --- Pronouns ---
    ("من", f"م{_FA}ن", 50000),
    ("تو", f"ت{_DA}", 40000),
    ("او", f"ا{_DA}", 35000),
    ("ما", "ما", 30000),
    ("شما", f"ش{_DA}ما", 25000),
    # --- Common nouns ---
    ("کتاب", f"ک{_KA}تا{_SU}ب", 8000),
    ("خانه", f"خان{_KA}ه", 7000),
    ("آب", "آب", 9000),
    ("نان", "نان", 6000),
    ("مرد", f"م{_FA}ر{_SU}د", 7000),
    ("زن", f"ز{_FA}ن", 7000),
    ("بچه", f"ب{_FA}چ{_SH}{_KA}ه", 6000),
    ("شهر", f"ش{_FA}ه{_SU}ر", 5000),
    ("کشور", f"ک{_KA}ش{_SU}و{_FA}ر", 5000),
    ("زبان", f"ز{_FA}بان", 4000),
    ("دانشگاه", f"دان{_KA}ش{_SU}گاه", 3000),
    ("دانش", f"دان{_KA}ش", 3500),
    ("روز", f"ر{_DA}ز", 8000),
    ("شب", f"ش{_FA}ب", 7000),
    ("سال", "سال", 7000),
    ("ماه", "ماه", 6000),
    ("نام", "نام", 5000),
    ("کار", "کار", 7000),
    ("راه", "راه", 6000),
    ("دست", f"د{_FA}س{_SU}ت", 5000),
    ("سر", f"س{_FA}ر", 6000),
    ("چشم", f"چ{_FA}ش{_SU}م", 4000),
    ("دل", f"د{_KA}ل", 5000),
    # --- Places ---
    ("ایران", "ایران", 10000),
    ("تهران", f"ت{_KA}ه{_SU}ران", 8000),
    ("اصفهان", f"ا{_KA}ص{_SU}ف{_FA}هان", 4000),
    ("شیراز", "شیراز", 4000),
    # --- Adjectives ---
    ("بزرگ", f"ب{_DA}ز{_DA}ر{_SU}گ", 6000),
    ("کوچک", f"ک{_DA}چ{_FA}ک", 5000),
    ("خوب", f"خ{_DA}ب", 8000),
    ("بد", f"ب{_FA}د", 7000),
    ("زیبا", "زیبا", 4000),
    ("نو", f"ن{_DA}", 5000),
    # --- Verbs (infinitive stems) ---
    ("است", f"ا{_FA}س{_SU}ت", 50000),
    ("بود", f"ب{_DA}د", 20000),
    ("شد", f"ش{_DA}د", 15000),
    ("کرد", f"ک{_FA}ر{_SU}د", 12000),
    ("گفت", f"گ{_DA}ف{_SU}ت", 10000),
    ("رفت", f"ر{_FA}ف{_SU}ت", 8000),
    ("آمد", f"آم{_FA}د", 8000),
    ("داد", "داد", 7000),
    ("دید", "دید", 6000),
    ("خواست", f"خ{_SU}واس{_SU}ت", 5000),
    ("داشت", f"داش{_SU}ت", 8000),
    ("شده", f"ش{_DA}د{_KA}ه", 10000),
    ("کرده", f"ک{_FA}ر{_SU}د{_KA}ه", 8000),
    ("نوشت", f"ن{_KA}و{_KA}ش{_SU}ت", 3000),
    # --- Prepositions & particles ---
    ("در", f"د{_FA}ر", 40000),
    ("به", f"ب{_KA}ه", 35000),
    ("از", f"ا{_FA}ز", 30000),
    ("با", "با", 25000),
    ("برای", f"ب{_FA}رای", 15000),
    ("تا", "تا", 12000),
    ("که", f"ک{_KA}ه", 40000),
    ("این", "این", 30000),
    ("آن", "آن", 20000),
    ("هم", f"ه{_FA}م", 15000),
    ("یک", f"ی{_FA}ک", 12000),
    ("دو", f"د{_DA}", 10000),
    ("سه", f"س{_KA}ه", 8000),
    ("هر", f"ه{_FA}ر", 10000),
    ("چه", f"چ{_KA}ه", 8000),
    ("خود", f"خ{_DA}د", 12000),
    ("دیگر", f"دیگ{_FA}ر", 8000),
    # --- Islamic/Arabic loanwords common in Persian ---
    ("الله", f"ا{_FA}ل{_SH}اه", 5000),
    ("محمد", f"م{_DA}ح{_FA}م{_SH}{_FA}د", 4000),
    ("اسلام", f"ا{_KA}س{_SU}لام", 3000),
    ("قرآن", f"ق{_DA}ر{_SU}آن", 3000),
    # --- Food & daily life ---
    ("غذا", f"غ{_FA}ذا", 3000),
    ("چای", "چای", 3000),
    # --- Modern words ---
    ("دولت", f"د{_DA}ل{_FA}ت", 4000),
    ("مردم", f"م{_FA}ر{_SU}د{_DA}م", 5000),
    ("جهان", f"ج{_FA}هان", 3000),
    ("فارسی", f"فار{_SU}سی", 5000),
    ("عربی", f"ع{_FA}ر{_FA}بی", 3000),
]


# ---------------------------------------------------------------------------
# Dictionary compilation (same TRLD v1 format as Arabic)
# ---------------------------------------------------------------------------

MAGIC = b"TRLD"
VERSION = 1


def build_from_vocab(
    vocab: list[tuple[str, str, int]],
) -> tuple[dict[str, list[tuple[str, int]]], dict[tuple[str, str], str]]:
    """Build unigram table from curated vocabulary."""
    from collections import defaultdict

    unigrams: dict[str, list[tuple[str, int]]] = defaultdict(list)

    for skeleton, diacritized, freq in vocab:
        clean_skeleton = strip_diacritics(skeleton)
        unigrams[clean_skeleton].append((diacritized, freq))

    # Sort each entry by frequency descending
    for skeleton in unigrams:
        unigrams[skeleton].sort(key=lambda x: -x[1])

    # No bigrams for curated vocab (not enough context data)
    bigrams: dict[tuple[str, str], str] = {}

    return dict(unigrams), bigrams


def compile_dictionary(
    unigrams: dict[str, list[tuple[str, int]]],
    bigrams: dict[tuple[str, str], str],
    output_path: Path,
) -> None:
    """Compile to TRLD v1 binary format (identical to Arabic)."""
    buf = bytearray()
    buf.extend(MAGIC)
    buf.extend(struct.pack("<I", VERSION))
    buf.extend(struct.pack("<I", len(unigrams)))
    buf.extend(struct.pack("<I", len(bigrams)))
    unigram_offset_pos = len(buf)
    buf.extend(struct.pack("<I", 0))
    bigram_offset_pos = len(buf)
    buf.extend(struct.pack("<I", 0))

    struct.pack_into("<I", buf, unigram_offset_pos, len(buf))
    for skeleton in sorted(unigrams):
        forms = unigrams[skeleton]
        skel_bytes = skeleton.encode("utf-8")
        buf.extend(struct.pack("<H", len(skel_bytes)))
        buf.extend(skel_bytes)
        buf.extend(struct.pack("<H", len(forms)))
        for form, freq in forms:
            form_bytes = form.encode("utf-8")
            buf.extend(struct.pack("<H", len(form_bytes)))
            buf.extend(form_bytes)
            buf.extend(struct.pack("<I", freq))

    struct.pack_into("<I", buf, bigram_offset_pos, len(buf))
    # (no bigrams for curated vocab)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(bytes(buf))
    print(f"Written: {output_path} ({len(buf):,} bytes)", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Persian context dictionary from curated vocabulary"
    )
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output binary dict path")
    parser.add_argument("--stats", action="store_true", help="Print stats only")
    parser.add_argument("--json-stats", type=Path, default=None, help="Write stats to JSON")
    args = parser.parse_args()

    unigrams, bigrams = build_from_vocab(PERSIAN_VOCAB)

    print("\n--- Statistics ---", file=sys.stderr)
    print(f"Curated vocabulary entries: {len(PERSIAN_VOCAB)}", file=sys.stderr)
    print(f"Unique skeletons:          {len(unigrams)}", file=sys.stderr)
    print(f"Bigram entries:            {len(bigrams)}", file=sys.stderr)

    if args.json_stats:
        stats = {
            "vocab_entries": len(PERSIAN_VOCAB),
            "unique_skeletons": len(unigrams),
            "bigrams": len(bigrams),
        }
        args.json_stats.write_text(json.dumps(stats, indent=2))

    if args.stats:
        return

    compile_dictionary(unigrams, bigrams, args.output)


if __name__ == "__main__":
    main()
