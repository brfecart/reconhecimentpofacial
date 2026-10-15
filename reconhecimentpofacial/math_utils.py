import numpy as np

def cosine(a, b):
    a=np.asarray(a,dtype=np.float32).reshape(-1)
    b=np.asarray(b,dtype=np.float32).reshape(-1)
    if a.shape!=b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Vetores inválidos/incompatíveis")
    d=float(np.linalg.norm(a)*np.linalg.norm(b))
    if d<1e-8: raise ValueError("Vetor nulo")
    return float(np.dot(a,b)/d)
