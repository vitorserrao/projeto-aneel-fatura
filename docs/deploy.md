# Deploy — front (Vercel) + back (FastAPI + Postgres)

> Provedores recomendados (decisão de infra registrada em 09/10/2026):
> **Vercel** para o frontend estático (React/Vite) e **Render + Neon** (ou o
> Postgres do próprio Render) para a API FastAPI e o banco. As instruções
> abaixo são agnósticas e valem para Railway/Fly.io com pequenas adaptações.

## 1. Frontend (Vercel)

O frontend é um SPA Vite puro (`frontend/`), sem necessidade de
funções serverless — a camada Gemini/express do template não é usada.

1. Importe o repositório `vitorserrao/SIMULADOR-FATURA` no Vercel
   (framework preset: **Vite**; build: `npm run build`; output: `dist`).
2. Configure a variável de ambiente no projeto Vercel:
   - `VITE_API_BASE` = URL pública da API, ex.: `https://api-projeto-aneel.onrender.com`
     (sem barra no final).
3. O `vite.config.ts` não precisa de proxy em produção. Em dev local, a API
   default é `http://127.0.0.1:8000` (definida em `src/lib/api.ts`).
4. Rewrites SPA (caso o Vercel peça `vercel.json` na raiz do front):

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

## 2. Backend (Render/Railway/Fly.io)

1. Hospede `Dockerfile.api` (build da imagem com uvicorn).
2. Variáveis de ambiente do serviço:
   - `DATABASE_URL` = Postgres gerenciado (Neon/Render): carregado o dataset
     ANEEL (ver scripts de ingestão do projeto).
   - `FRONTEND_ORIGINS` = domínio(s) do front separados por vírgula, ex.:
     `https://simulador-fatura.vercel.app` (CORS implementado em `api/main.py`).
   - `ANEEL_API_BASE` (opcional) se o front consultar outros ambientes.
3. Libere o acesso do serviço ao banco (Neon: connection string com TLS;
   Render Postgres: mesma rede interna).

## 3. Banco (Postgres + dataset ANEEL)

1. Crie o banco `projeto_aneel` no provedor.
2. Rode a migração/ingestão uma única vez (o pipeline do projeto usa
   SQLModel/SQLAlchemy; conferir `scripts/` de ingestão e `infra/`).
3. O banco deve conter `tarifa_aplicacao_componente`, `distribuidora`,
   `bandeira_valor` (ou o schema equivalente usado pela ingestão atual).

## 4. Smoke test de produção

```bash
curl https://api-projeto-aneel.onrender.com/health
curl "https://api-projeto-aneel.onrender.com/api/distribuidoras"
curl -X POST "https://api-projeto-aneel.onrender.com/api/calculo/fatura?modalidade=Verde&base_tarifaria=Tarifa%20de%20Aplica%C3%A7%C3%A3o" \
  -H "Content-Type: application/json" \
  -d '{"distribuidora":"COPEL-DIS","subgrupo":"A4","classe":"Não se aplica","subclasse":"Não se aplica","detalhe":"Não se aplica","data_referencia":"2023-03-15","consumo_ponta_kwh":55,"consumo_fora_ponta_kwh":9094,"demanda_medida_unica_kw":150.65,"demanda_contratada_unica_kw":260}'
```

## 5. Dev local

- Postgres: `docker compose up -d` (porta 5433) — já configurado no projeto.
- API: `./.venv/Scripts/python.exe -m uvicorn api.main:app --reload` (porta 8000).
- Front: `cd frontend && npm install && npm run dev` (porta 3000, host 0.0.0.0).
- O CORS padrão já aceita `localhost:3000/5173` em dev.
