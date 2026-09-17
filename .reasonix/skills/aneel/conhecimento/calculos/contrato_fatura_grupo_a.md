# Contrato da fatura — Grupo A (estrutura do Simulador de Fatura)

> **Origem:** projeto anterior (Kevin Wu), planilha
> `Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm`
> + regras oficiais (REN 1.000/2021) registradas em `ren1000_2021_faturamento.md`.
> Rastreabilidade: **Arquivo → Aba → Célula** quando aplicável.

## 1. Linhas de cobrança por modalidade

| Modalidade | Linhas |
|---|---|
| **Azul** (A) | TUSD demanda ponta (R$/kW), TUSD demanda fora ponta (R$/kW), TUSD energia ponta (R$/MWh), TUSD energia fora ponta (R$/MWh), TE ponta, TE fora ponta |
| **Verde** (A) | TUSD demanda **única** (R$/kW), TUSD energia ponta, TUSD energia fora ponta, TE ponta, TE fora ponta |
| **Convencional Binômia** (A) | TUSD demanda única (R$/kW), TUSD energia única (R$/MWh), TE única |

**Linhas adicionais** (para qualquer modalidade): ultrapassagem de demanda,
bandeira tarifária, reativos excedentes, CIP/COSIP, outros valores.

## 2. Parâmetros (defaults documentados no motor)

| Parâmetro | Default | Origem |
|---|---|---|
| Tolerância de ultrapassagem | **5%** (consumidor) | REN 1.000/2021, art. 301 |
| Fator de ultrapassagem | **2×** a tarifa de demanda | REN 1.000/2021 |
| Fator de potência limite | **0,92** | REN 1.000/2021 |
| PIS/COFINS/ICMS (tributos) | **opcionais** (base líquida por padrão) | Simulador (referência) |
| Fórmula de tributos | `tarifa / ((1 − PIS − COFINS) × (1 − ICMS))` | Simulador `Fatura - 1` célula `K20` — *referência, não oficial* |

## 3. Fórmulas por linha

| Linha | Fórmula | Origem |
|---|---|---|
| TUSD demanda (posto) | `demanda_faturavel = máx(contratada, medida) × tarifa` | REN 1.000/2021 |
| TUSD/energia e TE | `consumo_do_posto (MWh) × tarifa` | motor estrutural (A1) |
| Ultrapassagem | `[PAM − PAC × 1,05] × 2 × tarifa_demanda` (se > 0) | REN 1.000/2021 |
| Reativos | `reativo_excedente × tarifa_energia_tusd` (quando fp < 0,92) | REN 1.000/2021 + aproximação documentada |
| Bandeira | `consumo_total (kWh) × adicional (R$/kWh)` | Simulador |
| CIP/COSIP | valor fixo (R$) | Simulador |
| Outros | valor fixo (R$) | Simulador |
| Tributos (opcional) | `linha_tarifaria × fator` | Simulador (referência) |

## 4. Entrada (perfil do consumidor)

Campos do `Consumidor`/schema: distribuidora, subgrupo, classe, subclasse,
`detalhe` (padrão `Não se aplica` — resolve o P6), data de referência,
consumo ponta/fora ponta (kWh), demanda medida ponta/fora ponta (kW),
**demanda contratada ponta/fora ponta (kW)**, reativos (energia kVArh e
demanda kVAr por posto), bandeira (R$/kWh), CIP/COSIP (R$) e outros (R$).

## 5. Decisões aprovadas
- Filtro por `detalhe` no repositório (padrão `Não se aplica`) — elimina a
  soma dupla de linhas sobrepostas (`APE`/`SCEE` vs `Não se aplica`).
- Demanda faturável = máx(contratada, medida) — regra oficial.
- MVP: Grupo A (Azul, Verde, Convencional Binômia); tributos opcionais.
