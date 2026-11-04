# Preço de Indiferença (PI) — fórmula implementada

> Status: **implementado** em `core/epi.py` (`calcular_pi` / `calcular_pi_meses`).
> Fórmula **adaptada de Lemos (2025)** — registrada como decisão metodológica
> do projeto (não é regra da ANEEL). Não altera as regras de faturamento do
> `core/motor_calculo.py`; este módulo apenas consome os totais de energia e as
> TE (sem tributos) da modalidade de menor custo no ACR.

## Definição

O **PI** (R$/MWh) é o preço da energia no ACL que iguala o custo de energia
entre ACR e ACL. Se o preço real do ACL for menor que o PI, o ACL é vantajoso;
se for maior, o ACR é vantajoso (considerando apenas energia + custos do ACL
informados).

## Entradas

| Símbolo | Descrição | Unidade | Padrão |
|---|---|---|---|
| `e_ponta` | Energia no posto ponta | MWh | — (obrigatório) |
| `e_fora_ponta` | Energia no posto fora de ponta | MWh | — (obrigatório) |
| `te_ponta` | TE ponta sem tributos (modalidade de menor custo no ACR) | R$/MWh | — (obrigatório) |
| `te_fora_ponta` | TE fora de ponta sem tributos (modalidade de menor custo no ACR) | R$/MWh | — (obrigatório) |
| `pis` | Alíquota de PIS | fração | — (informado pelo usuário) |
| `cofins` | Alíquota de COFINS | fração | — (informado pelo usuário) |
| `icms` | Alíquota de ICMS | fração | — (informado pelo usuário) |
| `bandeira` | Bandeira tarifária | R$/MWh | `0` |
| `encargos` | Encargos do ACL por energia (ex.: ESS) — custo do lado ACL, não se soma à TE | R$/MWh | `0` |
| `k` | Perdas na migração ao ACL | fração | `0,03` |
| `opex_mensal` | OPEX do ACL | R$/mês | `0` |
| `capex` | CAPEX do ACL | R$ | `0` |
| `horizonte_meses` | Horizonte de amortização do CAPEX | meses | `60` |

## Fórmula (um mês)

```
E          = e_ponta + e_fora_ponta
C_TE       = e_ponta·te_ponta + e_fora_ponta·te_fora_ponta
C_E_ACR    = (C_TE + E·bandeira) / ((1 − pis − cofins)·(1 − icms))
CUSTOS_ACL = opex_mensal + capex / horizonte_meses + E·(1+k)·encargos
BASE_ACL   = E·(1 + k) / (1 − icms)
PI         = (C_E_ACR − CUSTOS_ACL) / BASE_ACL
```

> A tributação aqui é a forma **multiplicativa** `(1 − PIS − COFINS) × (1 − ICMS)`,
> conforme a especificação da fórmula adaptada de Lemos (2025). O motor de
> faturamento continua usando a sua própria regra de tributos — este módulo
> **não** altera `motor_calculo.py`.

## Vários meses

Somar `C_E_ACR`, `CUSTOS_ACL` e `BASE_ACL` de **todos** os meses antes de
dividir:

```
PI = (Σ C_E_ACR − Σ CUSTOS_ACL) / Σ BASE_ACL
```

**Não** calcular nem fazer média dos PIs mensais. `core/epi.py` expõe
`calcular_pi_meses(meses, ...)` para esse caso.

## Fonte do `k` (perdas na rede básica)

O `k` representa as **perdas da rede básica rateadas ao consumo** na
contabilização da CCEE — na migração ao ACL o consumidor continua pagando o
uso da rede, e a CCEE ajusta o consumo medido por um fator de perdas.

- **Fonte primária (regra):** CCEE — Regras de Comercialização, Módulo
  "Medição Contábil": as perdas da rede básica são rateadas **50% geração /
  50% consumo**, com fator de consumo
  `XP_CLF = (TOT_CP + TOT_P/2) / TOT_CP` (fator multiplicativo sobre o
  consumo medido).
- **Histórico publicado:** o InfoMercado (CCEE) traz mensalmente a tabela
  "Perdas na rede básica" com o **Fator de perdas do consumo (%)**. Na
  tabela de jan/2012–jan/2013 os valores apurados variaram entre **~1,9% e
  ~2,7%** (ex.: jan/13 = 2,11%; dez/12 = 2,22%).
- **Conclusão:** o padrão `k = 0,03` (3%) é uma **aproximação razoável e
  levemente conservadora** frente ao histórico apurado (~2–2,7%). O valor
  exato varia mês a mês (geração, consumo e perdas apurados no SIN) e
  permanece parametrizável em `calcular_pi`.

## Validações de entrada

