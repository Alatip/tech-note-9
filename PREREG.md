# Pre-registration — decomposition as an operator (2026-10-09, before any call)

Design per PLAN.md, refined after the item selection (selection.json) and
BEFORE any model call (2026-10-09).

## Items (97)
From the audited 16-draw resamples (corpus-traces, relabels applied,
excluded items dropped; truncated draws count as wrong, as in the corpus):
GLM-5.3-flash: hard 41 (olympiad 21, GPQA 16, GSM-Hard 4), medium 12, easy 6.
DeepSeek v3.2: hard 20 (olympiad 10, GPQA 6, GSM-Hard 4), medium 12, easy 6.
Medium/easy sampled with seed 20261009.

**Sub-strata found at selection, fixed here:** 38 of GLM's 41 hard items
have ≥ 8 of 16 draws cut by the 8,192-token cap (hard-cap); DeepSeek's
20 hard items have no such truncation (hard-true). GLM's hard stratum
therefore tests "the model runs out of tokens", DeepSeek's "the model
cannot". Both are reported separately.

## Budget rule
Every arm gets the same total completion budget as one corpus draw:
8,192 tokens across all calls (plan ≤ 1,024; subtasks share 5,120, split
equally over n ≤ 4; assembly ≤ 2,048; the plan cap was 768 / pool 5,376 in
the first 13 records, moved after GLM's verbose plans still hit 768). Reasoning tokens count and are bounded to half of each call's budget
(added after an aborted first start, 8 records, in which GLM spent every
call's cap on hidden reasoning and emitted no text; those records are kept
in runs-aborted-reasoning-bug.jsonl and not used). T = 1.

## Arms
2. Same model decomposed: plan (2–4 ordered subtasks, no solving) → one call
   per subtask (sees problem, subtask list, earlier results) → assembly
   (FINAL: line). Base model does every call.
3. Across agents: identical, but subtask i goes to worker i mod 3 from
   [qwen/qwen3.7-plus, mistralai/mistral-large-2512, moonshotai/kimi-k2.5];
   plan and assembly by the base model.
Arm 1 and best-of-k: the existing 16 draws.
Repeats: arms 2 and 3 once on all 97 items; three more repeats on the 61
hard items (pass@4 of decomposition vs pass@4 / pass@16 of the single model).

## Statistics
Per base model and stratum: single pass@1 (mean of 16), pass@4, pass@16;
decomposition pass@1 (repeat 0) and pass@4 (hard); items solved by
decomposition that the single model solved 0/16; φ between decomposition
repeat 0 and single draw 0; union(single@16 ∪ decomp@4) vs single@16.
Bootstrap over items for the differences. Assembly failures (no FINAL)
counted as wrong; plan-parse failures logged and counted as wrong.

## Predictions
- hard-true (DeepSeek, 20 items, single mean p ≈ 0.08): arm 2 pass@1 ≤ 0.15,
  arm 3 ≤ arm 2; 0/16 items solved by any decomposition repeat: 0–1 of 12.
  H1 signal: ≥ 3 of the 12 audited 0/16 items solved, or decomposition
  pass@4 ≥ 0.35 with the bootstrap interval excluding single pass@4.
- hard-cap (GLM, 38 items): decomposition will solve more than single
  pass@1 (0.1) — predicted 0.2–0.4 — because shorter calls fit the cap.
  That is a budget-allocation result, not new coverage; the comparator
  there is single pass@4 (≈ 0.25). Signal of something more: decomposition
  pass@1 above single pass@4.
- medium: decomposition pass@1 within ±0.10 of single pass@1.
- easy: decomposition loses ≤ 2 of 6 per model.
- arm 3 ≤ arm 2 everywhere (hand-off loss).
- φ(decomp, single draw 0) 0.3–0.6.
- If arm 2 > arm 1 but arm 3 ≈ arm 2: the operator is "split", not "team".

## Cost cap
LBD_CLOUD_CAP = 25 USD; expected 8–15.

## Protocol revision v2 (2026-10-09, after the first wave, before any repeat)
Wave 1 under protocol v1 (194 jobs, runs-wave1-protocol1.jsonl, $0.63) showed
both base models solving inside the "plan" call and hitting its cap (DeepSeek
49 of 52 plan failures by length; GLM 18 of 31), so the arm measured prompt
compliance, not decomposition. Changes, applied to every job and re-run from
zero: the no-solving instruction is repeated in the user turn with the
problem marked "for planning only"; the plan call runs with reasoning capped
at 64 tokens; one plan retry is allowed, and both plan calls count against
the 8,192 total (the subtask pool is what remains after planning and the
2,048 assembly reserve, at least 512 per subtask); the parser accepts
malformed JSON by taking the quoted strings. Plan failures that survive this
still count as wrong. Predictions unchanged. Wave-1 numbers are reported in
RESULTS.md as a pilot, not pooled.
