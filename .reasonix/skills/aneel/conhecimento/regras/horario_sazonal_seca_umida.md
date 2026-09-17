# Horário-sazonal (seca/úmida) — pendência P5

## O fenômeno
Antes da REN ANEEL nº 1.000/2021, a tarifa de energia do Grupo A era
**horo-sazonal**: variava em duas dimensões.

1. **Sazonalidade diária (horária)** — continua existindo:
   - Ponta (~3 h no fim da tarde)
   - Fora de Ponta (demais 21 h)
2. **Sazonalidade anual (eliminada pela REN 1.000/2021)**:
   - Período **Úmido**: dezembro a abril (5 meses) — hidrelétricas, mais barato
   - Período **Seco**: maio a novembro (7 meses) — térmicas, mais caro

A combinação gerava **4 postos de consumo (kWh)**:

| Posto tarifário | Sigla | Período |
|---|---|---|
| Ponta Seca | PS | ponta + seco |
| Ponta Úmida | PU | ponta + úmido |
| Fora de Ponta Seca | FS | fora ponta + seco |
| Fora de Ponta Úmida | FU | fora ponta + úmido |

**O que mudou:** a REN 1.000/2021 eliminou a sazonalidade anual; restaram só
`Ponta` e `Fora de Ponta`. A variação anual foi substituída pelas **Bandeiras
Tarifárias** (Verde/Amarela/Vermelha), que sinalizam mês a mês o custo de
geração.

## Efeito no motor
O motor só reconhece os 2 postos atuais (`Ponta`, `Fora ponta`). Portanto:
- Datas **anteriores à REN 1.000/2021** podem ter tarifas só em postos
  horo-sazonais (seca/úmida) → ficam em `tarifas_nao_mapeadas` e **fora da
  fatura** (sem TE, no caso da CPFL JAGUARI A2 Azul em 2010-06).
- Datas **recentes** (ex.: 2024) usam só `Ponta`/`Fora ponto` → `tarifas_nao_mapeadas = 0`.

## Evidência real (consulta SQL)
CPFL JAGUARI, A2, Azul, `2010-06-01` (base "Tarifa de Aplicação", detalhe
"Não se aplica") → 12 tarifas vigentes:
- 4 mapeadas (`TUSD` Ponta/Fora ponta, kW e MWh)
- 8 não mapeadas:
  - TE: Ponta seca 177,55 / Ponta úmida 103,01 / Fora ponta seca 158,62 / Fora ponta úmida 92,04 (R$/MWh)
  - TUSD (energia MWh): Ponta seca / Ponta úmida / Fora ponta seca / Fora ponta úmida (todas 31,48)

Junho = período **seco**; a regra de mapeamento correta usaria apenas os
postos "seca" para a data.

## Pendência P5 (regra de mapeamento horo-sazonal)
A implementar: para datas anteriores à REN 1.000/2021, mapear
`Ponta seca`/`Fora ponta seca` ou `Ponta úmida`/`Fora ponta úmida` conforme o
mês da `data_referencia`, colapsando para `Ponta`/`Fora ponta` no motor.
Aguardando decisão de escopo (o MVP usa faturas recentes).

## Fonte
- Conhecimento do usuário (texto consolidado sobre horo-sazonalidade).
- REN ANEEL nº 1.000/2021 (eliminação da sazonalidade anual).
