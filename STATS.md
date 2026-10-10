# stats (generated)

runs 560; plan failures 62; cost $5.07; mean tokens 3932

| base | stratum | n | single p@1 | single p@4 | single p@16 | arm2 p@1 | arm3 p@1 | arm2 p@4 | arm3 p@4 | arm2∪arm3 @4 | 0/16 items | 0/16 solved by any decomp | union(single16 ∪ decomp) − single16 | Δ arm2 p@1 − single p@1 [CI] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| glm-5.3- | hard-true | 3 | 0.04 | 0.00 | 0.67 | 0.33 | 0.00 | 0.33 | 0.67 | 0.67 | 1 | 1 ['gsmhard:11771746'] | +0.33 | +0.29 [-0.06,+1.00] |
| glm-5.3- | hard-cap | 38 | 0.10 | 0.37 | 0.58 | 0.45 | 0.42 | 0.71 | 0.66 | 0.82 | 16 | 10 ['aime25:29', 'gpqa:12', 'gpqa:18', 'gpqa:30', 'gpqa:32', 'gpqa:45', 'gpqa:47', 'gpqa:48', 'gpqa:55', 'gsmhard:4218257'] | +0.26 | +0.35 [+0.20,+0.50] |
| glm-5.3- | medium | 12 | 0.67 | 1.00 | 1.00 | 0.75 | 0.75 | 0.75 | 0.75 | 0.83 | 0 | 0  | +0.00 | +0.08 [-0.20,+0.33] |
| glm-5.3- | easy | 6 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0 | 0  | +0.00 | +0.00 [+0.00,+0.00] |
| deepseek | hard-true | 20 | 0.05 | 0.15 | 0.40 | 0.20 | 0.15 | 0.35 | 0.20 | 0.35 | 12 | 3 ['gpqa:18', 'gpqa:32', 'gpqa:57'] | +0.15 | +0.15 [+0.00,+0.33] |
| deepseek | medium | 12 | 0.62 | 1.00 | 1.00 | 0.25 | 0.25 | 0.25 | 0.25 | 0.42 | 0 | 0  | +0.00 | -0.37 [-0.57,-0.16] |
| deepseek | easy | 6 | 0.99 | 1.00 | 1.00 | 0.50 | 0.67 | 0.50 | 0.67 | 0.67 | 0 | 0  | +0.00 | -0.49 [-0.83,-0.16] |

z-ai_glm-5.3-flash: n=59 φ(arm2,single0)=0.58 φ(arm3,single0)=0.43 φ(arm2,arm3)=0.46 φ(single0,single1)=0.53
deepseek_deepseek-v3.2: n=38 φ(arm2,single0)=0.22 φ(arm3,single0)=0.22 φ(arm2,arm3)=0.46 φ(single0,single1)=0.68

z-ai_glm-5.3-flash arm2: runs 182, plan fail 0, asm truncated 23, any subtask truncated 63, mean tokens 2631, mean subtasks 3.6
z-ai_glm-5.3-flash arm3: runs 182, plan fail 0, asm truncated 30, any subtask truncated 132, mean tokens 4487, mean subtasks 3.6
deepseek_deepseek-v3.2 arm2: runs 98, plan fail 35, asm truncated 36, any subtask truncated 57, mean tokens 4707, mean subtasks 2.5
deepseek_deepseek-v3.2 arm3: runs 98, plan fail 27, asm truncated 48, any subtask truncated 47, mean tokens 4542, mean subtasks 2.8