# Meet&Speak — Especificação da aula diária (LESSON_SPEC v1)

Este documento é o contrato que a automação diária deve seguir para gerar a aula.
O site (`index.html`) renderiza qualquer JSON que siga este formato.

## Regras inegociáveis

1. **A notícia é real e o texto é sagrado.** Nunca invente, resuma, parafraseie ou "melhore" o texto da notícia. Os `article.paragraphs` devem ser parágrafos contínuos copiados VERBATIM (palavra por palavra, pontuação incluída) da matéria publicada.
2. **Verifique a fidelidade do texto** extraindo a matéria duas vezes (prompts diferentes) e comparando; use apenas parágrafos idênticos nas duas extrações.
3. **Fontes aceitas (nesta ordem de preferência):** BBC (bbc.com), CNN (cnn.com), Reuters, The Guardian, AP News, PBS NewsHour, NPR, Al Jazeera English, CNBC, ABC News. A matéria deve ter sido publicada nas últimas 24–36 horas.
4. **Se uma fonte bloquear o acesso, tente a próxima.** Nunca reconstrua a notícia "de memória" a partir de manchetes ou resultados de busca.
5. **Tamanho do trecho:** 300–500 palavras, cortadas apenas em fim de parágrafo (a aula é de ~20 min). Sempre inclua `article.url` para a matéria completa e o aviso em `excerpt_note_pt`.
6. **Atribuição completa:** `headline` exata, `source`, `agency` (se for matéria de agência, ex.: AP/Reuters), `published` e `url`.
7. **Todo exercício deve ser respondível apenas com o trecho incluído.** Não use fatos das partes não incluídas da matéria nem conhecimento externo.
8. **Ditado e shadowing usam frases VERBATIM do trecho.** O validador confere isso automaticamente.
9. **Idempotência:** se `lessons/<data-de-hoje>.json` já existir no repositório, não faça nada (a aula do dia já foi publicada).
10. **Rotação de temas** (preferências do aluno: Mundo & política, Tecnologia & ciência, Negócios & economia, Cultura & esportes): evite repetir o tema do dia anterior quando houver boa alternativa. Escolha sempre uma matéria adequada ao nível B1–B2 (evite textos muito técnicos ou jurídicos) e evite conteúdo gráfico/violento em excesso.

## Nível e dosagem (B1–B2, ~20 minutos)

- `vocabulary`: 8 itens úteis e reutilizáveis (não nomes próprios), cada um com exemplo VERBATIM da matéria.
- `reading.questions`: 5 (mistura de `mc` com 4 opções e `tf`), com `explain_pt` que ensina, citando o trecho relevante.
- `listening.questions`: 3 `mc` focadas em detalhes auditivos (números, datas, nomes); `listening.dictation`: 3 frases verbatim com UMA palavra oculta cada (`accept` para grafias alternativas, ex.: canceled/cancelled).
- `writing`: tarefa comunicativa ligada à notícia (e-mail, mensagem, opinião), 60–100 palavras, `checklist_pt` com 4 itens acionáveis, `model_answer` original (NUNCA apresentar como parte da notícia) + `model_note_pt`.
- `speaking.shadow_sentences`: 4 frases verbatim de 8–16 palavras; `speaking.questions`: 3 perguntas abertas (da mais guiada à mais pessoal) com `support_pt`.
- `grammar`: 1 ponto gramatical que APARECE no texto do dia, explicado em português (`point_pt`, HTML simples com <p>, <b>, <i>), 3–4 `examples` verbatim com o alvo em `<mark>`, e 5 `exercises` (3 `mc` + 2 `gap`). Rotacione os pontos ao longo da semana (tempos verbais, voz passiva, reported speech, relative clauses, comparativos, condicionais, phrasal verbs, artigos, preposições…). Não repita o ponto dos últimos 3 dias (confira as aulas anteriores em `lessons/`).

## Formato do JSON

Use `lessons/2026-07-12.json` como referência canônica de estrutura. Campos:

- Raiz: `schema` (1), `date` (YYYY-MM-DD, data de hoje em GMT-3), `level`, `estimated_minutes`, `topic`, `topic_pt`.
- `article`: `headline`, `source`, `agency`, `published`, `url`, `excerpt_note_pt`, `paragraphs[]`.
- Questões `mc`: `{type:"mc", q, options[4], answer:<índice 0-based>, explain_pt}`.
- Questões `tf`: `{type:"tf", q, answer:<true|false>, explain_pt}`.
- Gaps/ditado: `{before, answer, after, hint_pt, accept?:[]}` — `before + answer + after` deve reproduzir a frase original exatamente (no ditado) e ser uma frase correta (na gramática).

## Criptografia (aulas protegidas por senha)

As aulas e o `lessons/index.json` ficam CRIPTOGRAFADOS no repositório
(PBKDF2-SHA256 + AES-256-GCM — wrapper `{"enc":1,...}`). O site pede a senha ao abrir.
A senha é fornecida à automação; nunca escreva a senha em arquivos do repositório,
e não inclua a manchete da notícia nas mensagens de commit.

- Publicar (criptografa a aula E atualiza o index): `python3 scripts/lesson_crypto.py publish /tmp/<data>.json --password "<SENHA>" --repo-root .`
- Ler uma aula existente (ex.: conferir pontos de gramática recentes): `python3 scripts/lesson_crypto.py decrypt lessons/<data>.json --password "<SENHA>"`
- Requer `pip install cryptography --break-system-packages` se a lib não estiver disponível.

## Publicação (passos da automação)

IMPORTANTE (ambiente Claude/Cowork): `git clone/push` direto para este repositório é BLOQUEADO
pelo proxy do sandbox. Use SEMPRE as ferramentas do conector MCP do GitHub
(`get_file_contents`, `push_files`) — elas rodam fora do sandbox. Repositório: `erickparente/meet-speak`, branch `main`.

1. Calcular a data de hoje em GMT-3: `TZ=America/Sao_Paulo date +%F`.
2. Idempotência (regra 9): `get_file_contents` em `lessons/<data>.json` — se o arquivo EXISTIR, parar (aula já publicada).
3. Baixar via `get_file_contents`: `LESSON_SPEC.md`, `scripts/lesson_crypto.py`, `scripts/validate_lesson.py`, `lessons/index.json` e as 2–3 aulas mais recentes; salvar localmente. Decriptar as aulas recentes (`lesson_crypto.py decrypt`) para checar temas e pontos de gramática já usados (regra 10).
4. Escolher e extrair a notícia (regras 1–7).
5. Gerar a aula PLAINTEXT em `/tmp/repo/<data>.json` seguindo este spec.
6. Rodar `python3 scripts/validate_lesson.py /tmp/repo/<data>.json` e corrigir qualquer erro (0 erros obrigatório).
7. Rodar `lesson_crypto.py publish` (acima) — gera `lessons/<data>.json` criptografada e atualiza `lessons/index.json` localmente.
8. Publicar os DOIS arquivos em um único commit com `push_files` (branch `main`, mensagem `Add lesson <data>` — sem manchete).
9. Verificar: baixar de volta `lessons/<data>.json` com `get_file_contents` e conferir que decripta corretamente; depois confirmar que a URL pública do site serve o novo arquivo (o deploy do Pages leva 1–3 min).
10. Apagar os arquivos plaintext temporários.