- Alíquotas `pis`, `cofins`, `icms` ∈ `[0, 1)` e `(1 − pis − cofins) > 0`.
- Consumo total `e_ponta + e_fora_ponta > 0` (parcelas não negativas).
- `te_ponta`, `te_fora_ponta`, `bandeira`, `k`, `opex_mensal`, `capex` ≥ 0.
- `horizonte_meses` inteiro > 0.

Entrada inválida levanta `ValueError` com mensagem em português.

## Aviso de PI ≤ 0

Se `PI ≤ 0`, o resultado preenche o campo `aviso`: o custo ACR de energia não
cobre os custos do ACL no horizonte informado (ACL vantajoso mesmo com preço de
energia zero ou negativo). O valor é retornado mesmo assim.

## Retorno

`core.models.ResultadoPI` (dataclass congelada):

| Campo | Descrição |
|---|---|
| `pi` | Preço de Indiferença (R$/MWh) |
| `e` | Energia total (MWh) |
| `c_te` | Custo de energia TE (R$) |
| `c_e_acr` | Custo de energia no ACR com tributos (R$) |
| `custos_acl` | Custos mensais do ACL (R$/mês) |
| `base_acl` | Base de comparação do ACL (MWh) |
| `aviso` | Mensagem quando `pi ≤ 0` (senão `None`) |
| `meses` | Quantidade de meses agregados |

## Casos de referência (testes em `tests/unit/test_core_epi.py`)

1. `e_ponta=30`, `e_fora_ponta=220`, `te_ponta=450`, `te_fora_ponta=280`,
   `pis+cofins=0,0374`, `icms=0,17`, `k=0,03`, sem OPEX/CAPEX → **PI ≈ 302,98**.
2. Mesmo caso com `opex=1000`, `capex=20000`, `horizonte=60` → **PI ≈ 298,68**.
3. Omitir OPEX e CAPEX dá o mesmo resultado que informá-los iguais a 0.

## De onde vêm as entradas (estado atual do sistema)

| Entrada | Já existe no sistema? | Onde |
|---|---|---|
| `e_ponta`, `e_fora_ponta` | ✅ sim | `schemas/consumidor.py` → `consumo_ponta_kwh` / `consumo_fora_ponta_kwh` (converter kWh → MWh) |
| `te_ponta`, `te_fora_ponta` | ✅ sim | tarifas TE sem tributos da modalidade de menor custo (repo `infra/repositories/tarifa_repository.py` + `services/otimizacao_service.py` já escolhem a melhor modalidade) |
| `bandeira` | ✅ sim | bandeira vigente (`api`/motor já tratam bandeira) |
| `pis`, `cofins`, `icms` | ✅ sim (entrada do usuário) | o motor já recebe alíquotas de tributos em `services/calculo_service.py` |
| `k` (perdas) | ✅ sim | `schemas/epi.py` → campo `k` (POST `/api/epi/calcular`) |
| `encargos` (ESS) | ✅ sim | `schemas/epi.py` → campo `encargos` (lado ACL) |
| `opex_mensal`, `capex`, `horizonte_meses` | ✅ sim | `schemas/epi.py` → campos `opex_mensal`, `capex`, `horizonte_meses` |

## Próximos passos (não fazem parte deste módulo)

1. ~~Expor `k`, `opex_mensal`, `capex`, `horizonte_meses` em `schemas/` e na API.~~ ✅ feito (`schemas/epi.py` + `POST /api/epi/calcular`).
2. ~~Ligar `services/epi_service.py` ao `core.epi.calcular_pi`.~~ ✅ feito.
3. Criar a **UI** do PI (Streamlit/frontend) usando os campos novos.
4. (Opcional) aceitar demanda/contrato no perfil do PI para a escolha
   automática da modalidade de menor custo refletir o custo total completo.

## Referências

- **Lemos (2025)** — TCC de origem da fórmula do Preço de Indiferença
  (adaptada neste projeto; ver seção "Fórmula").
- **CCEE — Regras de Comercialização, Módulo "Medição Contábil"**
  (versão 2026.5.2): rateio 50/50 das perdas da rede básica e fator de
  consumo `XP_CLF = (TOT_CP + TOT_P/2) / TOT_CP`.
  https://www.ccee.org.br/documents/80415/31256427/02%20-%20Medição%20Contábil_2026.5.2_MAI.pdf
- **CCEE — InfoMercado** (publicação mensal): tabela "Perdas na rede
  básica" com o fator de perdas do consumo (%) histórico; ex. jan/2012–jan/2013
  entre ~1,9% e ~2,7% (InfoMercado abr/2013).
  https://www.cogen.com.br/content/upload/1/documentos/paper/2013/Infomercado_abr13.pdf
