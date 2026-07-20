---
name: verify
description: How to run and verify this repo (Meet&Speak + inteligêncIA hub) locally — static site, no build.
---

# Verificando o Meet&Speak / inteligêncIA

Site 100% estático (GitHub Pages), sem build e sem dependências. Duas superfícies:

- `/` — Meet&Speak, o curso de inglês (aulas em `lessons/*.json`).
- `/hub/` — inteligêncIA, a central de cursos e apps (catálogo em `hub/apps.json`).
- `/inteligencia/` — landing page do grupo; a vitrine de produtos lê `../hub/apps.json` (ativos = cards clicáveis, em-breve = faixa "Chegando em breve"; se o fetch falhar, mostra `#prodMsg` com link para a plataforma). URLs relativas do catálogo são resolvidas contra `../hub/`.

## Servir

```bash
python3 -m http.server 8765 --bind 127.0.0.1   # na raiz do repo
```

## Dirigir (headless)

Playwright com o Chromium pré-instalado do ambiente (não rodar `playwright install`):

```js
const { chromium } = require('playwright-core'); // npm i playwright-core no scratchpad
const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', // conferir versão com ls /opt/pw-browsers
  headless: true
});
```

Fluxos que valem dirigir no hub: cards renderizados de `apps.json` (ativos = `<a>`, em-breve = `<div>` com selo), busca (sem acento: "ingles" acha "inglês"), chips de categoria, favorito (persiste em `localStorage.hub_favs`), toggle de tema (chave `ms_theme`, compartilhada com o curso), atalho curso ⇄ hub, e o caminho de erro (bloquear `apps.json` num contexto com `serviceWorkers: 'block'` → mensagem amigável).

Fluxo "+ Adicionar produto": o formulário salva em `localStorage.hub_local_apps` (categorias novas em `hub_local_cats`) e o card aparece na hora com o selo "salvo neste navegador"; adicionar com o mesmo nome de um "em breve" do catálogo reaproveita o id (ativa o placeholder, sem duplicar). "Salvar no GitHub" copia o apps.json mesclado para o clipboard (testar com `grantPermissions(['clipboard-read'])` e `waitForEvent('popup')`) e abre `github.com/<owner>/<repo>/edit/main/hub/apps.json`. Locais idênticos a um app ativo do catálogo (mesmo id e url) são limpos no load.

## Pegadinhas

- Os service workers (`sw.js` e `hub/sw.js`) são network-first e cacheiam tudo que passa; para testar falha de rede, use um contexto novo com `serviceWorkers: 'block'`, senão o cache responde.
- Screenshot `fullPage` do Chromium headless às vezes perde emoji/badge abaixo da dobra (artefato de costura); para conferir visual, role até o elemento e capture o viewport.
- As aulas do curso são texto puro em `lessons/`; a página inicial do curso abre a aula mais recente do `lessons/index.json`.
