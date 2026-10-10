"""Decomposition arms. Usage: .venv/bin/python experiments/decomposition/run.py [--repeats N] [--workers W]"""
import json, re, sys, time, threading, argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE = Path(__file__).resolve().parent; CT = HERE.parent / "corpus-traces"
sys.path.insert(0, str(HERE.parent.parent)); sys.path.insert(0, str(CT))
from lbd import cloud
import importlib.util
spec = importlib.util.spec_from_file_location("ctrun", CT / "run.py"); ctrun = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctrun)
grade, parse_final = ctrun.grade, ctrun.parse_final

BASES = {"z-ai_glm-5.3-flash": "z-ai/glm-5.3-flash", "deepseek_deepseek-v3.2": "deepseek/deepseek-v3.2"}
WORKERS = ["qwen/qwen3.7-plus", "mistralai/mistral-large-2512", "moonshotai/kimi-k2.5"]
TOTAL, PLAN_MAX, SUB_POOL, ASM_MAX = 8192, 1024, 5120, 2048
PLAN_SYS = "You are planning, not solving. Break the problem into 2 to 4 ordered subtasks such that solving them in order gives the final answer. Do not solve anything. Output the JSON array of strings first, with no text before it."
SUB_SYS = "Solve only the subtask you are given, using the problem statement and the results of earlier subtasks. Be concise. End with a line: RESULT: <result of this subtask>"
ASM_SYS = "Combine the subtask results into the final answer to the original problem. Do not re-solve from scratch. Give the final answer on the last line exactly as: FINAL: <answer>"
OUT = HERE / "runs.jsonl"; lock = threading.Lock()

def items():
    aud = json.load(open(CT / "data/label-audit.json")); rel = aud["relabels"]
    it = {}
    for name in ("items.jsonl", "items-gpqa.jsonl"):
        for l in open(CT / "data" / name):
            if l.strip():
                r = json.loads(l); r["dataset"] = r["layer"]
                if r["id"] in rel: r["gold"] = rel[r["id"]]["new"]
                it[r["id"]] = r
    return it

