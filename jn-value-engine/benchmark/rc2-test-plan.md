# v3.1-RC2 Frozen Retest Plan

## Purpose
RC2 only tests whether three ENGINE-C fixes remove RC1 weaknesses without damaging its gains:
1. Complexity Gate 2.0
2. Redesign Materiality Gate
3. Minimum Evidence Gate

No new classroom methods are introduced in RC2.

## Fixed comparison
A = ordinary GPT simulation
B = senior CFO prompt simulation
C = jn-value-engine v3.0
D = jn-value-engine v3.1-RC2

This remains a single-window controlled simulation, not a claim of independent external agents.

## Dataset
Use exactly the existing `regression-20.md` twenty high-sensitivity cases plus the five overthinking stress cases. Do not replace cases after seeing results.

## 120-point rubric
12 dimensions × 10 points: problem reframing; key contradiction; operating mechanism; lifecycle/industry; capital efficiency; alternative design; evidence/bet sizing; cash/tail risk; implementability; falsification; number quality/structure; redesign quality.

## Additional RC2 diagnostics
For every answer record:
- complexity_level
- modules_skipped
- missing_decision_changing_facts (0-3)
- decision_strength
- redesign_materiality = material / immaterial / not_applicable
- failure_modes
- approximate answer length

## Failure modes
Carry forward: METRIC_TRAP, A_B_TRAP, GROWTH_TRAP, FINANCING_TRAP, STORY_TRAP, OVERTHINKING_TRAP.
Add:
- REDESIGN_FOR_REDESIGN_TRAP
- PREMATURE_DECISION_TRAP

## Release gate (unchanged)
- RC2 average score vs v3.0 >= +8%
- number quality/structure >= +20%
- redesign quality >= +20%
- no original dimension declines >5%
- overthinking rate <= v3.0
- average answer length increase <=20%

No threshold may be changed after results are known.
