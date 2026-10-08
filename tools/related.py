"""Thematic 'See also' for each publication: TF-IDF of title+abstract+tags, plus weighted shared keywords."""
import os, re, json, math, sys, unicodedata
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
def fm(path):
    t = open(path).read().split('---')[1]
    g = lambda k: (re.search(rf'^{k}: (.*)$', t, re.M) or [None, ''])[1]
    js = lambda k: json.loads(g(k)) if g(k).startswith('[') else []
    st = lambda k: json.loads(g(k)) if g(k).startswith('"') else g(k)
    return dict(title=st('title'), abstract=st('abstract'), tags=js('tags'), keywords=js('keywords'),
                types=js('publication_types'), date=g('date'))
def compute(site, n=5):
    """Return {folder: [n most thematically similar folders]} for all publications under site/content/publication."""
    C = os.path.join(site, 'content/publication')
    P = {d: fm(f'{C}/{d}/index.md') for d in sorted(os.listdir(C)) if os.path.isfile(f'{C}/{d}/index.md')}
    slugs = list(P)
    def norm(s): return unicodedata.normalize('NFKC', s)
    docs = [norm(' '.join([P[s]['title']] * 2 + [P[s]['abstract']] + P[s]['tags'] * 2)) for s in slugs]
    vec = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), min_df=2, max_df=0.5, sublinear_tf=True,
                          token_pattern=r'(?u)\b[\w⁰¹²³⁴⁵⁶⁷⁸⁹-]{2,}\b')
    X = vec.fit_transform(docs); S = (X @ X.T).toarray()
    # keyword weights: rarer keywords count more (inverse document frequency)
    N = len(slugs); df = {}
    for s in slugs:
        for k in P[s]['keywords']: df[k] = df.get(k, 0) + 1
    idf = {k: math.log(N / v) for k, v in df.items()}
    GENERIC = {'Zircon', 'ID-TIMS', 'LA-ICPMS'}   # techniques, not themes
    def score(a, b):
        ka, kb = set(P[a]['keywords']), set(P[b]['keywords'])
        shared = (ka & kb) - GENERIC
        kw = sum(idf[k] for k in shared) / max(1e-9, math.sqrt(sum(idf[k] for k in ka - GENERIC) * sum(idf[k] for k in kb - GENERIC) or 1))
        return 0.6 * S[slugs.index(a), slugs.index(b)] + 0.4 * kw
    out = {}
    for a in slugs:
        ranked = sorted((b for b in slugs if b != a), key=lambda b: -score(a, b))
        out[a] = [(b, round(score(a, b), 3)) for b in ranked[:n]]
    return {a: [b for b, _ in v[:n]] for a, v in out.items()}
