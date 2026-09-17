# Caso de validação — Conta real Copel A4 Verde (03/2023)

> Registro da comparação entre uma **conta real de energia** (DANF3E/NF3E da
> Copel Distribuição) e o resultado do nosso simulador.
> Arquivo de origem: `clipboard-20260916-114548.262904-000003.pdf` (anexado).
> Data do teste: 2025-09-16.

## 1. Dados da conta real

| Campo | Valor |
|---|---|
| Distribuidora | Copel Distribuição S.A. (CNPJ 04.368.898/0001-06) |
| Consumidor | ON PETRO DISTRIBUIDORA DE COMBUSTIVEIS LTDA |
| Subgrupo | A4 |
| Modalidade | **Tarifa Horária Verde** |
| Competência / fatura | 04/2023 (leituras 28/02/2023 a 31/03/2023) |
| Data de emissão | 13/04/2023 |
| Total da fatura | **R$ 9.854,93** |

## 2. Grandezas faturadas (conta)

| Produto | Faturado | Tarifa (com tributos) | Total |
|---|---:|---:|---:|
| ENERGIA ELETRICA TE PONTA | 55 kWh | 0,499818 | 27,49 |
| ENERGIA ELETRICA USD PONTA | 55 kWh | 1,323455 | 72,79 |
| ENERGIA ELETRICA TE F PONTA | 9.094 kWh | 0,318435 | 2.895,85 |
| ENERGIA ELETRICA USD F PONTA | 9.094 kWh | 0,142793 | 1.298,56 |
| ENERGIA REAT EXCED TE F PONTA | 9 kWh | 0,333333 | 3,00 |
| DEMANDA USD | 150,65 kW | 22,645868 | 3.411,60 |
| DEMANDA USD ISENTA ICMS | 109,35 kW | 18,570005 | 2.030,63 |
| CONT ILUMIN PUBLICA MUNICIPIO | — | — | 115,01 |
| **TOTAL** | | | **9.854,93** |

- Demanda contratada: **260 kW** (medida 150,65 kW; faturada = contratada).
- Demanda total faturada = 150,65 + 109,35 = **260 kW** (split tributável × isento de ICMS).
- Bandeira tarifária: **Verde** (01/03–31/03/2023) → adicional 0.
- Tributos informados na conta: ICMS 18%, PIS 0,95%, COFINS 4,38%
  (PIS R$ 79,35 + COFINS R$ 365,83 = R$ 445,18; ICMS R$ 1.387,67 — incluídos).

## 3. Tarifas líquidas (nosso banco × conta)

A conta mostra nas "Informações Suplementares" as tarifas **líquidas**:

| Componente | Banco (`Tarifa de Aplicação`) | Conta |
|---|---:|---:|
| TE Ponta | 388,08 R$/MWh | 0,388080 R$/kWh ✓ |
| TE Fora ponta | 247,20 R$/MWh | 0,247200 R$/kWh ✓ |
| TUSD Ponta | 1.027,46 R$/MWh | 1,027460 R$/kWh ✓ |
| TUSD Fora ponta | 110,85 R$/MWh | 0,110850 R$/kWh ✓ |
| TUSD Demanda (única) | 17,58 R$/kW | 17,580000 R$/kW ✓ |

**Vigência no banco:** 2022-06-24 a 2023-06-23 (REH correspondente).

## 4. Fórmula de tributos validada

A conta da Copel engrossa as tarifas líquidas pelo fator:

```
fator = 1 / ((1 − PIS − COFINS) × (1 − ICMS))
      = 1 / ((1 − 0,0095 − 0,0438) × (1 − 0,18))
      = 1,28817
```

Conferência: 0,388080 × 1,28817 ≈ 0,499818 ✓ — **a conta usa a forma
"por fora" (multiplicativa)**, que no nosso sistema é `tipo_icms="fora"`.
A forma aditiva (`1/(1−PIS−COFINS−ICMS)` = 1,3043) NÃO reproduz a conta.

> Registro: a conta real **valida a escolha do `tipo_icms="fora"`** para
> reproduzir faturas Copel. A fonte oficial MME/ANEEL usa a aditiva; manter
> as duas fórmulas com seletor (decisão já implementada).

