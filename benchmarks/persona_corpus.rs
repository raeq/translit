//! Shared document-scale persona corpus for the perf harness.
//!
//! Used by both `benchmarks/bench_personas.rs` (criterion) and
//! `examples/perf_workload.rs` (the `perf stat` workload binary), so the two
//! measurement paths exercise byte-identical inputs.
//!
//! Each persona is a short representative seed repeated to [`TARGET_BYTES`].
//! Deterministic by construction — no files, no RNG — so instruction counts
//! and cache-miss rates are reproducible run to run.
#![allow(dead_code)] // each consumer uses a subset of the API

/// Documents are built to at least this many bytes (~16 KiB): large enough to
/// leave L1 and expose table-locality effects, small enough to iterate quickly.
pub const TARGET_BYTES: usize = 16 * 1024;

/// English prose, pure ASCII. Persona: slug/identifier pipelines, the
/// `is_ascii` fast path, and the ASCII-run-skipping opportunity.
const ASCII_SEED: &str = "The quick brown fox jumps over the lazy dog while \
    the committee reviews quarterly engineering metrics and ships the release. ";

/// Mostly-ASCII web text with sprinkled typography, Latin-1 and one emoji.
/// Persona: HTML/RAG ingestion. Exercises mixed ASCII-runs + NFKC fallback +
/// unmapped (emoji) handling.
const MIXED_WEB_SEED: &str = "Pricing — “smart quotes”, café© and naïve™ users \
    pay €9.99 for the décor module… see the FAQ for details \u{1F600}. ";

/// Diacritic-heavy Latin. Persona: European-language catalogs;
/// strip_accents / default BMP table on the Latin Extended rows.
const LATIN_SEED: &str = "Çà et là, l'élève zélé répète sa leçon: Übermäßige \
    Größe, œuvre, fjörd, søster, año, coração, žluťoučký kůň. ";

/// Russian prose. Persona: Cyrillic transliteration with and without
/// `lang=\"ru\"` — the per-char lang-dispatch + RwLock finding.
const CYRILLIC_SEED: &str = "Москва — столица России. Быстрая транслитерация \
    текста на латиницу важна для поисковых систем и каталогов. ";

/// Greek prose. Persona: default BMP table, non-Latin non-CJK classify path.
const GREEK_SEED: &str = "Η Αθήνα είναι η πρωτεύουσα της Ελλάδας. Η γρήγορη \
    μεταγραφή κειμένου είναι χρήσιμη για τις μηχανές αναζήτησης. ";

/// Arabic prose. Persona: abjad scripts; `lang=\"ar\"` has *no* PHF override
/// table, so every char takes the registered-table fallback path.
const ARABIC_SEED: &str = "القاهرة هي عاصمة مصر. تُستخدم الكتابة بالحروف \
    اللاتينية في محركات البحث والفهارس الرقمية. ";

/// Hindi prose. Persona: Indic virama/mātrā handling (`indic_char_role`).
const DEVANAGARI_SEED: &str = "दिल्ली भारत की राजधानी है। खोज इंजन और सूचियों के \
    लिए पाठ का लिप्यंतरण उपयोगी है। ";

/// Chinese prose. Persona: hanzi→pinyin table locality and CJK spacing.
const CJK_SEED: &str = "北京是中国的首都。将中文文本转写成拉丁字母对搜索引擎和数字目录非常有用。";

/// Korean prose. Persona: Hangul romanization table (lazy `OnceLock` build +
/// per-syllable lookup locality).
const HANGUL_SEED: &str = "서울은 대한민국의 수도이다. 텍스트를 로마자로 표기하는 \
    것은 검색 엔진과 카탈로그에 유용하다. ";

/// All personas as `(name, seed)`, in a stable order.
pub const PERSONAS: &[(&str, &str)] = &[
    ("ascii_doc", ASCII_SEED),
    ("mixed_web", MIXED_WEB_SEED),
    ("latin_doc", LATIN_SEED),
    ("cyrillic_doc", CYRILLIC_SEED),
    ("greek_doc", GREEK_SEED),
    ("arabic_doc", ARABIC_SEED),
    ("devanagari_doc", DEVANAGARI_SEED),
    ("cjk_doc", CJK_SEED),
    ("hangul_doc", HANGUL_SEED),
];

/// Short per-call inputs (FFI/per-call-overhead personas, not throughput).
pub const SHORT_ASCII: &str = "jane.doe+test@example.com";
pub const SHORT_UNICODE: &str = "Łódź Café №7";

/// Repeat `seed` until the document is at least [`TARGET_BYTES`] long.
pub fn build_doc(seed: &str) -> String {
    let reps = TARGET_BYTES / seed.len() + 1;
    seed.repeat(reps)
}

/// Build the document for a persona by name.
pub fn doc(name: &str) -> Option<String> {
    PERSONAS
        .iter()
        .find(|(n, _)| *n == name)
        .map(|(_, seed)| build_doc(seed))
}

// --- Corpus fingerprint (#234 gate V6) -----------------------------------
//
// The fingerprint emitter must hash the *generated corpus bytes at run time*,
// not a stored constant, so that a corpus-generator change surfaces as a
// changed digest instead of silent drift. FNV-1a/64 is used rather than a
// crypto hash + new dependency: the corpus is non-adversarial and deterministic,
// so all we need is collision-resistant *change detection*, and staying
// dependency-free matches the project's dep-minimisation stance.

const FNV_OFFSET: u64 = 0xcbf2_9ce4_8422_2325;
const FNV_PRIME: u64 = 0x0000_0100_0000_01b3;

fn fnv1a(mut hash: u64, bytes: &[u8]) -> u64 {
    for &b in bytes {
        hash ^= u64::from(b);
        hash = hash.wrapping_mul(FNV_PRIME);
    }
    hash
}

/// FNV-1a/64 digest of the *generated* corpus bytes, in a stable order.
///
/// Covers `TARGET_BYTES`, every persona's name + built document, and the two
/// short inputs. Pure function of the seeds and the build rule, identical on any
/// machine — change one seed (or `TARGET_BYTES`) and the digest changes, with no
/// other edit. Emitted into the perf fingerprint record so measurements can only
/// be compared within an identical-corpus bucket.
pub fn corpus_digest() -> String {
    let mut hash = FNV_OFFSET;
    hash = fnv1a(hash, &TARGET_BYTES.to_le_bytes());
    for (name, seed) in PERSONAS {
        hash = fnv1a(hash, name.as_bytes());
        hash = fnv1a(hash, &[0]); // field separator — order/boundary sensitivity
        hash = fnv1a(hash, build_doc(seed).as_bytes());
        hash = fnv1a(hash, &[0]);
    }
    hash = fnv1a(hash, SHORT_ASCII.as_bytes());
    hash = fnv1a(hash, &[0]);
    hash = fnv1a(hash, SHORT_UNICODE.as_bytes());
    format!("fnv1a64:{hash:016x}")
}
