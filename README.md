# Projeto de Análise e Otimização ACR × ACL

Projeto acadêmico (IFSC) com objetivo de desenvolver uma ferramenta computacional
para **enquadramento tarifário de consumidores potencialmente livres**, permitindo:

1. calcular o custo no ACR (Ambiente de Contratação Regulada);
2. comparar modalidades tarifárias aplicáveis;
3. identificar a modalidade de menor custo;
4. comparar o resultado com uma referência de preço do ACL;
5. calcular um **Preço de Indiferença (EPI)** simplificado;
6. analisar o histórico tarifário do ACR;
7. realizar uma projeção experimental da evolução do custo no ACR.

## Tecnologias

- Python
- PostgreSQL (via Docker)
- FastAPI
- Streamlit
- SQLAlchemy
- Pydantic
- pytest

## Arquitetura

A arquitetura é **modular e incremental**, com uma regra central:

> **O `core/` nunca depende de infraestrutura.**

O motor de cálculo tarifário é determinístico e executável sem PostgreSQL,
FastAPI, Streamlit, Docker ou APIs externas. As tarifas entram como dados e o
resultado é sempre reproduzível:

```
Tarifas entram como dados
        ↓
motor_calculo()
        ↓
Resultado do cálculo
```

Visão geral dos diretórios:

| Diretório  | Responsabilidade |
|------------|------------------|
| `core/`    | Regras de negócio puras (modelos, tarifas, cálculo, otimização, EPI) |
| `infra/`   | PostgreSQL, SQLAlchemy, repositórios e ingestão do dataset ANEEL |
| `services/`| Orquestração dos casos de uso |
| `schemas/` | Modelos Pydantic (entrada/saída) |
| `api/`     | FastAPI (HTTP, validação, chamada de services) |
| `app/`     | Streamlit (interface) |
| `forecast/`| Módulo experimental (baseline estatístico → modelos futuros) |
| `data/`    | Dataset ANEEL (raw / processed / samples) |
| `tests/`   | Testes unitários, de integração e fixtures |
| `scripts/` | Tarefas reproduzíveis (ingestão, validação com Excel) |
| `docs/`    | Premissas, regras, proveniência, validação — rastreabilidade |

Mais detalhes em [`docs/arquitetura.md`](docs/arquitetura.md).

## Estado atual

**Etapa 1 (bootstrap)** — estrutura de diretórios, ambiente, dependências,
PostgreSQL local, FastAPI com `/health`, Streamlit mínimo, estrutura de testes
e documentação inicial. **Nenhum cálculo tarifário foi inventado ou implementado.**

## Como executar

### 1. Banco de dados (Docker)

```bash
docker compose up -d
```

### 2. Ambiente Python

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# ou: .venv\Scripts\activate     # Windows (cmd/PowerShell)
pip install -r requirements.txt
```

### 3. Configuração

Copie `.env.example` para `.env` e ajuste os valores:

```bash
cp .env.example .env
```

### 4. API FastAPI

```bash
uvicorn api.main:app --reload
```

Endpoints:
- `GET /health` — verificação de saudade do serviço.

### 5. Interface Streamlit

```bash
streamlit run app/main.py
```

### 6. Testes

```bash
pytest
```

## Escopo do MVP

O MVP cobre: perfil do consumidor, consulta tarifária, cálculo ACR
(energia, demanda, TE, TUSD), otimização de modalidades (Azul, Verde,
Convencional quando aplicável), EPI simplificado e projeção experimental.

**Fora do MVP** (trabalhos futuros): bandeiras tarifárias, MMGD/SCEE, curva de
carga real/CTR, integração automática com ACL, PLD, CCEE, clustering, feature
importance, detecção de anomalias, MCA e Apriori.

## Validação

A ferramenta Excel `Recriar Faturas.xlsm` do projeto anterior é referência de
validação. O sistema **não depende** do Excel para funcionar; a comparação é um
experimento de validação documentado em [`docs/validacao_excel.md`](docs/validacao_excel.md).

## Documentação

- [`docs/arquitetura.md`](docs/arquitetura.md) — arquitetura, dependências entre camadas
- [`docs/premissas.md`](docs/premissas.md) — premissas e dúvidas a validar
- [`docs/regras_tarifarias.md`](docs/regras_tarifarias.md) — regras formais de cálculo
- [`docs/dataset.md`](docs/dataset.md) — dataset ANEEL, campos e proveniência
- [`docs/validacao_excel.md`](docs/validacao_excel.md) — plano de validação com o Excel
