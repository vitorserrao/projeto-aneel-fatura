# Passo a passo — entrega do banco + API para o professor (laboratório)

> Use este roteiro **amanhã, antes e durante a reunião** com o professor.

## 1. O que entregar (checklist)

| Item | Onde está | Obrigatório? |
|---|---|---|
| Dump do banco | `infra_lab/projeto_aneel.dump` | ✅ sim (é o "banco de dados") |
| API somente leitura | `api/main_lab.py` | ✅ sim |
| Imagem da API | `Dockerfile.api` | ✅ sim |
| Compose do lab | `docker-compose.lab.yml` | ✅ sim |
| Requisitos da API | `infra_lab/requirements.lab.txt` | ✅ sim |
| Configuração de exemplo | `infra_lab/.env.lab.example` | ✅ sim |
| Instruções para o professor | `docs/infra_lab.md` | ✅ sim |

Você pode entregar **a pasta do projeto inteira** (mais simples) ou só esses arquivos
num zip (o professor só precisa deles para o servidor do lab).

## 2. Antes da reunião (fazer em casa)

1. **Garantir que o Docker Desktop está rodando** (ícone da baleia ativo).
2. **Regenerar o dump** (deixa o banco no estado mais atual):
   ```bash
   docker exec projeto-aneel-db pg_dump -U postgres -Fc projeto_aneel > infra_lab/projeto_aneel.dump
   ```
   Conferir que o arquivo tem ~27 MB:
   ```bash
   ls -la infra_lab/projeto_aneel.dump
   ```
3. **Validar o dump:**
   ```bash
   docker cp infra_lab/projeto_aneel.dump projeto-aneel-db:/tmp/projeto_aneel.dump
   MSYS_NO_PATHCONV=1 docker exec projeto-aneel-db pg_restore --list //tmp/projeto_aneel.dump | head
   ```
   Deve listar os objetos (TOC Entries ~55) sem erro.
4. **Testar a API do lab localmente** (sem subir o Compose, só a app):
   ```bash
   .venv/Scripts/python.exe -m pytest tests/integration -q
   ```
   (ou subir o Compose do lab e bater em `/health` e `/api/tarifas` — ver `docs/infra_lab.md`).

## 3. Como passar para o professor (recomendado: tar só com o essencial)

NÃO precisa mandar o projeto inteiro (evita levar `.env`, testes, app Streamlit e
logs). Gere um tar.gz só com o que a API do lab usa:

```bash
tar -czf aneel_lab_entrega.tar.gz   --exclude='.venv' --exclude='.git' --exclude='__pycache__'   --exclude='data/raw/*.csv' --exclude='.reasonix'   --exclude='api/routers/calculo.py'   --exclude='api/routers/epi.py'   --exclude='api/routers/otimizacao.py'   --exclude='api/routers/projecao.py'   api core infra schemas scripts   Dockerfile.api docker-compose.lab.yml   infra_lab docs/infra_lab.md
```

Entregue o `aneel_lab_entrega.tar.gz` (já contém o dump dentro de `infra_lab/`).

> Sobre o código de cálculo: ele **não precisa ser separado manualmente** — a
> API do lab (`api/main_lab.py`) **não monta** as rotas de cálculo. No tar acima,
> os routers de cálculo/EPI/otimização/projeção são excluídos por precaução, então
> nem código de cálculo vai junto na pasta `api/routers/`.

## 4. O que o professor precisa ter/instalar

- **Docker** (Docker Desktop ou Docker Engine) na máquina do laboratório.
- Nada de Python/Postgres instalado manualmente — o Compose cuida de tudo.

## 5. O professor roda apenas isto (passe esta parte pra ele)

```bash
cp infra_lab/.env.lab.example .env.lab
docker compose -f docker-compose.lab.yml --env-file .env.lab up -d --build
```

Depois testa:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/distribuidoras
```

## 6. Testar juntos na máquina do lab

1. `docker compose -f docker-compose.lab.yml --env-file .env.lab logs restore` → conferir que o dump foi restaurado.
2. `curl http://localhost:8000/health` → `{"status":"ok"}`.
3. `curl http://localhost:8000/api/modalidades` → lista de modalidades.
4. `curl "http://localhost:8000/api/tarifas?sig_agente=EQUATORIAL%20PA&subgrupo=A4&modalidade=Verde&data=2024-12-15"` → tarifas reais.

## 7. Informações para repassar aos alunos

- URL base: `http://IP_DO_SERVIDOR_DO_LAB:8000`
- Endpoints: `/health`, `/api/distribuidoras`, `/api/tarifas`, `/api/tarifas/te-tusd`,
  `/api/subgrupos`, `/api/modalidades`, `/api/classes`, `/api/componentes`,
  `/api/bases-tarifarias`, `/api/acessantes`, `/api/bandeira`, `/api/bandeiras`.
- Exemplos prontos: ver `docs/infra_lab.md`.

## 8. Perguntas para confirmar com o professor

1. Qual o **IP/hostname** do servidor do lab? (para divulgar aos alunos)
2. A porta **8000** está livre? (senão, mudar `API_PORT` no `.env.lab`)
3. O **firewall/rede** do lab permite acesso à porta da API?
4. Quem vai **manter/reiniciar** o Docker lá? (o Compose já sobe sozinho com `restart: unless-stopped`)
5. Precisa de **senha/controle de acesso**? (hoje está aberto na rede interna, como combinado)
