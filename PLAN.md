# Decomposition as an operator — plan (OPEN-QUESTIONS #1), fixed 2026-10-09, NOT started

Status: **run 2026-10-09/10, $5.07 + $0.63 pilot; see RESULTS.md.** Verdict: H0 holds on true-hard numeric items (0 of 7 zero-items, Δ pass@4 0.00); gains only where the single model hits the cap (budget) or on GPQA at chance (guessing); decomposition hurts DeepSeek on medium/easy (−0.41); team ≤ split.

## Why
The last operator untested by the notes: splitting a task into parts solved
separately (within one model, or across agents). Literature: decomposition
across agents either loses (CooperBench coop −41% of solo; Interaction Tax
HPE the worst arm at matched budget) or its gain is confounded with extra
tools and calls (CodeR, Conductor). Nobody has identical tasks, matched
budget, per-task results. On the SWE-bench matrix, decomposed systems
(MASAI, Composio, Aime, Agentless, AutoCodeRover) fail on the same bugs as
free agents on the same model (φ 0.42–0.67; `axis-F-swebench/decomposition-cut.md`).

## Hypothesis
H0: at equal token budget, decomposition solves nothing a single pass does
not solve within the same number of attempts; it moves mass, not support.
H1: there are tasks the model never solves whole (0/16) that it solves in
parts, because the failure is horizon, not a missing move.

## Arms (same total token cap per task)
1. Single pass — already in corpus (`corpus-traces/raw/<model>/samples-<layer>.jsonl`, 16 draws).
2. Same model, decomposed: plan call (subtasks only) → one call per subtask
   (sees problem + prior subtask answers) → assembly call.
3. Across agents: same as 2, subtasks handed to other models of the seven
   (uncapped ones only), assembly by the base model.
Control: best-of-n of arm 1 at equal cost — already in corpus (16 draws).

## Items (difficulty from the existing 16 draws; filter through
`corpus-traces/data/label-audit.json` first — pre-audit, 4 of DeepSeek's 7
olympiad 0/16 were label errors)
Base models: z-ai/glm-5.3-flash (more hard mass, cheap) and deepseek-v3.2.
| stratum | rule | GLM | DeepSeek |
|---|---|---|---|
| hard | ≤4/16 | all (~43: oly 21, gpqa 16, gsm-hard 6) | all (~20 after audit) |
| medium | 5–13/16 | 12 sampled | 12 sampled |
| easy | ≥14/16 | 6 (sanity) | 6 (sanity) |
≈100 items. Arms 2 and 3 once each on every item; 3 more repeats of arms 2
and 3 on the hard stratum so decomposition pass@4 can be set against the
single model's pass@4 and pass@16.

## Predictions (write into PREREG.md unchanged before running)
- Hard stratum (single p ≤ 0.25, mean ≈ 0.1): under H0 one decomposition
  solves ≈ 10 %, and 0 of the audited 0/16 items.
- Signal for H1: ≥ 3 audited 0/16 items solved by arm 2 or 3, or hard-stratum
  solve rate ≥ 0.30 with a bootstrap interval excluding the H0 expectation.
- Medium: decomposition pass@1 vs single pass@1 answers efficiency, not
  coverage; expect within ±5.
- Easy: decomposition loses ≤ 1–2 of 6 (assembly errors).
- Arm 3 ≤ arm 2 (hand-off loss); if arm 2 > arm 1 but arm 3 = arm 2, the
  operator is "split", not "team".
- If it helps GLM and not DeepSeek: decomposition compensates weakness
  (a boundary of the thesis, not an exception). Helps both on 0/16: real
  exception.

## Cost
Arms 2+3 once, ~100 items: ~200 runs × 6–10k tokens ≈ 1.5–2 M tokens, 3–6 $.
Hard-stratum repeats: ~360 runs, 3–4 M tokens, 5–10 $. Grader local
(corpus-traces/grader.py), 0 $. Upper bound ≈ 20 $. Arm 1 and best-of-16: 0 $.

## Deliverable
RESULTS.md with the three-stratum table per base model; a paragraph or a
section in note 8 ("Agents with Tools Fail Together") or, if H1, a note of
its own.

## Follow-up, not planned (low priority, 2026-10-10)

**Arm 4: expensive planner over cheap workers.** The arrangement people sell
as an orchestrator, which arm 3 did not test (its workers were dearer than
the base). Planner and assembler DeepSeek v3.2; workers GLM-5.3-flash plus
one more cheap model (qwen/qwen3.7-plus is cheaper than DeepSeek; the free
qwen3.8-27b / gemma-4-31b endpoints are unstable). Items: the same 38
DeepSeek items (20 hard, 12 medium, 6 easy), hard ones ×4, ≈100 runs.
Compare at equal dollars against DeepSeek whole (16 draws in the corpus),
against arm 2 (DeepSeek splitting its own work) and against GLM whole.
Hypothesis of the cheap scheme: not worse than DeepSeek whole for less
money. Prediction from what is already seen: GLM overruns subtasks less
than DeepSeek, so arm 4 may be cheaper than arm 2 and no worse, but it
will not solve the numeric hard items, which neither DeepSeek whole nor
GLM solves. Work: `arm4` in run.py (planner=base, workers=cheap list), a
half-page PREREG, about an hour of runs, 1–3 $, one paragraph in the note.
