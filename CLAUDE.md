# CLAUDE.md — PNW Outdoor Adventures

Guia para Claude Code en este sitio. Generado por site-pipeline.

## Que es
Sitio Astro + Cloudflare Pages, preset `content`. Dominio: pnwoutdooradventures.com.

## Stack
- Astro 4 + Tailwind, deploy a CF Pages via GitHub (nunca wrangler deploy).
- SEO cableado en `src/layouts/BaseLayout.astro` (title/description/canonical/OG).

## Features de este preset
- Blog: si
- Formulario: none
- Schema.org: Article, FAQPage, BreadcrumbList
- Backend: no

## Reglas
- Cada pagina usa BaseLayout con title <=60 (unico), description 120-160, y `path` canonico coherente con trailingSlash="always".
- Un solo <h1> por pagina; jerarquia sin saltos.
- No credenciales en el repo (ver `.env.example`, `secrets.example`).

## Flujo
1. Editar diseno/contenido (LLM).
2. `npm run build` (astro build -> dist/).
3. `site-pipeline build dist --csp-hashes` (genera _headers con CSP).
4. `site-pipeline qa dist` (gate; solo este comando sale !=0).
5. `site-pipeline deploy` (git push -> CF Pages).
6. `site-pipeline verify <url>` (post-deploy).
