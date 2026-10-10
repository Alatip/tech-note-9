# tech-note-9 — Decomposition Buys Budget at Best, Nothing Usually

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23273230.svg)](https://doi.org/10.5281/zenodo.23273230) — the note.

Companion runs and code for the technical note **"Decomposition Buys Budget at Best, Nothing Usually"**
(alatip.github.io/decomposition-buys-budget/): a task cut into 2–4 subtasks and solved one at a time,
by the same model (arm 2) or with the subtasks handed to three other models (arm 3), at the same 8,192-token
budget as one whole attempt, on 97 problems chosen by how often each base model (GLM-5.3-flash, DeepSeek v3.2)
already solved them in sixteen whole attempts. 560 runs, 9–10 October 2026, $5.07 nominal on OpenRouter,
plus a 186-run pilot under the first protocol ($0.66) kept separately.

Order of reading:

1. `PREREG.md` — predictions written before the run, and the two protocol revisions made before the main
   run (reasoning bound per call; planning prompt), each with its reason.
2. `PLAN.md` — the design as agreed, and the follow-up not run (expensive planner over cheap workers).
3. `selection.json` — the 97 items: `[base, layer, id, stratum, correct-of-16, truncated-of-16]`.
4. `runs.jsonl` — one record per decomposition attempt (see Data).
5. `stats.py` → `STATS.md` — the tables; `RESULTS.md` — the findings, the review corrections of 10 October,
   the dollar comparison and the truncation gradient.

## Data

`runs.jsonl` (560 records, main run, protocol v2): `base`, `arm` (arm2 = same model solves the parts;
arm3 = Qwen 3.7 plus / Mistral Large 2512 / Kimi K2.5 solve the parts, round-robin, with a recorded
substitution to the next worker after a 429), `rep` (0–3), `id`, `dataset`, `gold`, `plan` (the subtask list),
`sub_results`, `asm_text` (tail of the assembly reply), `answer`, `correct`, `graded`, `cost` (USD, OpenRouter
ledger), `tokens` (completion tokens over all calls), `calls` (per call: step, finish reason, output tokens,
worker, substituted). `runs-wave1-protocol1.jsonl` (186) and `runs-aborted-reasoning-bug.jsonl` (14) are the
pilot and the aborted first start; they are not pooled into any table.

**GPQA Diamond** records (200 of 560) carry no plan, subtask or assembly text, and their `gold` and `answer`
are per-item random tokens (equal when the answer was right), per the dataset's terms; `gpqa_redacted: true`
marks them. Every statistic in the note is reproducible from the `correct` field. AIME 2024/2025 and
GSM-Hard records are complete.

The single-model side (arm 1, best-of-k: 16 draws per item at T = 1) is the corpus of
[tech-note-5](https://github.com/Alatip/tech-note-5) (`raw/<model>/samples-<layer>.jsonl`, `label-audit.json`).

## Run

```
TECH_NOTE_5=/path/to/tech-note-5 python3 stats.py     # writes STATS.md; standard library only
```

`run.py` is the runner as used (OpenRouter through the collection repository's `lbd.cloud` client and the
`corpus-traces/run.py` grader of tech-note-5); it is kept for the protocol, not as a turnkey script.

## License

CC BY 4.0 (see `LICENSE`). Cite the note as: Latipov, A. (2026). *Decomposition Buys Budget at Best,
Nothing Usually*. Zenodo. https://doi.org/10.5281/zenodo.23273230