def call(model, sys_, user, max_tokens, label, reasoning_max=None):
    # reasoning bounded to half the call budget (or an explicit cap) so the visible text is never empty
    r = cloud.chat(model, [{"role": "system", "content": sys_}, {"role": "user", "content": user}], temperature=1.0,
                   max_tokens=max_tokens, label=label, reasoning=True, reasoning_max=(max_tokens // 2 if reasoning_max is None else reasoning_max), provider={"sort": "throughput", "allow_fallbacks": True})
    return {"text": r["text"] or (r.get("reasoning") or "")[-1500:], "finish": r["finish"], "cost": r["cost_usd"], "served": r["model"],
            "out": (r.get("usage") or {}).get("completion_tokens")}

def parse_plan(text):
    m = re.search(r"\[.*\]", text, re.S)
    if not m: return None
    try:
        arr = json.loads(m.group(0))
        flat = []
        for x in arr:  # models sometimes emit [{"1": "..."}] or [{"subtask": "..."}]
            if isinstance(x, dict): flat += [str(v) for v in x.values()]
            else: flat.append(str(x))
        arr = [x.strip() for x in flat if x.strip()]
        return arr[:4] if 2 <= len(arr) else None
    except Exception:
        pass
    # malformed JSON: take the quoted strings of at least 20 characters, in order
    strs = [x for x in re.findall(r'"((?:[^"\\]|\\.){20,}?)"', text) if not x.lower().startswith("subtask")]
    strs = [x.strip() for x in strs if x.strip()]
    return strs[:4] if 2 <= len(strs) else None

def one(job):
    base_slug, item, arm, rep = job; base = BASES[base_slug]
    lab = f"decomp:{arm}:{base_slug}:{item['id']}:{rep}"
    calls, cost, spent = [], 0.0, 0
    plan_user = ("Do NOT solve the problem. Reply with ONLY a JSON array of 2 to 4 short strings (one per subtask, at most 40 words each), nothing else.\n\nPROBLEM (for planning only):\n" + item["prompt"] + "\n\nJSON array of subtasks:")
    plan = None
    for attempt in range(2):  # one retry if the first reply is not a parseable plan; both count against the 8,192 budget
        p = call(base, PLAN_SYS, plan_user, PLAN_MAX, lab + f":plan{attempt}", reasoning_max=64)
        calls.append({"step": "plan" if attempt == 0 else "plan-retry", **{k: p[k] for k in ("finish", "served", "out")}}); cost += p["cost"] or 0; spent += p["out"] or 0
        plan = parse_plan(p["text"])
        if plan: break
    rec = {"base": base_slug, "arm": arm, "rep": rep, "id": item["id"], "dataset": item["dataset"], "gold": item["gold"], "plan": plan, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if not plan:
        rec.update(answer="", correct=False, fail="plan", cost=cost, tokens=spent, calls=calls, plan_text=p["text"][:800]); return rec
    n = len(plan); per = max(512, (TOTAL - ASM_MAX - spent) // n); results = []
    for i, st in enumerate(plan):
        worker = base if arm == "arm2" else WORKERS[i % len(WORKERS)]
        ctx = "\n".join(f"Subtask {j+1}: {plan[j]}\nResult {j+1}: {results[j]}" for j in range(i))
        user = f"PROBLEM:\n{item['prompt']}\n\nSUBTASKS:\n" + "\n".join(f"{j+1}. {s}" for j, s in enumerate(plan)) + (f"\n\nEARLIER RESULTS:\n{ctx}" if ctx else "") + f"\n\nYOUR SUBTASK: {i+1}. {st}"
        used = worker
        try:
            r = call(worker, SUB_SYS, user, per, lab + f":sub{i+1}")
        except Exception as e:  # 429 / provider down: retry once, then hand the subtask to the next worker (recorded)
            if "429" not in str(e) and "rate" not in str(e).lower(): raise
            time.sleep(20)
            try: r = call(worker, SUB_SYS, user, per, lab + f":sub{i+1}")
            except Exception:
                used = WORKERS[(i + 1) % len(WORKERS)] if arm == "arm3" else base
                r = call(used, SUB_SYS, user, per, lab + f":sub{i+1}:subst")
        cost += r["cost"] or 0; spent += r["out"] or 0
        calls.append({"step": f"sub{i+1}", "worker": used, "substituted": used != worker, **{k: r[k] for k in ("finish", "served", "out")}})
        m = re.findall(r"RESULT:\s*(.+)", r["text"]); results.append((m[-1].strip() if m else r["text"][-600:]).strip())
    user = f"PROBLEM:\n{item['prompt']}\n\n" + "\n".join(f"Subtask {j+1}: {plan[j]}\nResult {j+1}: {results[j]}" for j in range(n))
    a = call(base, ASM_SYS, user, ASM_MAX, lab + ":asm"); cost += a["cost"] or 0; spent += a["out"] or 0
    calls.append({"step": "asm", **{k: a[k] for k in ("finish", "served", "out")}})
    ans = parse_final(a["text"]); c = grade(item, ans)
    rec.update(answer=ans, correct=bool(c), graded=c, sub_results=results, asm_text=a["text"][-600:], cost=cost, tokens=spent, calls=calls)
    return rec

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--repeats", type=int, default=4); ap.add_argument("--workers", type=int, default=4); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    it = items(); sel = json.load(open(HERE / "selection.json"))
    done = set()
    if OUT.exists():
        for l in open(OUT):
            if l.strip(): r = json.loads(l); done.add((r["base"], r["arm"], r["id"], r["rep"]))
    jobs = []
    for base_slug, layer, iid, stratum, c, tr in sel:
        reps = a.repeats if stratum == "hard" else 1
        for rep in range(reps):
            for arm in ("arm2", "arm3"):
                if (base_slug, arm, iid, rep) not in done: jobs.append((base_slug, it[iid], arm, rep))
    jobs.sort(key=lambda j: j[3])  # all repeat-0 first
    print(f"{len(jobs)} jobs ({len(done)} done)", flush=True)
    if a.dry: return
    stats = {"ok": 0, "fail": 0, "correct": 0, "cost": 0.0}
    def work(job):
        try:
            rec = one(job)
            with lock:
                with OUT.open("a") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                stats["ok"] += 1; stats["correct"] += rec["correct"]; stats["cost"] += rec["cost"]
                if stats["ok"] % 20 == 0: print(f"  {stats['ok']} done, acc {stats['correct']/stats['ok']:.2f}, ${stats['cost']:.2f}", flush=True)
        except cloud.CloudCapReached as e:
            print("CAP:", e, flush=True); raise
        except Exception as e:
            with lock: stats["fail"] += 1
            print(f"  fail {job[1]['id']} {job[2]} r{job[3]}: {str(e)[:160]}", flush=True)
    with ThreadPoolExecutor(a.workers) as ex: list(ex.map(work, jobs))
    print(f"ok {stats['ok']} fail {stats['fail']} acc {stats['correct']/max(1,stats['ok']):.2f} cost ${stats['cost']:.2f}", flush=True)

if __name__ == "__main__": main()
