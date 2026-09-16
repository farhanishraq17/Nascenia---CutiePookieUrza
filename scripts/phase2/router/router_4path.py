"""router_4path.py — the full pipeline, in the two divisions the design calls for.

    DIVISION 1 — Phase 1.  The leaderboard path, untouched.
      1 ID_LOOKUP      competition id resolves into ChatDoctor    -> CHAMPION (exact draft)

    DIVISION 2 — no direct id.  Everything below only ever runs when branch 1 misses.
      2 CONTENT_MATCH  ChatDoctor, matched on question text >= t1 -> CHAMPION (recovered draft)
      3 BROAD_MATCH    the wider corpus,               sim >= t2  -> CHAMPION (recovered draft)
      4 SPECIALIST     nothing clears                             -> QWEN D1

`router.py` (3 branches) stays as the validated ROUTER-01 artefact and is not modified. This module
adds branch 3 on top of it.

🔴 WHY BRANCH 3's CORPUS IS NOT "EVERY DATASET WE HOLD"
Two independent constraints point at the same, smaller set, so this is forced rather than chosen:

  (a) STRUCTURAL. The champion consumes "english: {en}\\nbangla: {bn}". A source with no English
      side cannot form that input at all. `given_train` (competition Bengali) and
      `doctor_qa_bangla` (natively Bengali) have no English anywhere -- they are unusable here
      regardless of how they score.
  (b) MEASURED (LOOKUP-EXPAND, 2026-08-23, on the 133 dev rows branch 2 rejects):
        ai_medical_chatbot  0.3258   <- the only non-ChatDoctor source with real signal
        given_train         0.1970   <- also structurally unusable, per (a)
        icliniq             0.0758
        genmedgpt           0.0547
        doctor_qa_bangla    0.0351   <- also structurally unusable, per (a)

The two worst sources are exactly the two that cannot supply an English side. What remains is
ai_medical_chatbot (English recoverable via `aimc_<n>` -> Data_Search_4 `source_row`), plus icliniq
and genmedgpt whose English lives in the ChatDoctor English file.

🔴 BRANCH 3 IS DISABLED BY DEFAULT AND SHOULD STAY THAT WAY. THERE IS NO SAFE THRESHOLD.
The gate that makes branch 2 trustworthy does not exist for branch 3. Measured on the 133 dev
rows branch 2 rejects (LOOKUP-EXPAND, 2026-08-23):

      tau     ChatDoctor draft F1      broad-corpus draft F1
     0.00           0.5803                    0.2249
     0.30           0.5865                    0.2448
     0.35           0.5927                    0.2797   <- peak
     0.40           0.5961                    0.2616
     0.45           0.5960                    0.1569
     0.50           0.5973                    0.1306
     0.60             --                      0.1183

ChatDoctor rises **monotonically** with similarity: more confidence really does mean a better
draft, which is what licenses a threshold at all. The broad corpus **peaks at 0.35 and then
collapses** -- by 0.60 it is below the measured wrong-match floor (0.1795). Similarity there is
not evidence of correct content; the top-scoring rows are generic medical boilerplate that is
lexically close and clinically unrelated. **You cannot tune t2 to make this safe.**

A second, independent reason: English is only recoverable for corpora we have PRE-INDEXED. The
case branch 3 exists to insure against -- a Phase 2 question from a corpus we do not hold -- has
no English side at all, so no champion input can be formed for it. The branch only functions
where it is least needed.

Both arguments land in the same place: **those rows belong to the specialist.** Qwen at least
attempts the actual question. The champion handed a wrong draft does not fail loudly -- it
fluently restyles a different patient's answer into perfect house register, which reads as
confident and is the failure mode an LLM judge punishes hardest.

The branch-3 code is kept, disabled (`t2=1.01`), because the corpus plumbing (English recovery,
leak control) is correct and re-measuring is cheaper than rebuilding. Enabling it requires new
evidence, not a new threshold.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CHAMPION_TEMPLATE = "english: {en}\nbangla: {bn}"
ID_LOOKUP, CONTENT_MATCH, BROAD_MATCH, SPECIALIST = (
    "ID_LOOKUP", "CONTENT_MATCH", "BROAD_MATCH", "SPECIALIST")

# English is recoverable for these; the others in the master corpus have no English side at all.
BROAD_SOURCES = ("ai_medical_chatbot", "icliniq", "genmedgpt")


@dataclass
class Decision:
    row_id: object
    branch: str
    champion_input: str | None   # ready for the champion; None only on SPECIALIST
    matched_key: object | None   # which corpus row supplied the draft
    similarity: float | None     # None on ID_LOOKUP (exact, not a match score)


def _tfidf(texts, max_features):
    from sklearn.feature_extraction.text import TfidfVectorizer
    v = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                        max_features=max_features, min_df=2, sublinear_tf=True)
    return v, v.fit_transform(texts)


def _top1(vec, X, queries, chunk=256):
    Q = vec.transform(queries)
    bi = np.empty(Q.shape[0], dtype=np.int64)
    bs = np.empty(Q.shape[0], dtype=np.float32)
    for s in range(0, Q.shape[0], chunk):
        S = (Q[s:s + chunk] @ X.T).toarray()
        bi[s:s + chunk] = S.argmax(axis=1)
        bs[s:s + chunk] = S.max(axis=1)
    return bi, bs


class Router4:
    def __init__(self, chatdoctor_bn_csv, chatdoctor_en_csv, master_csv=None,
                 aimc_en_csv=None, t1: float = 0.40, t2: float = 1.01,
                 exclude_ids=(), max_features: int = 200_000, verbose: bool = True):
        """
        t1 : branch-2 floor. 0.40 -> 88% routed at 98.1% precision (ROUTER-01).
        t2 : branch-3 floor. Default 1.01 = DISABLED, deliberately (see module docstring).
        exclude_ids : ids to drop from every corpus. 🔴 Pass the frozen dev/test ids whenever
                      you evaluate, or a row retrieves its own answer and the number is fiction.
        """
        self.t1, self.t2, self.verbose = t1, t2, verbose
        self.exclude = {str(x) for x in exclude_ids}

        bn = pd.read_csv(chatdoctor_bn_csv, dtype=str).dropna(subset=["input", "output"])
        en = pd.read_csv(chatdoctor_en_csv, dtype=str).dropna(subset=["output"])
        cd_bn = bn[bn["source"] == "healthcaremagic"].copy()
        cd_en = en[en["source"] == "healthcaremagic"].copy() if "source" in en else en.copy()
        for d in (cd_bn, cd_en):
            d["cid"] = d["id"].str.replace("hcm_", "", regex=False)
        cd_bn = cd_bn[~cd_bn["cid"].isin(self.exclude)].drop_duplicates("cid")
        cd_en = cd_en.drop_duplicates("cid")

        self.bn_q = cd_bn.set_index("cid")["input"]
        self.bn_a = cd_bn.set_index("cid")["output"]
        self.en_a = cd_en.set_index("cid")["output"]
        keys = self.bn_q.index.intersection(self.bn_a.index).intersection(self.en_a.index)
        self.cd_keys = np.array(keys)
        self._say(f"ChatDoctor usable (question + both answers): {len(self.cd_keys):,}")

        self._say("indexing branch 2 ...")
        self.v1, self.X1 = _tfidf(self.bn_q.loc[self.cd_keys].astype(str).tolist(), max_features)

        # ---- branch 3 -------------------------------------------------------------------
        self.broad = None
        if master_csv is not None and t2 <= 1.0:
            self.broad = self._build_broad(master_csv, aimc_en_csv, chatdoctor_en_csv)
            self._say("indexing branch 3 ...")
            self.v2, self.X2 = _tfidf(self.broad["input"].astype(str).tolist(), max_features)
        elif master_csv is not None:
            self._say("branch 3 corpus NOT built (t2 > 1.0 -> branch disabled)")

    def _say(self, m):
        if self.verbose:
            print(m, flush=True)

    def _build_broad(self, master_csv, aimc_en_csv, cd_en_csv) -> pd.DataFrame:
        m = pd.read_csv(master_csv, dtype=str).dropna(subset=["input", "output"])
        m = m[m["source"].isin(BROAD_SOURCES)]
        m = m[~m["id"].isin(self.exclude)]
        self._say(f"branch 3 candidate rows (sources with a recoverable English side): {len(m):,}")

        eng = {}
        if aimc_en_csv is not None and Path(aimc_en_csv).is_file():
            a = pd.read_csv(aimc_en_csv, dtype=str).dropna(subset=["doctor"])
            eng.update({f"aimc_{r}": d for r, d in zip(a["source_row"], a["doctor"])})
        ce = pd.read_csv(cd_en_csv, dtype=str).dropna(subset=["output"])
        eng.update({i: o for i, o in zip(ce["id"], ce["output"])
                    if i.startswith(("ic_", "gmg_"))})

        m["english"] = m["id"].map(eng)
        before = len(m)
        m = m.dropna(subset=["english"])          # no English -> cannot form a champion input
        self._say(f"  kept {len(m):,} with English recovered (dropped {before-len(m):,})")
        return m.reset_index(drop=True)

    def _exact(self, rid):
        k = str(rid)
        return k if (k in self.en_a.index and k in self.bn_a.index) else None

    def route(self, ids, questions) -> list[Decision]:
        ids, questions = list(ids), list(questions)
        assert len(ids) == len(questions)
        out: list[Decision | None] = [None] * len(ids)

        # ---- branch 1: exact id (Division 1 -- this is the whole Phase 1 path) ------------
        pending = []
        for i, rid in enumerate(ids):
            k = self._exact(rid)
            if k is not None:
                out[i] = Decision(rid, ID_LOOKUP,
                                  CHAMPION_TEMPLATE.format(en=self.en_a.loc[k], bn=self.bn_a.loc[k]),
                                  k, None)
            else:
                pending.append(i)
        self._say(f"branch 1 ID_LOOKUP     : {len(ids)-len(pending)}")
        if not pending:
            return out  # Phase 1 exits here: nothing below ever executes

        # ---- branch 2: ChatDoctor content match ------------------------------------------
        idx, sim = _top1(self.v1, self.X1, [questions[i] for i in pending])
        still = []
        for j, i in enumerate(pending):
            if sim[j] >= self.t1:
                k = self.cd_keys[idx[j]]
                out[i] = Decision(ids[i], CONTENT_MATCH,
                                  CHAMPION_TEMPLATE.format(en=self.en_a.loc[k], bn=self.bn_a.loc[k]),
                                  k, float(sim[j]))
            else:
                still.append(i)
        self._say(f"branch 2 CONTENT_MATCH : {len(pending)-len(still)}")

        # ---- branch 3: broad corpus ------------------------------------------------------
        if still and self.broad is not None:
            i3, s3 = _top1(self.v2, self.X2, [questions[i] for i in still])
            left = []
            for j, i in enumerate(still):
                if s3[j] >= self.t2:
                    r = self.broad.iloc[i3[j]]
                    out[i] = Decision(ids[i], BROAD_MATCH,
                                      CHAMPION_TEMPLATE.format(en=r["english"], bn=r["output"]),
                                      r["id"], float(s3[j]))
                else:
                    left.append(i)
            self._say(f"branch 3 BROAD_MATCH   : {len(still)-len(left)}")
            still = left

        # ---- branch 4: specialist --------------------------------------------------------
        for i in still:
            out[i] = Decision(ids[i], SPECIALIST, None, None, None)
        self._say(f"branch 4 SPECIALIST    : {len(still)}")
        assert all(o is not None for o in out), "a row was never routed"
        return out

    @staticmethod
    def summarize(decisions) -> dict:
        from collections import Counter
        c = Counter(d.branch for d in decisions)
        n = len(decisions) or 1
        champ = c[ID_LOOKUP] + c[CONTENT_MATCH] + c[BROAD_MATCH]
        return {"n": len(decisions), **{b: c[b] for b in
                (ID_LOOKUP, CONTENT_MATCH, BROAD_MATCH, SPECIALIST)},
                "pct_to_champion": 100.0 * champ / n}
