import json
import os
from datetime import datetime, timezone

import numpy as np
from dotenv import load_dotenv
from postgrest.exceptions import APIError
from supabase import create_client

load_dotenv()
_client = None


def get_client():
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SECRET_KEY")
        if not url or not key:
            raise RuntimeError("Faltam SUPABASE_URL ou SUPABASE_SECRET_KEY no .env")
        _client = create_client(url, key)
    return _client


def init_db():
    try:
        get_client().table("pessoas").select("id").limit(1).execute()
    except Exception as e:
        raise RuntimeError(f"Não consegui conectar ao Supabase: {e}") from e


def save_person(nome, embeddings, consentimento=False):
    if not isinstance(nome, str) or not nome.strip():
        raise ValueError("Nome/ID vazio.")
    v = np.asarray(embeddings, dtype=np.float32)
    if v.ndim == 2:
        v = v.mean(axis=0)
    if v.ndim != 1 or not np.isfinite(v).all() or np.linalg.norm(v) < 1e-8:
        raise ValueError("Embedding inválido.")
    if v.size != 128:
        raise ValueError("Embedding deve ter 128 dimensões (SFace).")
    v = v / np.linalg.norm(v)

    dados = {
        "nome": nome.strip(),
        "embedding": "[" + ",".join(f"{x:.8f}" for x in v) + "]",
        "consentimento": consentimento,
        "data_consentimento": datetime.now(timezone.utc).isoformat() if consentimento else None,
    }
    try:
        res = get_client().table("pessoas").insert(dados).execute()
    except APIError as e:
        if getattr(e, "code", None) == "23505":
            raise ValueError("Nome/ID já cadastrado.") from e
        raise RuntimeError(f"Erro ao salvar no Supabase: {e.message}") from e
    return res.data[0]["id"]


def list_people():
    res = (get_client().table("pessoas")
           .select("id,nome,criado_em").eq("ativo", True).order("nome").execute())
    return [{"id": r["id"], "nome": r["nome"], "data_cadastro": r["criado_em"]}
            for r in res.data]


def embeddings():
    res = (get_client().table("pessoas")
           .select("id,nome,embedding").eq("ativo", True).execute())
    out = []
    for r in res.data:
        emb = r["embedding"]
        if isinstance(emb, str):
            emb = json.loads(emb)
        v = np.asarray(emb, dtype=np.float32)
        if v.size == 128 and np.isfinite(v).all():
            out.append({"id": r["id"], "nome": r["nome"], "embedding": v})
    return out


def delete_person(pid):
    res = get_client().table("pessoas").delete().eq("id", int(pid)).execute()
    return len(res.data) > 0