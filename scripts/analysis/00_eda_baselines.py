import sys, re, json
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np, pandas as pd

SP = r'C:\Users\LENOVO\AppData\Local\Temp\claude\D--Project-Based-Learning-Nascenia-Datathon\070b9cef-7b39-4a42-8e4f-eb6d60611efe\scratchpad'
tr = pd.read_csv(r'D:\Project Based Learning\Nascenia_Datathon\DATA\COMPETITION_PROVIDED_DATA\train.csv').dropna(subset=['input','output'])
te = pd.read_csv(r'D:\Project Based Learning\Nascenia_Datathon\DATA\COMPETITION_PROVIDED_DATA\test.csv')

PUNC = re.compile(r'[।,\.\?\!;:\(\)\[\]\{\}"\'`\-—–/\\|~@#\$%\^&\*\+=<>০-৯0-9]')
def tok(s): return PUNC.sub(' ', str(s)).split()

tr['otokl'] = tr['output'].map(lambda s: len(tok(s)))
tr['itokl'] = tr['input'].map(lambda s: len(tok(s)))
te['itokl'] = te['input'].map(lambda s: len(tok(s)))

print('=== TOKEN LENGTHS (whitespace words) ===')
for nm, ser in [('train input', tr['itokl']), ('train output', tr['otokl']), ('test input', te['itokl'])]:
    q = ser.quantile([.05,.25,.5,.75,.90,.95,.99])
    print(f'{nm:13s} mean={ser.mean():6.1f} ' + ' '.join(f'p{int(k*100)}={v:.0f}' for k,v in q.items()))

print('\n=== DUPLICATES / LEAKAGE ===')
print('dup inputs:', int(tr["input"].duplicated().sum()), '| dup outputs:', int(tr["output"].duplicated().sum()))
print('test inputs exactly in train:', int(te['input'].isin(set(tr['input'])).sum()), '/', len(te))

print('\n=== OPENERS (first 2 output tokens) ===')
for v,c in tr['output'].map(lambda s:' '.join(tok(s)[:2])).value_counts().head(10).items():
    print(f'  {c:6d} ({100*c/len(tr):5.2f}%)  {v}')
print('\n=== first token only ===')
for v,c in tr['output'].map(lambda s:(tok(s)+[""])[0]).value_counts().head(8).items():
    print(f'  {c:6d} ({100*c/len(tr):5.2f}%)  {v}')

print('\n=== HIGH DOC-FREQUENCY OUTPUT TOKENS (in 20k sample) ===')
cnt = Counter()
N=20000
for s in tr['output'].sample(N, random_state=0): cnt.update(set(tok(s)))
for w,c in cnt.most_common(35): print(f'   {100*c/N:5.1f}%  {w}')

# ---------- fast metrics ----------
def token_f1(ptoks, rtoks, rcnt=None):
    if not ptoks or not rtoks: return 0.0
    cp = Counter(ptoks); cr = rcnt if rcnt is not None else Counter(rtoks)
    ov = sum((cp & cr).values())
    if ov == 0: return 0.0
    return 2*(ov/len(ptoks))*(ov/len(rtoks))/((ov/len(ptoks))+(ov/len(rtoks)))

def lcs_np(a, b):
    """LCS length via numpy row DP - vectorized inner loop."""
    la, lb = len(a), len(b)
    if la == 0 or lb == 0: return 0
    if la > lb: a, b, la, lb = b, a, lb, la
    b = np.array(b, dtype=object)
    prev = np.zeros(lb+1, dtype=np.int32)
    for i in range(la):
        eq = (b == a[i])
        cur = np.zeros(lb+1, dtype=np.int32)
        # cur[j+1] = max(prev[j]+1 if eq[j] else 0, cur[j], prev[j+1])
        cand = np.where(eq, prev[:-1]+1, 0)
        cur[1:] = np.maximum(cand, prev[1:])
        # enforce running max (cur[j] propagation)
        np.maximum.accumulate(cur, out=cur)
        prev = cur
    return int(prev[lb])

def rouge_l(ptoks, rtoks):
    if not ptoks or not rtoks: return 0.0
    l = lcs_np(ptoks, rtoks)
    if l == 0: return 0.0
    p, r = l/len(ptoks), l/len(rtoks)
    return 2*p*r/(p+r)

rng = np.random.RandomState(42)
idx = rng.permutation(len(tr))
dev = tr.iloc[idx[:600]].reset_index(drop=True)
pool = tr.iloc[idx[600:]].reset_index(drop=True)
dev_toks = [tok(s) for s in dev['output']]
dev_cnts = [Counter(t) for t in dev_toks]

