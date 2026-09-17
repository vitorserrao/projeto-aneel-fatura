# Projeto anterior — Casos de validação (ground truth de referência)

> Estes casos virão do projeto anterior; **NÃO são automaticamente corretos** — servem como referência para comparar com o novo sistema e com as regras oficiais.

## CASO 1 — Fatura Grupo A (Verde, Amazonas Energia, 2010)

**Entrada:**
- Distribuidora: `Amazonas Energia`
- Subgrupo: `A4`; Modalidade: `Verde`
- REH: `Nº 1.077, de 26/10/2010` (vigência 11/01/2010 a 31/10/2011)
- Leitura anterior: `01/11/2010`; Leitura atual: `01/12/2010`
- Demanda faturada: P=100 kW, FP=100 kW; Contratada: P=100, FP=100
- Consumo: P=354 kWh, FP=3891 kWh
- Reativos: energia P=36 kVArh, FP=1510 kVArh; demanda 0
- Tributos: PIS 0,25%, COFINS 1,15%, ICMS 25%, CIP 133,20
- Outros valores: 50,00

**Parâmetros:**
- Limite B: 112,5 kVA; Limite Conv.Binômia: 300 kW
- % interm./FP: 0,10; % mês atual×anterior: 0

**Cálculo (regra):**
- `tarifa_com_imposto = tarifa / ((1 − PIS − COFINS) × (1 − ICMS))`
- `valor = quantidade × tarifa_com_imposto` para cada linha (demanda, consumo, TE, bandeira, reativos, CIP, outros).

**Resultado esperado (referência):**
- O total por modalidade é calculado comparando Verde/Azul/Convencional/Monômia/Branca. Os valores exatos dependem das tarifas da aba "Dados das tarifas" (Amazonas Energia REH 1.077). **A registrar os números após abrir o Excel** (valores dinâmicos/macro).

**Fonte:** `Simulador de Fatura/Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm` → abas `Painel Inicial` e `Fatura de Energia - 1` (linhas 20–55).

---

## CASO 2 — Cálculo de %TUSD SCEE (GDII) por subgrupo/modalidade

**Entrada (contexto):**
- Subgrupo/modalidade/posto/classe/subclasse (ex.: A3a Verde Ponta; B1 Branca Ponta; A2 Azul).

**Regra:**
- `%TUSD = TUSD sem componentes do Fio A / TUSD total`.

**Resultados de referência (extraídos do calculador):**
| Contexto | %TUSD (GDII) |
|---|---|
| A2 Azul (NA/NA) P e FP | 1,000000 (sem desconto) |
| A3 Azul | 1,000000 |
| A3a Azul | 1,000000 |
| A3a Verde P | 0,817754 |
| A4 Verde P | 0,817754 |
| B1 Branca P | 0,836067 |
| B1 Convencional | 0,882286 |
| B1 Convencional Baixa Renda | 0,826126 |
| B2 Branca P | 0,832795 |
| B3 Branca P | 0,827882 |
| B4a Iluminação Pública | 0,882287 |
| B4b Iluminação Pública | 0,882285 |

**Fonte:** `Calculador de Porcentagens SCEE/Calculador de Porcentagens - SCEE - Macro Habilitada.xlsm` → aba `Porcentagens SCEE`.

---

## CASO 3 — Devolutiva de fatura SCEE (Celesc, B1)
- Arquivos: `Faturamento Consumidores SCEE/Faturas no SCEE - cálculos e contas matemáticas/Devolutiva das Faturas da Celesc.xlsx` (abas `B1-SCEE-CELESC-dis - dez.2023` e `jan.2024`).
- Utilizar como caso real de fatura SCEE para validar componentes/percentuais quando o novo sistema suportar SCEE.

## Observação sobre rastreabilidade
- O projeto anterior utiliza nomes definidos/macros; valores finais exatos dependem de recalcular no Excel original. Estes casos valem pela **estrutura** e pela **regra**, e os resultados numéricos devem ser reconferidos abrindo os arquivos originais.
