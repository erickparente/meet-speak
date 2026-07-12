#!/usr/bin/env python3
"""Valida uma aula do Meet&Speak contra o LESSON_SPEC v1.

Uso: python3 scripts/validate_lesson.py lessons/YYYY-MM-DD.json
Sai com código 1 se houver erros (avisos não bloqueiam).
"""
import json, re, sys, unicodedata
from pathlib import Path

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)  # junção de gaps: sem espaço antes de pontuação
    return re.sub(r"\s+", " ", s).strip().lower()

def main(path: str) -> int:
    errors, warns = [], []
    p = Path(path)
    try:
        lesson = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERRO: JSON inválido: {e}")
        return 1

    for k in ["schema", "date", "level", "estimated_minutes", "topic", "topic_pt",
              "article", "vocabulary", "reading", "listening", "writing", "speaking", "grammar"]:
        if k not in lesson:
            errors.append(f"campo raiz ausente: {k}")
    if errors:
        print("\n".join("ERRO: " + e for e in errors)); return 1

    art = lesson["article"]
    for k in ["headline", "source", "published", "url", "excerpt_note_pt", "paragraphs"]:
        if not art.get(k):
            errors.append(f"article.{k} ausente/vazio")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", lesson["date"]):
        errors.append("date deve ser YYYY-MM-DD")
    if p.stem != lesson["date"]:
        errors.append(f"nome do arquivo ({p.stem}) difere de date ({lesson['date']})")
    if not str(art.get("url", "")).startswith("http"):
        errors.append("article.url deve ser um link http(s) real")

    words = sum(len(x.split()) for x in art.get("paragraphs", []))
    if not 250 <= words <= 600:
        warns.append(f"trecho com {words} palavras (alvo: 300–500)")

    body = norm(" ".join(art.get("paragraphs", [])))

    def in_article(s: str) -> bool:
        return norm(s) in body

    # ditado: frases verbatim
    for i, g in enumerate(lesson["listening"].get("dictation", [])):
        full = f"{g['before']} {g['answer']} {g['after']}"
        if not in_article(full):
            errors.append(f"listening.dictation[{i}] não é verbatim do trecho: “{full[:70]}…”")

    # shadowing: frases verbatim
    for i, s in enumerate(lesson["speaking"].get("shadow_sentences", [])):
        if not in_article(s):
            errors.append(f"speaking.shadow_sentences[{i}] não é verbatim do trecho: “{s[:70]}…”")

    # exemplos de vocabulário: devem vir do trecho (permite reticências)
    for i, v in enumerate(lesson.get("vocabulary", [])):
        ex = re.sub(r"^…|…$|^\.\.\.|\.\.\.$", "", v.get("example", "")).strip()
        core = max(ex.split("…"), key=len).strip(" .")
        if core and norm(core) not in body:
            warns.append(f"vocabulary[{i}].example pode não ser verbatim: “{ex[:60]}…”")
        ex_norm = norm(v.get("example", ""))
        term_words = [w for w in norm(v.get("term", "")).split() if len(w) > 3]
        stems_ok = any(w[: max(4, len(w) - 2)] in ex_norm for w in term_words) if term_words else True
        if not stems_ok:
            warns.append(f"vocabulary[{i}]: o termo não aparece no exemplo")

    # contagens
    def count(name, seq, lo, hi):
        n = len(seq)
        if not lo <= n <= hi:
            warns.append(f"{name}: {n} itens (alvo {lo}–{hi})")
    count("vocabulary", lesson["vocabulary"], 6, 10)
    count("reading.questions", lesson["reading"]["questions"], 4, 6)
    count("listening.questions", lesson["listening"]["questions"], 2, 4)
    count("listening.dictation", lesson["listening"]["dictation"], 2, 4)
    count("speaking.shadow_sentences", lesson["speaking"]["shadow_sentences"], 3, 5)
    count("speaking.questions", lesson["speaking"]["questions"], 2, 4)
    count("grammar.exercises", lesson["grammar"]["exercises"], 4, 6)

    # sanidade das questões
    for sec in ["reading", "listening"]:
        for i, q in enumerate(lesson[sec]["questions"]):
            if q["type"] == "mc":
                if len(q.get("options", [])) != 4:
                    errors.append(f"{sec}.questions[{i}]: mc precisa de 4 opções")
                if not (isinstance(q.get("answer"), int) and 0 <= q["answer"] < 4):
                    errors.append(f"{sec}.questions[{i}]: answer deve ser índice 0–3")
            elif q["type"] == "tf":
                if not isinstance(q.get("answer"), bool):
                    errors.append(f"{sec}.questions[{i}]: tf precisa de answer true/false")
            if not q.get("explain_pt"):
                warns.append(f"{sec}.questions[{i}] sem explain_pt")
    for i, q in enumerate(lesson["grammar"]["exercises"]):
        if q.get("type") == "mc" and not (isinstance(q.get("answer"), int) and 0 <= q["answer"] < len(q.get("options", []))):
            errors.append(f"grammar.exercises[{i}]: answer fora do intervalo")
        if q.get("type") == "gap" and not q.get("answer"):
            errors.append(f"grammar.exercises[{i}]: gap sem answer")

    w = lesson["writing"]
    for k in ["title", "task_pt", "prompt_en", "min_words", "max_words", "checklist_pt", "model_answer"]:
        if not w.get(k):
            errors.append(f"writing.{k} ausente/vazio")
    mw = len(w.get("model_answer", "").split())
    if not (w.get("min_words", 0) - 10) <= mw <= (w.get("max_words", 999) + 15):
        warns.append(f"model_answer com {mw} palavras (meta {w.get('min_words')}–{w.get('max_words')})")

    # index.json coerente (pulado se o index estiver criptografado — o publish cuida dele)
    idx_path = p.parent / "index.json"
    if idx_path.exists():
        idx = json.loads(idx_path.read_text(encoding="utf-8"))
        if idx.get("enc"):
            print("nota: index.json criptografado — coerência será garantida pelo lesson_crypto.py publish")
        else:
            entry = next((x for x in idx.get("lessons", []) if x.get("date") == lesson["date"]), None)
            if not entry:
                errors.append("aula não está em lessons/index.json")
            elif norm(entry.get("headline", "")) != norm(art["headline"]):
                errors.append("headline no index.json difere da aula")

    for wmsg in warns:
        print("AVISO:", wmsg)
    for emsg in errors:
        print("ERRO:", emsg)
    print(f"\n{'FALHOU' if errors else 'OK'} — {len(errors)} erro(s), {len(warns)} aviso(s). Trecho: {words} palavras.")
    return 1 if errors else 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: validate_lesson.py lessons/YYYY-MM-DD.json"); sys.exit(2)
    sys.exit(main(sys.argv[1]))
