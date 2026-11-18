# Validação contra faturas reais (sprint feriados móveis)
Contraprova do `fatura_verde(...)` com tarifas do `TarifaRepository` vigentes na data de referência de cada fatura. Tolerância do total: `config.TOLERANCIA_VALIDACAO` = 1.0%.
## Casos
### CEMIG-D · Verde · 12/2023 (cemig_bh_cii112_verde_2023_12)

CEMIG-D · 12/2023 (total técnico fatura R$ 55,777.64, simulado R$ 56,658.87)

| Componente | Fatura real | Simulado | Diferença (R$) | Diferença (%) |
|---|---:|---:|---:|---:|
| Demanda ativa (com + sem ICMS) | 8,909.61 | 9,790.79 | +881.18 | +9.89% |
| Energia ativa ponta (TE+TUSD) | 17,873.59 | 17,873.62 | +0.03 | +0.00% |
| Energia ativa fora ponta (TE+TUSD) | 28,994.44 | 28,994.46 | +0.02 | +0.00% |
| Reativo excedente | 0.00 | 0.00 | +0.00 | — |
| Bandeira | 0.00 | 0.00 | +0.00 | — |
Total técnico: fatura R$ 55,777.64 × simulado R$ 56,658.87 → Δ R$ +881.23 (+1.58%)

Notas da fatura:
- A CEMIG imprime TE+TUSD de energia em uma linha única por posto; a comparação agrupa os componentes do fatura_verde da mesma forma.- CIP/COSIP R$ 40,45 não é componente do fatura_verde; fica fora da comparação.- Multa/serviços/retenções e GD estão fora do motor (comparar por linha técnica).- A fatura divide a demanda em parcela COM ICMS (200 kW) e parcela ISENTA de ICMS (200 kW) — pendência não implementada em fatura_verde.
### COPEL-DIS · Verde · 04/2023 (copel_a4_verde_2023_04)

COPEL-DIS · 04/2023 (total técnico fatura R$ 9,739.92, simulado R$ 10,185.69)

| Componente | Fatura real | Simulado | Diferença (R$) | Diferença (%) |
|---|---:|---:|---:|---:|
| TUSD demanda | 5,442.23 | 5,887.98 | +445.75 | +8.19% |
| TUSD energia ponta | 72.79 | 72.79 | +0.00 | +0.01% |
| TUSD energia fora ponta | 1,298.56 | 1,298.57 | +0.01 | +0.00% |
| TE energia ponta | 27.49 | 27.50 | +0.01 | +0.02% |
| TE energia fora ponta | 2,895.85 | 2,895.86 | +0.01 | +0.00% |
| Ultrapassagem | 0.00 | 0.00 | +0.00 | — |
| Reativo excedente | 3.00 | 3.00 | +0.00 | +0.00% |
| Bandeira | 0.00 | 0.00 | +0.00 | — |
Total técnico: fatura R$ 9,739.92 × simulado R$ 10,185.69 → Δ R$ +445.77 (+4.58%)

Notas da fatura:
- CIP/COSIP R$ 115,01 não é componente do fatura_verde; fica fora da comparação (total técnico = R$ 9.739,92).- A fatura divide a demanda em parcela COM ICMS (150,65 kW) e parcela ISENTA de ICMS (109,35 kW) — pendência não implementada em fatura_verde.
## Diferenças acima de 0,5% — causas

1. **Demanda contratada não utilizada isenta de ICMS** (Copel e CEMIG): a fatura divide a demanda em parcela com ICMS e parcela isenta (só PIS/COFINS). O `fatura_verde` aplica o fator cheio em toda a demanda faturável — regra ainda não implementada nesta função (o `calcular_fatura` já tem `demanda_isenta_icms`).
2. **Arredondamento por linha** (Copel, centavos): a fatura arredonda cada linha; o `fatura_verde` devolve valores sem arredondar.
3. **CIP/COSIP**: não é componente do `fatura_verde`; fica fora da comparação técnica.