def score_pred_list(preds_toks):
    f1 = np.mean([token_f1(p, r, c) for p, r, c in zip(preds_toks, dev_toks, dev_cnts)])
    rl = np.mean([rouge_l(p, r) for p, r in zip(preds_toks, dev_toks)])
    return f1, rl, 0.3*f1+0.2*rl

res = {}
print('\n=== BASELINE A: BEST CONSTANT RESPONSE ===')
probe_toks = dev_toks[:250]; probe_cnts = dev_cnts[:250]
cand = pool[(pool['otokl']>pool['otokl'].quantile(.40))&(pool['otokl']<pool['otokl'].quantile(.70))]['output'].sample(150, random_state=1).tolist()
scored = []
for c in cand:
    ct = tok(c)
    scored.append((np.mean([token_f1(ct, r, cc) for r, cc in zip(probe_toks, probe_cnts)]), c))
scored.sort(reverse=True, key=lambda x: x[0])
best = scored[0][1]; bt = tok(best)
f1, rl, pt = score_pred_list([bt]*len(dev))
print(f'  TokenF1={f1:.4f}  RougeL={rl:.4f}  0.3F1+0.2RL={pt:.4f}   ({len(bt)} tokens)')
print('  text:', best[:220].replace('\n',' '))
res['constant'] = dict(tokf1=float(f1), rougel=float(rl), partial=float(pt))

print('\n=== BASELINE B: TF-IDF RETRIEVAL ===')
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
sub = pool.sample(60000, random_state=3).reset_index(drop=True)
for aname, kw in [('word', dict(analyzer='word', token_pattern=r'\S+', min_df=2, sublinear_tf=True)),
                  ('char_wb 3-5', dict(analyzer='char_wb', ngram_range=(3,5), min_df=3, max_features=400000, sublinear_tf=True))]:
    vec = TfidfVectorizer(**kw)
    X = normalize(vec.fit_transform(sub['input'].astype(str)))
    Q = normalize(vec.transform(dev['input'].astype(str)))
    sim = (Q @ X.T).toarray()
    top = sim.argmax(1)
    preds = [tok(s) for s in sub['output'].iloc[top]]
    f1, rl, pt = score_pred_list(preds)
    print(f'  [{aname}] TokenF1={f1:.4f} RougeL={rl:.4f} 0.3F1+0.2RL={pt:.4f}  mean_sim={sim.max(1).mean():.3f}')
    res[f'retrieval_{aname}'] = dict(tokf1=float(f1), rougel=float(rl), partial=float(pt))

print('\n=== BASELINE C: RANDOM REAL RESPONSE (fluent but unrelated) ===')
preds = [tok(s) for s in pool['output'].sample(len(dev), random_state=5)]
f1, rl, pt = score_pred_list(preds)
print(f'  TokenF1={f1:.4f} RougeL={rl:.4f} 0.3F1+0.2RL={pt:.4f}')
res['random_real'] = dict(tokf1=float(f1), rougel=float(rl), partial=float(pt))

print('\n=== BASELINE D: ORACLE (the true reference itself) ===')
f1, rl, pt = score_pred_list(dev_toks)
print(f'  TokenF1={f1:.4f} RougeL={rl:.4f} 0.3F1+0.2RL={pt:.4f}  <- ceiling')

print('\n=== LENGTH SENSITIVITY: truncated best-constant ===')
for L in [15,25,40,60,80,100,120,150,200]:
    if L > len(bt): break
    c = bt[:L]
    f1 = np.mean([token_f1(c, r, cc) for r, cc in zip(probe_toks, probe_cnts)])
    rl = np.mean([rouge_l(c, r) for r in probe_toks])
    print(f'  len={L:4d}: TokenF1={f1:.4f} RougeL={rl:.4f} 0.3F1+0.2RL={0.3*f1+0.2*rl:.4f}')

print('\n=== GENERATION-LENGTH vs SCORE (using retrieval preds truncated) ===')
vec = TfidfVectorizer(analyzer='word', token_pattern=r'\S+', min_df=2, sublinear_tf=True)
X = normalize(vec.fit_transform(sub['input'].astype(str)))
Q = normalize(vec.transform(dev['input'].astype(str)))
top = (Q @ X.T).toarray().argmax(1)
rp = [tok(s) for s in sub['output'].iloc[top]]
for L in [40,60,80,100,120,150,250]:
    preds = [p[:L] for p in rp]
    f1, rl, pt = score_pred_list(preds)
    print(f'  cap={L:4d}: TokenF1={f1:.4f} RougeL={rl:.4f} 0.3F1+0.2RL={pt:.4f}')

json.dump(res, open(SP+r'\baselines.json','w'), indent=2)
print('\nDONE')
