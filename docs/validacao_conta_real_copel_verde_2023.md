# Validação contra conta real — Copel A4 Tarifa Verde (03/2023)

> Registro do teste de comparação entre uma **conta real de energia elétrica**
> (DANF3E / NF3E da Copel Distribuição) e o resultado do nosso simulador.
>
> - Arquivo da conta: `clipboard-20260916-114548.262904-000003.pdf` (anexado)
> - Data do teste: 2025-09-16
> - Caso de referência: Copel-DIS, A4, Tarifa Horária Verde, competência 03/2023

---

## 1. Dados da conta real

| Campo | Valor |
|---|---|
| Distribuidora | Copel Distribuição S.A. (CNPJ 04.368.898/0001-06) |
| Consumidor | UC COPEL-1 (comercial, A4 Verde) |
| Subgrupo | A4 |
| Modalidade | **Tarifa Horária Verde** |
| Competência / fatura | 04/2023 (leituras 28/02/2023 a 31/03/2023) |
| Data de emissão | 13/04/2023 |
| Total da fatura | **R$ 9.854,93** |

## 2. Grandezas faturadas (conta real)

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

Observações da conta:

- Demanda contratada: **260 kW** (medida 150,65 kW; faturada = contratada).
- Demanda total faturada = 150,65 + 109,35 = **260 kW** — a Copel divide a
  demanda em parcela **com ICMS** e parcela **isenta de ICMS**.
- Bandeira tarifária: **Verde** (01/03 a 31/03/2023) → adicional 0.
- Tributos informados: ICMS 18%, PIS 0,95%, COFINS 4,38%
  (PIS R$ 79,35 + COFINS R$ 365,83 = R$ 445,18; ICMS R$ 1.387,67 — incluídos
  no total).

## 3. Tarifas líquidas — nosso banco × conta real

A conta mostra nas "Informações Suplementares" as tarifas **líquidas** (sem
tributos). Nosso banco (`tarifa_aplicacao_componente`, base
`Tarifa de Aplicação`, vigência 2022-06-24 a 2023-06-23) contém exatamente os
mesmos valores:

| Componente | Banco | Conta real | Confere? |
|---|---:|---:|---|
| TE Ponta | 388,08 R$/MWh | 0,388080 R$/kWh | ✅ |
| TE Fora ponta | 247,20 R$/MWh | 0,247200 R$/kWh | ✅ |
| TUSD Ponta | 1.027,46 R$/MWh | 1,027460 R$/kWh | ✅ |
| TUSD Fora ponta | 110,85 R$/MWh | 0,110850 R$/kWh | ✅ |
| TUSD Demanda (única) | 17,58 R$/kW | 17,580000 R$/kW | ✅ |

## 4. Fórmula de tributos validada pela conta

A Copel engrossa as tarifas líquidas com o fator **"por fora" (multiplicativo)**:

```
fator = 1 / ((1 − PIS − COFINS) × (1 − ICMS))
      = 1 / ((1 − 0,0095 − 0,0438) × (1 − 0,18))
      = 1,28817
```

Conferência com a conta:

- TE Ponta: 0,388080 × 1,28817 ≈ **0,499818** ✅
- TUSD Ponta: 1,027460 × 1,28817 ≈ **1,323455** ✅
- Demanda: 17,58 × 1,28817 ≈ **22,645868** ✅

> **Conclusão registrada:** a conta real **valida o uso de `tipo_icms="fora"`
> (multiplicativo)** para reproduzir faturas Copel. A forma aditiva
> (`1/(1−PIS−COFINS−ICMS)` = 1,3043) NÃO reproduz esta conta. O projeto mantém
> as duas fórmulas com seletor (`tipo_icms`: `dentro`/`fora`), documentando a
> divergência entre a fonte oficial (aditiva) e a prática observada na fatura.

## 5. Comparação — Conta real × Simulação

Parâmetros da simulação (`POST /api/calculo/fatura`):

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

**Explicação da diferença:**

- `+445,75` → a Copel divide a demanda em parcela com ICMS e parcela
  **isenta de ICMS**; nosso motor aplica o fator cheio nos 260 kW.
- `−3,00` → a conta cobra **reativo excedente faturado** (9 kWh × 0,333333);
  nosso motor não aceita a quantidade de reativo excedente já faturada.
- `+445,75 − 3,00 = +442,75` ✅ (os R$ 0,02 restantes são arredondamento de
  centavos da Copel).

## 6. O que foi validado ✅

1. **Tarifas líquidas**: o banco bate 1:1 com a conta real.
2. **Tributos por fora**: a fórmula multiplicativa reproduz as tarifas finais
   da conta.
3. **Demanda faturável = máx(medida, contratada)**: faturados 260 kW
   (contratada), com medida de 150,65 kW.
4. **Bandeira Verde 03/2023 → 0**: sem adicional nos dois lados.
5. **Horo-sazonal**: não se aplica em 2023 (postos simples Ponta/Fora ponta).
6. **Estrutura da fatura Verde**: TE + TUSD (energia) por posto e demanda
   única estão corretas.

## 7. Gaps identificados (novos itens de backlog)

1. **Isenção de ICMS na demanda** — impacto R$ 445,75 nesta conta.
   - Copel divide a demanda em `DEMANDA USD` (com ICMS) e
     `DEMANDA USD ISENTA ICMS` (apenas PIS/COFINS).
   - Necessário: suporte a **parcela isenta de ICMS** (quantidade isenta ×
     tarifa com fator apenas de PIS/COFINS).

2. **Reativo excedente faturado diretamente** — impacto R$ 3,00.
   - A conta traz `ENERGIA REAT EXCED TE F PONTA: 9 kWh × 0,333333`.
   - Necessário: aceitar **quantidade de reativo excedente já faturada**
     (além do cálculo por fator de potência < 0,92).

3. **Cosmético** — nossa linha sai como `TUSD DEMANDA PONTA`; a conta usa
   `DEMANDA USD` (demanda única da Verde).

## 8. Como reproduzir

```bash
# Consultar as tarifas líquidas usadas no banco
.venv\Scripts\python.exe scripts\consultar_banco.py ^
  --distribuidora "COPEL-DIS" --subgrupo A4 --modalidade Verde ^
  --data 2023-03-15
```

Endpoint: `POST http://127.0.0.1:8000/api/calculo/fatura` com o body da seção 5
e a query indicada.

## 9. Critérios de aceite futuros

Quando os gaps forem fechados, a simulação deve fechar:

- Demanda (com isenção de ICMS): **5.442,23**
- Reativo excedente: **3,00**
- **TOTAL: 9.854,93** (± R$ 0,03 de arredondamento de centavos da Copel)