## 5. Comparação de resultados

Simulação nossa: Copel-DIS, A4, Verde, `data_referencia=2023-03-15`,
consumo P=55 / FP=9.094 kWh, demanda medida única=150,65 kW, contratada
única=260 kW, `outros_rs=115,01`, tributos por fora (pis=0,0095,
cofins=0,0438, icms=0,18).

| Item | Conta real | Simulação | Diferença |
|---|---:|---:|---:|
| TE Ponta | 27,49 | 27,50 | +0,01 |
| TUSD Ponta | 72,79 | 72,79 | 0,00 |
| TE Fora Ponta | 2.895,85 | 2.895,86 | +0,01 |
| TUSD Fora Ponta | 1.298,56 | 1.298,57 | +0,01 |
| Demanda (260 kW) | 5.442,23 | 5.887,98 | **+445,75** |
| Reativo excedente | 3,00 | 0,00 | **−3,00** |
| Iluminação pública | 115,01 | 115,01 | 0,00 |
| **TOTAL** | **9.854,93** | **10.297,70** | **+442,77** |

Diferença total explicada: +445,75 (isenção de ICMS na demanda, não modelada)
− 3,00 (reativo excedente, não modelado) = **+442,75** ✓ (arredondamentos
de centavo na conta explicam os R$ 0,02 restantes).

## 6. O que foi validado ✅

1. Tarifas líquidas do banco batem 1:1 com a conta.
2. Fórmula de tributos "por fora" reproduz as tarifas finais da conta.
3. Demanda faturável = máx(medida, contratada): 260 kW faturado. ✓
4. Bandeira Verde 03/2023 → 0. ✓
5. Horo-sazonal não se aplica (2023 = posto simples Ponta/Fora ponta). ✓

## 7. Gaps identificados (novos itens de backlog)

1. **Isenção de ICMS na demanda** (impacto: R$ 445,75 nesta conta).
   - A Copel divide a demanda em: `DEMANDA USD` (com ICMS) e
     `DEMANDA USD ISENTA ICMS` (só PIS/COFINS).
   - Nosso motor aplica um único fator de tributos em toda a demanda.
   - Necessário: suporte a **parcela isenta de ICMS** (quantidade isenta ×
     tarifa grossed só com PIS/COFINS).

2. **Reativo excedente faturado diretamente** (impacto: R$ 3,00).
   - A conta traz `ENERGIA REAT EXCED TE F PONTA: 9 kWh × 0,333333`.
   - Nosso motor calcula reativo via fator de potência < 0,92 com proxy,
     e não aceita a quantidade de reativo excedente já faturada.

3. **Cosmético:** nossa linha sai como `TUSD DEMANDA PONTA`; a conta usa
   `DEMANDA USD` (demanda única da Verde).

## 8. Como reproduzir

```bash
# Consultar as tarifas líquidas usadas
.venv\Scripts\python.exe scripts\consultar_banco.py ^
  --distribuidora "COPEL-DIS" --subgrupo A4 --modalidade Verde ^
  --data 2023-03-15
```

Endpoint: `POST /api/calculo/fatura` com body:

```json
{
  "distribuidora": "COPEL-DIS",
  "subgrupo": "A4",
  "classe": "Não se aplica",
  "detalhe": "Não se aplica",
  "data_referencia": "2023-03-15",
  "consumo_ponta_kwh": 55,
  "consumo_fora_ponta_kwh": 9094,
  "demanda_medida_unica_kw": 150.65,
  "demanda_contratada_unica_kw": 260,
  "percentual_mes_anterior": 0,
  "outros_rs": 115.01
}
```

Query: `modalidade=Verde&aplicar_tributos=true&pis=0.0095&cofins=0.0438&icms=0.18&tipo_icms=fora`

## 9. Critérios de aceite futuros (quando os gaps forem fechados)

- Com isenção de ICMS modelada: demanda deve totalizar **5.442,23**.
- Com reativo excedente faturado: adicionar linha de **3,00**.
- TOTAL da simulação deve fechar em **9.854,93** (± R$ 0,03 de
  arredondamento de centavos da Copel).
