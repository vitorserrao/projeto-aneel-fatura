# Arquitetura

## Princípio central

> **O `core/` nunca depende de infraestrutura.**

O motor de cálculo é determinístico, executável sem PostgreSQL, FastAPI,
Streamlit, Docker ou APIs externas. As tarifas entram como dados de entrada e o
resultado é sempre reproduzível: **mesmas entradas + mesmas tarifas = mesmo
resultado.**

## Estrutura de diretórios

```
projeto-aneel/
├── core/                  # regras de negócio puras
├── infra/                 # PostgreSQL, SQLAlchemy, repositórios, ingestão
├── services/              # orquestração de casos de uso
├── schemas/               # modelos Pydantic (entrada/saída)
├── api/                   # FastAPI
├── app/                   # Streamlit
├── forecast/              # projeção experimental (opcional)
├── data/                  # dataset ANEEL (raw / processed / samples)
├── tests/                 # unit / integration / fixtures
├── scripts/               # tarefas reproduzíveis
└── docs/                  # rastreabilidade acadêmica
```

## Responsabilidade por camada

| Camada      | Responsabilidade | Não deve conter |
|-------------|------------------|-----------------|
| `core/`     | Regras tarifárias, matemática, modelos de domínio | Consultas de banco, HTTP, I/O |
| `infra/`    | Conexão, ORM, repositórios, ingestão de dados | Regras de negócio |
| `services/` | Orquestra casos de uso (repo → core → resultado) | Fórmulas tarifárias |
| `schemas/`  | Contratos Pydantic de entrada/saída | Regras de negócio |
| `api/`      | Endpoints HTTP, validação de schemas, chamada de services | Regras tarifárias |
| `app/`      | Interface (formulários, gráficos, resultados) | Regras tarifárias |
| `forecast/` | Preparação de série, baseline, avaliação | Núcleo obrigatório |

## Direção das dependências

```
api/  app/
   ↘    ↘
    services/
        ↓            ↓
      core/       infra/  (implementa repositórios)
        ↓            ↓
     (puro)      PostgreSQL
```

- `core/` conhece apenas modelos próprios e os dados de tarifa recebidos.
- `infra/` fornece persistência e conhece os modelos de dados, mas **não** regras tarifárias.
- `services/` orquestra: recebe input validado (schema), busca dados (repository),
  chama o `core/`, organiza o resultado.
- `api/` e `app/` são clientes de `services/`.

## `core/` — motor de cálculo puro

Fluxo conceitual:

```text
Tarifas entram como dados
        ↓
motor_calculo()
        ↓
Resultado do cálculo
```

O `core/` contém:
- `models.py` — modelos de domínio (tarifa, perfil de consumo, resultado).
- `tarifas.py` — representação e resolução de tarifas.
- `motor_calculo.py` — cálculo de energia, demanda, TE, TUSD e custo total ACR.
- `otimizador.py` — comparação de modalidades e seleção da menor custo.
- `epi.py` — Preço de Indiferença (EPI) simplificado.

A projeção (`core/projecoes.py` no esboço anterior) é tratada como experimental
e isolada em `forecast/`; se mantida no `core/`, não pode ser requisito do MVP.

## `services/` — exemplos de fluxo

```text
Service
   ↓
Repository → busca tarifa
   ↓
Core → calcula
   ↓
Service → organiza resultado
```

- `calculo_service.py`
- `otimizacao_service.py`
- `epi_service.py`
- `projecao_service.py`

## Regras de dependência a nunca violar

1. `core/` nunca importa `infra/`, `api/`, `app/`, banco, FastAPI, Streamlit, Docker ou APIs externas.
2. FastAPI e Streamlit não contêm regras de negócio.
3. Não inventar regras, valores ou fórmulas regulatórias — dúvidas vão para `docs/premissas.md`.
4. ML/forecast não é requisito para o MVP principal.
5. A validação contra o Excel é um experimento, nunca uma dependência de execução.
6. Determinismo: mesmas entradas + mesmas tarifas = mesmo resultado.
