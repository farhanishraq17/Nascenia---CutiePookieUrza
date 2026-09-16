import sys, re, json
import numpy as np, pandas as pd, torch
sys.stdout.reconfigure(encoding='utf-8')
from transformers import AutoTokenizer, AutoModel

MODEL = 'bert-base-multilingual-cased'
dev_n = 250
tr = pd.read_csv(r'D:\Project Based Learning\Nascenia_Datathon\DATA\COMPETITION_PROVIDED_DATA\train.csv').dropna(subset=['input','output'])
rng = np.random.RandomState(42); idx = rng.permutation(len(tr))
dev = tr.iloc[idx[:dev_n]].reset_index(drop=True)
pool = tr.iloc[idx[600:]].reset_index(drop=True)

tokz = AutoTokenizer.from_pretrained(MODEL)
model = AutoModel.from_pretrained(MODEL).eval()
dev_dev = 'cuda' if torch.cuda.is_available() else 'cpu'
model = model.to(dev_dev).half() if dev_dev=='cuda' else model
print('device', dev_dev)

@torch.no_grad()
def embed(texts, bs=16, layer=9):
    outs = []
    for i in range(0, len(texts), bs):
        b = [str(t) for t in texts[i:i+bs]]
        enc = tokz(b, return_tensors='pt', padding=True, truncation=True, max_length=256).to(dev_dev)
        h = model(**enc, output_hidden_states=True).hidden_states[layer]
        h = torch.nn.functional.normalize(h.float(), dim=-1)
        for j in range(len(b)):
            m = enc['attention_mask'][j].bool()
            outs.append(h[j][m][1:-1].cpu())   # drop CLS/SEP
    return outs

def bertscore_f1(P, R):
    out = []
    for p, r in zip(P, R):
        if len(p)==0 or len(r)==0: out.append(0.0); continue
        sim = p @ r.T
        prec = sim.max(dim=1).values.mean().item()
        rec  = sim.max(dim=0).values.mean().item()
        out.append(0.0 if prec+rec==0 else 2*prec*rec/(prec+rec))
    return float(np.mean(out)), out

refs = dev['output'].tolist()
E_ref = embed(refs)

# candidate strategies
best_constant = None
# rebuild best constant quickly: most "central" long-ish generic response
PUNC = re.compile(r'[।,\.\?\!;:\(\)\[\]\{\}"\'`\-—–/\\|~@#\$%\^&\*\+=<>০-৯0-9]')
def tok(s): return PUNC.sub(' ', str(s)).split()
from collections import Counter
cand = pool[pool['output'].str.len().between(500,700)]['output'].sample(60, random_state=1).tolist()
probe = [Counter(tok(s)) for s in refs[:150]]
def tf1(ct, rc, rl):
    cp = Counter(ct); ov = sum((cp & rc).values())
    if ov==0: return 0
    p, r = ov/len(ct), ov/rl
    return 2*p*r/(p+r)
scored = sorted(((np.mean([tf1(tok(c), rc, sum(rc.values())) for rc in probe]), c) for c in cand), reverse=True, key=lambda x:x[0])
best_constant = scored[0][1]

strategies = {
  'oracle (reference itself)': refs,
  'best constant string':      [best_constant]*len(refs),
  'random real response':      pool['output'].sample(len(refs), random_state=5).tolist(),
  'generic boilerplate only':  ['হেলো, নাসেনিয়া ডকে আপনাকে স্বাগতম। আপনার অনুসন্ধানের জন্য ধন্যবাদ। আমি আপনার সমস্যাটি বুঝতে পেরেছি এবং যথাসাধ্য সাহায্য করার চেষ্টা করব। আপনার লক্ষণগুলোর জন্য একজন বিশেষজ্ঞ ডাক্তারের সাথে পরামর্শ করা উচিত এবং প্রয়োজনীয় পরীক্ষা-নিরীক্ষা করানো দরকার। চিকিৎসকের পরামর্শ অনুযায়ী ওষুধ সেবন করুন এবং পর্যাপ্ত বিশ্রাম নিন। আশা করি এই উত্তরটি আপনাকে সাহায্য করবে। আরও কোনো প্রশ্ন থাকলে জিজ্ঞাসা করতে পারেন। ধন্যবাদ।']*len(refs),
  'input echoed back':         dev['input'].tolist(),
}
print(f'\n{"strategy":30s} {"BERTScore_F1":>13s}')
out = {}
for name, preds in strategies.items():
    E = embed(preds)
    m, _ = bertscore_f1(E, E_ref)
    out[name] = m
    print(f'{name:30s} {m:13.4f}')
json.dump(out, open(r'C:\Users\LENOVO\AppData\Local\Temp\claude\D--Project-Based-Learning-Nascenia-Datathon\070b9cef-7b39-4a42-8e4f-eb6d60611efe\scratchpad\bert.json','w'), indent=2)
print('\nBEST CONSTANT USED:', best_constant[:200])
print('DONE')
