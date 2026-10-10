import json,collections,random,statistics as st,math,sys
import os
CT=os.environ.get('TECH_NOTE_5', '../corpus-traces')  # path to a tech-note-5 checkout (raw/<model>/samples-<layer>.jsonl, data/label-audit.json)
_la=CT+'/data/label-audit.json' if os.path.exists(CT+'/data/label-audit.json') else CT+'/label-audit.json'
aud=json.load(open(_la)); rel=aud['relabels']
sel=json.load(open('selection.json'))  # [base, layer, id, stratum, correct16, trunc16]
meta={(b,i):(l,s,c,t) for b,l,i,s,c,t in sel}
single={}
for b in ('z-ai_glm-5.3-flash','deepseek_deepseek-v3.2'):
    for l in ('olympiad','gpqa-diamond','gsm-hard'):
        per=collections.defaultdict(list)
        for line in open(f'{CT}/raw/{b}/samples-{l}.jsonl'):
            if not line.strip(): continue
            r=json.loads(line)
            if (b,r['id']) not in meta: continue
            ok=r['correct']
            if r['id'] in rel: ok=(str(r['answer']).strip()==str(rel[r['id']]['new']).strip())
            per[r['id']].append(1 if ok else 0)
        for i,v in per.items(): single[(b,i)]=v[:16]
runs=[json.loads(l) for l in open('runs.jsonl') if l.strip()]
D=collections.defaultdict(dict)  # (base,arm,id) -> rep -> correct
for r in runs: D[(r['base'],r['arm'],r['id'])][r['rep']]=int(r['correct'])
def substratum(b,i):
    l,s,c,t=meta[(b,i)]
    if s!='hard': return s
    return 'hard-cap' if t>=8 else 'hard-true'
def boot_diff(xs,ys,B=2000,seed=0):
    rnd=random.Random(seed); n=len(xs); v=[]
    for _ in range(B):
        idx=[rnd.randrange(n) for _ in range(n)]; v.append(sum(xs[i] for i in idx)/n-sum(ys[i] for i in idx)/n)
    v.sort(); return v[int(.025*B)],v[int(.975*B)]
out=["# stats (generated)","",f"runs {len(runs)}; plan failures {sum(1 for r in runs if r.get('fail'))}; cost ${sum(r['cost'] for r in runs):.2f}; mean tokens {st.mean(r['tokens'] or 0 for r in runs):.0f}",""]
out.append("| base | stratum | n | single p@1 | single p@4 | single p@16 | arm2 p@1 | arm3 p@1 | arm2 p@4 | arm3 p@4 | arm2∪arm3 @4 | 0/16 items | 0/16 solved by any decomp | union(single16 ∪ decomp) − single16 | Δ arm2 p@1 − single p@1 [CI] |")
out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
rows_all=[]
for b in ('z-ai_glm-5.3-flash','deepseek_deepseek-v3.2'):
    for s in ('hard-true','hard-cap','medium','easy'):
        ids=[i for (bb,i) in meta if bb==b and substratum(b,i)==s and (b,i) in single]
        if not ids: continue
        sv=[single[(b,i)] for i in ids]
        p1=st.mean(st.mean(v) for v in sv); p4=st.mean(any(v[:4]) for v in sv); p16=st.mean(any(v) for v in sv)
        def arm(a,k):
            vals=[]
            for i in ids:
                reps=D.get((b,a,i),{}); got=[reps[r] for r in sorted(reps) if r<k]
                vals.append(any(got) if got else 0)
            return st.mean(vals)
        a2_1=arm('arm2',1); a3_1=arm('arm3',1); a2_4=arm('arm2',4); a3_4=arm('arm3',4)
        both4=st.mean(any(list(D.get((b,'arm2',i),{}).values())+list(D.get((b,'arm3',i),{}).values())) for i in ids)
        zero=[i for i in ids if sum(single[(b,i)])==0]
        zsolved=[i for i in zero if any(list(D.get((b,'arm2',i),{}).values())+list(D.get((b,'arm3',i),{}).values()))]
        union=st.mean(any(single[(b,i)]) or any(list(D.get((b,'arm2',i),{}).values())+list(D.get((b,'arm3',i),{}).values())) for i in ids)
        xs=[D.get((b,'arm2',i),{}).get(0,0) for i in ids]; ys=[single[(b,i)][0] for i in ids]
        # Δ vs mean single p@1 per item (more stable than draw 0)
        ys_m=[st.mean(single[(b,i)]) for i in ids]; lo,hi=boot_diff(xs,ys_m)
        out.append(f"| {b.split('_')[1][:8]} | {s} | {len(ids)} | {p1:.2f} | {p4:.2f} | {p16:.2f} | {a2_1:.2f} | {a3_1:.2f} | {a2_4:.2f} | {a3_4:.2f} | {both4:.2f} | {len(zero)} | {len(zsolved)} {zsolved if zsolved else ''} | {union-p16:+.2f} | {a2_1-p1:+.2f} [{lo:+.2f},{hi:+.2f}] |")
        rows_all.append((b,s,ids))
# phi between arm2 rep0 and single draw 0 over all items of a base
def phi(a,b_):
    n=len(a)
    if n==0: return float('nan')
    p1=sum(a)/n;p2=sum(b_)/n
    if p1 in(0,1) or p2 in(0,1):return float('nan')
    return (sum(x and y for x,y in zip(a,b_))/n-p1*p2)/math.sqrt(p1*(1-p1)*p2*(1-p2))
out.append("")
for b in ('z-ai_glm-5.3-flash','deepseek_deepseek-v3.2'):
    ids=[i for (bb,i) in meta if bb==b and (b,i) in single and 0 in D.get((b,'arm2',i),{}) and 0 in D.get((b,'arm3',i),{})]
    a2=[D[(b,'arm2',i)][0] for i in ids]; a3=[D[(b,'arm3',i)][0] for i in ids]; s0=[single[(b,i)][0] for i in ids]; s1=[single[(b,i)][1] for i in ids]
    out.append(f"{b}: n={len(ids)} φ(arm2,single0)={phi(a2,s0):.2f} φ(arm3,single0)={phi(a3,s0):.2f} φ(arm2,arm3)={phi(a2,a3):.2f} φ(single0,single1)={phi(s0,s1):.2f}")
# plan failure and truncation by base/arm
out.append("")
for b in ('z-ai_glm-5.3-flash','deepseek_deepseek-v3.2'):
    for a in ('arm2','arm3'):
        rr=[r for r in runs if r['base']==b and r['arm']==a]
        if not rr: continue
        out.append(f"{b} {a}: runs {len(rr)}, plan fail {sum(1 for r in rr if r.get('fail'))}, asm truncated {sum(1 for r in rr if r['calls'][-1]['step']=='asm' and r['calls'][-1]['finish']=='length')}, any subtask truncated {sum(1 for r in rr if any(c['finish']=='length' and c['step'].startswith('sub') for c in r['calls']))}, mean tokens {st.mean(r['tokens'] or 0 for r in rr):.0f}, mean subtasks {st.mean(len(r['plan'] or []) for r in rr):.1f}")
open('STATS.md','w').write('\n'.join(out)); print('\n'.join(out))
