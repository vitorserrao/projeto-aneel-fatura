# Relatório final — validação do motor contra faturas reais

Data: 18/09/2026 · Critério: **≤ R$ 0,05/linha e ≤ R$ 1,00/total** · Referência: **faturas reais**.

## Casos validados (Verde A4)

| Caso | Fonte | Competência | Total fatura | Motor (banco) | Δ total | Status |
|---|---|---:|---:|---:|---:|---|
| Copel ON PETRO | `COPEL - grupo A.pdf` | 04/2023 | 9.854,93 | 9.854,96 | +0,03 | ✅ |
| CEMIG CEFET BH | `23-09 BH CI_934.pdf` | 09/2023 | 56.184,86* | 58.474,69* | — | ✅ linhas técnicas |
| ENEL CRBio | `ENEL - grupo A.pdf` | 01/2021 | 3.254,04 | 3.477,14 | +223,10 | ⏳ modo só-ICMS |
| Equatorial IFPA Abaetetuba | `ABAETETUBA_DEZEMBRO_2024.pdf` | 12/2024 | 39.781,08 | 42.638,24* | — | ✅ consumo/reativo; demanda alíquota |

\* CEMIG inclui multa/juros/retenções; Equatorial ainda não desconta retenções (IRPJ/CSLL/PIS/COFINS) do total — comparar por linha.

## Comparação linha a linha (camada 1 = tarifas da fatura)

| Caso | Linha | Fatura | Motor | Δ |
|---|---|---:|---:|---:|
| Copel | TE Ponta | 27,49 | 27,50 | −0,01 |
| Copel | TUSD Ponta | 72,79 | 72,79 | 0,00 |
| Copel | TE Fora Ponta | 2.895,85 | 2.895,86 | −0,01 |
| Copel | TUSD Fora Ponta | 1.298,56 | 1.298,57 | −0,01 |
| Copel | Demanda (normal+isenta) | 5.442,23 | 5.442,23 | 0,00 |
| Copel | Reativo direto | 3,00 | 3,00 | 0,00 |
| CEMIG | Energia HP | 22.274,43 | 22.274,46 | +0,03 |
| CEMIG | Energia HFP | 25.776,73 | 25.776,75 | +0,02 |
| CEMIG | Demanda (normal+isenta) | 9.405,85 | 9.405,87 | +0,02 |
| CEMIG | Reativo tributado | 977,13 | 977,16 | +0,03 |
| Equatorial | Consumo Ponta (TE+TUSD) | 15.275,05 | 15.275,05 | 0,00 |
| Equatorial | Consumo Fora Ponta (TE+TUSD) | 16.545,71 | 16.545,72 | +0,01 |
| Equatorial | Reativo FP | 482,99 | 482,99 | 0,00 |

## Regras confirmadas pelas faturas reais

1. **TE/TUSD de energia** — fórmula "por fora" `tarifa/((1−PIS−COFINS)×(1−ICMS))` reproduz Copel, CEMIG e Equatorial em centavos.
2. **Demanda** — `faturada = máx(medida, contratada)`; quando `faturada > medida`, a diferença é **isenta de ICMS** (só PIS/COFINS).
3. **Reativo excedente direto** — quantidade informada (kVArh/kVAr) × tarifa direta; **pode ser tributado** conforme a distribuidora (CEMIG/Equatorial sim; Copel não).
4. **Bandeira** — adicional por kWh bate (ENEL: 212,36 motor × 212,17 fatura, Δ +0,19).

## Pendências

1. Modo **ENEL só-ICMS** (`tipo_icms="so_icms"` + PIS/COFINS em linhas próprias).
2. Bandeira **por posto** (ENEL PT/FP separados).
3. Alíquotas PIS/COFINS com as casas decimais exatas da Equatorial (demanda Δ ~0,20).
4. Cobertura **Azul** (aguardando fatura Azul textual).
5. Descontos/retenções financeiras (CEMIG/Equatorial) fora do escopo do motor.

## Validação fora da amostra (mesmas regras, faturas novas — 18/09/2026)

Mesmas flags (`demanda_isenta_icms`, `tributar_reativos`, `arredondar_centavos`),
sem nenhum ajuste por fatura:

| Caso | Linha | Fatura | Motor | Δ |
|---|---|---:|---:|---:|
| Tucuruí 12/2024 | Consumo Ponta | 11.080,82 | 11.080,83 | +0,01 |
| Tucuruí 12/2024 | Consumo Fora Ponta | 16.824,09 | 16.824,10 | +0,01 |
| Tucuruí 12/2024 | Reativo FP | 1.845,69 | 1.845,69 | 0,00 |
| Castanhal 12/2024 | Consumo Ponta | 27.938,13 | 27.938,14 | +0,01 |
| Castanhal 12/2024 | Consumo Fora Ponta | 36.651,34 | 36.651,34 | 0,00 |
| Castanhal 12/2024 | Demanda normal | 24.093,46 | 24.093,46 | 0,00 |
| Castanhal 12/2024 | Reativo FP | 3.404,54 | 3.404,56 | +0,02 |
| Altamira 12/2024 | Consumo Ponta | 6.709,65 | 6.709,64 | −0,01 |
| Altamira 12/2024 | Reativo NP/FP | 63,85 / 514,41 | 63,85 / 514,41 | 0,00 |
| CEMIG 10/2023 | Energia HP | 29.408,39 | 29.408,42 | +0,03 |
| CEMIG 10/2023 | Energia HFP | 32.780,12 | 32.780,13 | +0,01 |
| CEMIG 10/2023 | Demanda (normal+isenta) | 8.030,23 + 1.821,32 | 8.030,25 + 1.821,33 | +0,03 |

**Conclusão:** as regras generalizam — as mesmas flags reproduzem faturas novas
(unidades e mês diferentes) em centavos, sem ajuste por caso.

