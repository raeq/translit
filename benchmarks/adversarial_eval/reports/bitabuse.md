# Adversarial-text robustness — bitabuse

_translit 0.6.3; `strip_obfuscation`. Numbers reflect the current version and may differ from the historical baseline in the README as coverage grows._

- rows evaluated: **325580**
- perturbation-bearing rows (contain non-ASCII): **99.9%** (325361/325580)
- non-ASCII codepoints folded by `strip_obfuscation`: **77.1%** (3709425/4811752)

## Recovery (clean ground truth available)

- XMR (exact-match recovery, `P(perturbed) == P(clean)`): **5.8%**
- line-exact recovery (`P(perturbed) == clean`): **5.6%**
- word-level recovery: **64.1%**

## Miss-mining (non-ASCII codepoints surviving the defense)

- **principled** (in UTS#39, addressable — feed to #40): **56** distinct, 119060 occurrences
- **novel** (not in UTS#39, out of scope): **299** distinct, 870030 occurrences

Top principled (addressable) misses:

| codepoint | char | occurrences |
|---|---|---|
| U+0437 | `з` | 24813 |
| U+050D | `ԍ` | 24488 |
| U+043F | `п` | 13333 |
| U+0499 | `ҙ` | 12386 |
| U+0432 | `в` | 11996 |
| U+03C4 | `τ` | 6806 |
| U+00E6 | `æ` | 6235 |
| U+0375 | `͵` | 1942 |
| U+1D28 | `ᴨ` | 1941 |
| U+0223 | `ȣ` | 1885 |
| U+1D0D | `ᴍ` | 1674 |
| U+04A3 | `ң` | 1137 |
| U+01BB | `ƻ` | 1002 |
| U+01A7 | `Ƨ` | 824 |
| U+066C | `٬` | 819 |

> Guardrail: these are **observations**, not optimization targets. Principled misses are candidates to verify and upstream via #40 — never silent table edits.
