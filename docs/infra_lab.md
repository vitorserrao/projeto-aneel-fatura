# Infraestrutura do laboratório — banco + API de consulta

Pacote para rodar no laboratório (Docker) e permitir que os alunos consultem o
banco de tarifas ANEEL **sem depender do notebook do projeto**.

## O que está incluído

| Arquivo | Papel |
|---|---|
| `infra_lab/projeto_aneel.dump` | Dump do PostgreSQL (formato custom, ~27 MB) |
| `api/main_lab.py` | API **somente leitura** (consultas) |
| `Dockerfile.api` | Imagem da API |
| `docker-compose.lab.yml` | Sobe `db` + `restore` + `api` |
| `infra_lab/.env.lab.example` | Template de configuração |

## Passo a passo (máquina do professor)

1. Instalar o **Docker** (Docker Desktop ou engine) e garantir que está rodando.
2. Copiar a pasta do projeto para a máquina do laboratório (pode ser um zip).
3. Criar o arquivo de ambiente:
   ```bash
   cp infra_lab/.env.lab.example .env.lab
   ```
4. Subir tudo (a primeira subida restaura o dump automaticamente):
   ```bash
   docker compose -f docker-compose.lab.yml --env-file .env.lab up -d --build
   ```
5. Conferir a restauração:
   ```bash
   docker compose -f docker-compose.lab.yml --env-file .env.lab logs restore
   ```
   A última linha deve terminar sem erro (o serviço usa `|| true` para não
   quebrar em subidas repetidas).
6. Testar a API:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/api/distribuidoras
   ```

Os alunos acessam por `http://IP_DA_MAQUINA_DO_LAB:8000/...` (porta configurável
em `.env.lab`, `API_PORT`).

## Endpoints disponíveis (todos GET, somente leitura)

| Endpoint | Descrição |
|---|---|
| `/health` | status da API |
| `/api/distribuidoras` | lista de distribuidoras |
| `/api/tarifas?sig_agente=...&data=...&subgrupo=...&modalidade=...&base_tarifaria=...&componente=...` | tarifas vigentes por filtros |
| `/api/tarifas/te-tusd?sig_agente=...&subgrupo=...&modalidade=...&data=...` | TE e TUSD de um perfil (sem somar) |
| `/api/subgrupos` | subgrupos disponíveis |
| `/api/modalidades` | modalidades tarifárias presentes no banco |
| `/api/classes` | classes tarifárias |
| `/api/componentes` | componentes tarifários (TE/TUSD) |
| `/api/bases-tarifarias` | bases tarifárias |
| `/api/acessantes` | acessantes (estudos de geração/GD) |
| `/api/bandeira?competencia=AAAA-MM-DD` | bandeira vigente na competência |
| `/api/bandeiras?competencia=AAAA-MM-DD` | opções de bandeira e valores |

## Exemplos para os alunos

```bash
# Todas as distribuidoras
curl "http://IP_DO_LAB:8000/api/distribuidoras"

# Tarifas TUSD da CEMIG-D, A4, Verde, em 01/09/2023
curl "http://IP_DO_LAB:8000/api/tarifas?sig_agente=CEMIG-D&subgrupo=A4&modalidade=Verde&data=2023-09-15&componente=TUSD"

# TE e TUSD (sem somar) de um perfil
curl "http://IP_DO_LAB:8000/api/tarifas/te-tusd?sig_agente=EQUATORIAL%20PA&subgrupo=A4&modalidade=Verde&data=2024-12-15"

# Bandeira vigente
curl "http://IP_DO_LAB:8000/api/bandeira?competencia=2024-12-15"
```

## Backup / manutenção

- Os dados ficam no volume Docker `pgdata_lab`.
- Backup:
  ```bash
  docker exec aneel-lab-db pg_dump -U postgres -Fc projeto_aneel > backup.dump
  ```
- Restauração manual:
  ```bash
  docker exec -i aneel-lab-db pg_restore -U postgres -d projeto_aneel --clean --if-exists < backup.dump
  ```
