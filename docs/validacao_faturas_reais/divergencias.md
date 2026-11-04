# Divergências encontradas nas faturas reais — classificação e correções

Critério: **≤ R$ 0,05 por linha e ≤ R$ 1,00 no total** (centavo a centavo).

## Classificação

| # | Divergência | Onde aparece | Causa | Status |
|---|---|---|---|---|
| 1 | Demanda cobrada cheia com ICMS | Copel, CEMIG, Equatorial | Parcela de demanda **contratada não utilizada** é **isenta de ICMS** (só PIS/COFINS) | ✅ Corrigido (`demanda_isenta_icms`) |
| 2 | Reativo excedente sem tributos | CEMIG, Equatorial | Essas distribuidoras **tributam** o reativo excedente; o motor não tributava | ✅ Corrigido (`tributar_reativos`) |
| 3 | Tarifa com só ICMS embutido | ENEL | ENEL usa `tarifa/(1−ICMS)` e cobra PIS/COFINS em linhas separadas | ⏳ Pendente (novo `tipo_icms`) |
| 4 | Bandeira separada por posto | ENEL | Fatura cobra bandeira PT e FP em linhas separadas | ⏳ Pendente |
| 5 | Alíquotas com mais casas decimais | Equatorial (demanda) | Fatura aplica PIS/COFINS com arredondamento próprio (~R$ 0,20) | 📝 Documentado |
| 6 | Fatura agrupada com multa/juros/retenções | CEMIG | Total da fatura tem itens financeiros fora do motor | 📝 Comparar só linhas técnicas |

## Correções aplicadas no motor (18/09/2026)

- `calcular_fatura(..., demanda_isenta_icms=False, tributar_reativos=False)`.
- `demanda_isenta_icms=True`: quando `faturada > medida`, a demanda vira duas linhas:
  - parcela **medida** → tributada normalmente;
  - parcela `faturada − medida` → **ISENTA ICMS** (fator `1/(1−PIS−COFINS)`).
- `tributar_reativos=True`: linhas de **REATIVOS** passam a receber PIS/COFINS/ICMS.
- Exposto na API: `POST /calculo/fatura?demanda_isenta_icms=true&tributar_reativos=true`.

## Validação após a correção (camada 1)

| Caso | Linha | Fatura | Motor corrigido | Δ |
|---|---|---:|---:|---:|
| Copel | Demanda normal + isenta | 3.411,60 + 2.030,63 = 5.442,23 | 3.411,63 + 2.030,60 = 5.442,23 | 0,00 |
| Copel | **Total** | **9.854,93** | **9.854,96** (reativo sem tributar) | **+0,03** |
| CEMIG | Demanda normal + isenta | 5.563,86 + 3.841,99 = 9.405,85 | 5.563,87 + 3.842,00 = 9.405,87 | +0,02 |
| CEMIG | Reativo tributado | 977,13 | 977,16 | +0,03 |
| Equatorial | Consumo Ponta | 15.275,05 | 15.275,05 | 0,00 |
| Equatorial | Consumo Fora Ponta | 16.545,71 | 16.545,72 | +0,01 |
| Equatorial | Reativo FP tributado | 482,99 | 482,99 | 0,00 |
| Equatorial | Demanda (alíquota) | 10.207,98 | 10.207,94 | −0,04 |

## Pendências para o próximo ciclo

1. Modo **ENEL só-ICMS** (`tipo_icms="so_icms"` + PIS/COFINS em linhas próprias).
2. Bandeira **por posto** (ENEL).
3. Ajuste fino de alíquotas PIS/COFINS com as casas decimais exatas de cada fatura.
