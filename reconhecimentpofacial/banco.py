import sqlite3
from datetime import datetime, timezone
import numpy as np
from config import DB_PATH

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con=sqlite3.connect(DB_PATH); con.row_factory=sqlite3.Row
    return con

def init_db():
    with connect() as c:
        c.execute("CREATE TABLE IF NOT EXISTS pessoas (id INTEGER PRIMARY KEY, nome TEXT UNIQUE COLLATE NOCASE NOT NULL, embedding BLOB NOT NULL, dimensao INTEGER NOT NULL, data_cadastro TEXT NOT NULL)")

def save_person(nome, embeddings):
    if not isinstance(nome,str) or not nome.strip(): raise ValueError("Nome/ID vazio.")
    v=np.asarray(embeddings,dtype=np.float32)
    if v.ndim==2: v=v.mean(axis=0)
    if v.ndim!=1 or not np.isfinite(v).all() or np.linalg.norm(v)<1e-8: raise ValueError("Embedding inválido.")
    v=v/np.linalg.norm(v)
    try:
        with connect() as c:
            cur=c.execute("INSERT INTO pessoas(nome,embedding,dimensao,data_cadastro) VALUES(?,?,?,?)",
                (nome.strip(),v.tobytes(),v.size,datetime.now(timezone.utc).isoformat()))
            return cur.lastrowid
    except sqlite3.IntegrityError as e: raise ValueError("Nome/ID já cadastrado.") from e

def list_people():
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT id,nome,data_cadastro FROM pessoas ORDER BY nome")]

def embeddings():
    with connect() as c: rows=c.execute("SELECT id,nome,embedding,dimensao FROM pessoas").fetchall()
    out=[]
    for r in rows:
        v=np.frombuffer(r["embedding"],dtype=np.float32).copy()
        if v.size==r["dimensao"] and np.isfinite(v).all(): out.append({"id":r["id"],"nome":r["nome"],"embedding":v})
    return out

def delete_person(pid):
    with connect() as c: return c.execute("DELETE FROM pessoas WHERE id=?",(int(pid),)).rowcount>0
