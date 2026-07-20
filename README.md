# Meet&Speak

## Meet&Hub — a central de cursos e aplicativos (`hub/`)

A pasta `hub/` é a **porta de entrada da plataforma**: uma página única que reúne todos os
cursos de idiomas (inglês, italiano…) e aplicativos (planejador de eventos, treinos de
corrida…) criados no Lovable, no Claude ou em qualquer outro lugar. Abra em
`https://<seu-usuario>.github.io/meet-speak/hub/` — também é um PWA instalável, com busca,
filtro por categoria e favoritos.

**Para adicionar um app novo:** publique o app na plataforma onde ele foi criado (no Lovable:
*Publish* → copie a URL; no Claude: publique o artifact/site e copie o link), edite
`hub/apps.json` e acrescente um bloco na lista `"apps"` com `nome`, `descricao`, `emoji`,
`categoria`, a `url` publicada e `"status": "ativo"`. Salve (*Commit changes*) e ele aparece
no hub. Apps ainda não publicados ficam com `"status": "em-breve"`. Categorias novas e o
nome da plataforma também se editam nesse mesmo arquivo.

- `hub/index.html` — a página do hub (lê o catálogo e desenha os cards).
- `hub/apps.json` — o catálogo: plataforma, categorias e lista de apps.
- `hub/manifest.json`, `hub/sw.js`, `hub/icon*.svg` — PWA do hub (instalação + offline).

## Meet&Speak — o curso de inglês

Plataforma pessoal de estudo de inglês (nível B1–B2): todos os dias às 8h (horário de Brasília),
uma automação busca uma notícia real recém-publicada em um grande veículo de língua inglesa
(BBC, CNN, Reuters, Guardian, AP…) e constrói sobre ela a aula do dia com
**Reading, Listening, Writing, Speaking e Grammar** (~20 minutos).

- O texto da notícia é sempre reproduzido **sem modificações**, com crédito e link para a fonte.
- As aulas ficam **criptografadas** (AES-256-GCM); o site pede uma senha ao abrir.
- A partir da 2ª aula, cada dia abre com **revisão espaçada**: lacunas com o vocabulário das aulas de 1, 3 e 7 dias atrás.
- O Writing tem um botão que **copia um prompt de correção** pronto para colar no Claude; no Speaking, onde não há reconhecimento de fala (ex.: iPhone), dá para **gravar a própria voz** e comparar com o áudio original.
- O site é um **PWA**: instalável no celular/desktop, e a última aula aberta funciona offline.
- `index.html` — o site (não precisa de servidor além do GitHub Pages).
- `lessons/index.json` — índice das aulas, criptografado (mais recente primeiro).
- `lessons/YYYY-MM-DD.json` — uma aula por dia, criptografada.
- `LESSON_SPEC.md` — o contrato que a automação diária segue.
- `config.json` — **nível-alvo das aulas** (A1 · A2 · B1 · B2 · C1 · C2): edite este arquivo para subir ou baixar o nível; a notícia e os exercícios do dia seguinte já vêm no nível novo.
- `scripts/validate_lesson.py` — valida uma aula antes da publicação.
- `scripts/lesson_crypto.py` — criptografa/publica aulas e atualiza o índice (com tema, gramática e vocabulário do dia).
- `manifest.json`, `sw.js`, `icon.svg`, `icon-maskable.svg` — PWA (instalação + offline).

Áudio do Listening/Speaking: gerado no navegador (Web Speech API) lendo o texto original.
Reconhecimento de fala do Speaking: Chrome/Edge.
