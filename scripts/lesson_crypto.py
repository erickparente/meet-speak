#!/usr/bin/env python3
"""Criptografa e publica aulas do Meet&Speak (compatível com o Web Crypto do site).

Formato: PBKDF2-SHA256 (310000 iterações) -> AES-256-GCM. Wrapper JSON:
  {"enc":1,"kdf":"PBKDF2-SHA256","iter":310000,"salt":b64,"iv":b64,"data":b64}

Comandos:
  publish <aula_plaintext.json> --password SENHA [--repo-root DIR]
      Valida nome/data, grava lessons/<date>.json criptografada e atualiza
      (decripta, insere no topo, recriptografa) lessons/index.json.
  decrypt <arquivo.json> --password SENHA
      Imprime o JSON decriptado (debug/verificação).
"""
import argparse, base64, json, os, sys
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    print("ERRO: instale a lib -> pip install cryptography --break-system-packages")
    sys.exit(2)

ITER = 310000

def derive(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER)
    return kdf.derive(password.encode("utf-8"))

def encrypt_obj(obj, password: str) -> dict:
    salt, iv = os.urandom(16), os.urandom(12)
    key = derive(password, salt)
    data = AESGCM(key).encrypt(iv, json.dumps(obj, ensure_ascii=False).encode("utf-8"), None)
    b64 = lambda b: base64.b64encode(b).decode()
    return {"enc": 1, "kdf": "PBKDF2-SHA256", "iter": ITER, "salt": b64(salt), "iv": b64(iv), "data": b64(data)}

def decrypt_obj(wrapper: dict, password: str):
    b = lambda s: base64.b64decode(s)
    key = derive(password, b(wrapper["salt"]))
    plain = AESGCM(key).decrypt(b(wrapper["iv"]), b(wrapper["data"]), None)
    return json.loads(plain.decode("utf-8"))

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def save(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=None, separators=(",", ":")), encoding="utf-8")

def cmd_publish(args):
    plain_path = Path(args.file)
    lesson = load(plain_path)
    date = lesson.get("date", "")
    if plain_path.stem != date:
        print(f"ERRO: nome do arquivo ({plain_path.stem}) difere de date ({date})"); return 1
    root = Path(args.repo_root)
    ldir = root / "lessons"
    ldir.mkdir(exist_ok=True)
    out = ldir / f"{date}.json"

    save(out, encrypt_obj(lesson, args.password))

    idx_path = ldir / "index.json"
    idx = {"lessons": []}
    if idx_path.exists():
        raw = load(idx_path)
        idx = decrypt_obj(raw, args.password) if raw.get("enc") else raw
    entry = {"date": date, "headline": lesson["article"]["headline"],
             "topic": lesson.get("topic", ""), "topic_pt": lesson.get("topic_pt", ""),
             "source": lesson["article"].get("source", ""),
             "grammar": (lesson.get("grammar") or {}).get("title", ""),
             "vocab": [v.get("term", "") for v in lesson.get("vocabulary", [])]}
    idx["lessons"] = [entry] + [x for x in idx.get("lessons", []) if x.get("date") != date]
    idx["lessons"].sort(key=lambda x: x["date"], reverse=True)
    save(idx_path, encrypt_obj(idx, args.password))
    print(f"OK: {out.name} criptografada e index.json atualizado ({len(idx['lessons'])} aula(s)).")
    return 0

def cmd_decrypt(args):
    raw = load(Path(args.file))
    if not raw.get("enc"):
        print(json.dumps(raw, ensure_ascii=False, indent=2)); return 0
    print(json.dumps(decrypt_obj(raw, args.password), ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("publish"); p1.add_argument("file"); p1.add_argument("--password", required=True); p1.add_argument("--repo-root", default=".")
    p2 = sub.add_parser("decrypt"); p2.add_argument("file"); p2.add_argument("--password", required=True)
    a = ap.parse_args()
    sys.exit({"publish": cmd_publish, "decrypt": cmd_decrypt}[a.cmd](a))
