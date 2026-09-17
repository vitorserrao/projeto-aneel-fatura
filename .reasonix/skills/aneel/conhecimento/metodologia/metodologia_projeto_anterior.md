# Projeto anterior — Metodologia

> Fonte: arquivos do projeto Kevin Wu; reconstrução **somente a partir do que existe**.

## 1. Metodologia geral
1. **Banco de dados**: utilizar a base de tarifas da ANEEL (2010–2025), já filtrada por distribuidora/REH/vigência/subgrupo/modalidade/componente.
2. **Discretização**: separar os valores por componente tarifário (TUSD demanda R$/kW, TUSD energia R$/MWh, TE R$/MWh) × posto (P/INT/FP, seca/úmida quando < 2014).
3. **Perfil do consumidor**: coletar demanda (faturada/contratada, por posto), consumo (por posto), reativos, datas de leitura anterior/atual, distribuidora, subgrupo, modalidade, REH, tributos.
4. **Montar linhas de cobrança** por modalidade (Azul/Verde/Convencional/Monômia/Branca): demanda, consumo, TE, bandeira, ultrapassagem, reativos, CIP, outros.
5. **Tributação**: aplicar PIS/COFINS/ICMS "por dentro" sobre cada tarifa antes de multiplicar pela quantidade.
6. **Comparar** o total de cada modalidade e identificar indisponíveis.

## 2. Fluxo de cálculo (ENTRADAS → PARÂMETROS → CÁLCULOS → RESULTADOS)

```
ENTRADAS (Painel Inicial):
  - distribuidora, subgrupo, modalidade, REH, datas leitura
  - demanda faturada/contratada (P/FP), consumo (P/FP), reativos
  - tributos (PIS, COFINS, ICMS, CIP)
  - tipo ICMS (fora/dentro), % mês, % int/FP, bandeira
        ↓
PARÂMETROS (constantes):
  - limites (112,5 kVA B; 300 kW Conv.Binômia)
  - tarifas do banco (por vigência)
        ↓
CÁLCULOS (Fatura - 1/2):
  - quantidade × tarifa_com_imposto para cada linha
  - tarifa_com_imposto = tarifa / ((1−PIS−COFINS)×(1−ICMS))
        ↓
RESULTADOS:
  - total R$ por modalidade
  - comparação Azul/Verde/Convencional/Monômia/Branca
```

## 3. Premissas e simplificações
- PIS/COFINS aplicados como **taxa somada** (não-cumulativo simplificado).
- CIP/COSIP tratado como **valor fixo mensal** no exemplo.
- **Bandeiras tarifárias** com adicional por kWh (0 no exemplo de 2010).
- Período **anterior a 2014** exige distinção seca/úmida (proporção entre meses de leitura).
- Não há Python; tudo é fórmula Excel + macros VBA.

## 4. Limitações explícitas da ferramenta anterior
- A aba "Fatura" usa **nomes definidos** alimentados por macro; o openpyxl resolve como `#NAME?`, exigindo interpretação manual — as fórmulas registradas preservam a lógica mesmo sem a macro.
- O cálculo de bandeiras/reativos/ultrapassagem depende de valores que no exemplo padrão são zero.
