# Meet&Speak

Plataforma pessoal de estudo de inglês (nível B1–B2): todos os dias às 8h (horário de Brasília),
uma automação busca uma notícia real recém-publicada em um grande veículo de língua inglesa
(BBC, CNN, Reuters, Guardian, AP…) e constrói sobre ela a aula do dia com
**Reading, Listening, Writing, Speaking e Grammar** (~20 minutos).

- O texto da notícia é sempre reproduzido **sem modificações**, com crédito e link para a fonte.
- As aulas ficam **criptografadas** (AES-256-GCM); o site pede uma senha ao abrir.
- `index.html` — o site (não precisa de servidor além do GitHub Pages).
- `lessons/index.json` — índice das aulas, criptografado (mais recente primeiro).
- `lessons/YYYY-MM-DD.json` — uma aula por dia, criptografada.
- `LESSON_SPEC.md` — o contrato que a automação diária segue.
- `scripts/validate_lesson.py` — valida uma aula antes da publicação.
- `scripts/lesson_crypto.py` — criptografa/publica aulas e atualiza o índice.

Áudio do Listening/Speaking: gerado no navegador (Web Speech API) lendo o texto original.
Reconhecimento de fala do Speaking: Chrome/Edge.
