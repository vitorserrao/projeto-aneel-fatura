# Fórmulas e procedimentos de cálculo

> Fonte: `Base de Dados e Análise das Tarifas das Distribuidoras de Energia Elétrica.pdf` (Guia Básico ANEEL).
> Classificação: *Regra explícita* / *Interpretação* / *Não determinado*.

## 1. Fórmulas explicitamente apresentadas no documento

### 1.1 Variação percentual temporal *(pág. 15)*
```
((tarifa_atual − tarifa_anterior) / tarifa_anterior) × 100%
```
*(Regra explícita — pág. 15)* — útil para comparar distribuidoras com níveis tarifários diferentes.

### 1.2 Variação absoluta *(pág. 15)*
```
tarifa_atual − tarifa_anterior
```
*(Regra explícita — pág. 15)*

### 1.3 Coeficiente de variação (CV) *(pág. 15)*
```
desvio padrão / média
```
*(Regra explícita — pág. 15)* — indica volatilidade relativa.

### 1.4 Índices relativos entre distribuidoras *(pág. 15)*
```
tarifa da distribuidora / tarifa média do grupo
```
*(Regra explícita — pág. 15)*

## 2. Procedimento de comparação tarifária *(pág. 15–16)*
Métodos recomendados no documento:
1. **Estatísticas descritivas**: média, mediana, mínimo, máximo, desvio padrão/variância.
2. **Análise de variação temporal**: variação absoluta e percentual; tendência; sazonalidade.
3. **Comparação entre distribuidoras**: boxplot, linhas simultâneas, índices relativos.
4. **Métricas avançadas (opcionais)**: CV; diferença ponta × fora de ponta; correlação temporal entre distribuidoras. *(Regra explícita — pág. 15–16)*

## 3. Análise de tendência *(pág. 17–18)*
Procedimento metodológico em 5 passos:
1. Observação visual (padrão geral, picos/vales, sazonalidade).
2. Suavização da série (média móvel de N períodos; suavização exponencial; filtro de Savitzky-Golay).
3. Modelagem por regressão (reta por mínimos quadrados; inclinação = tendência: subida/queda/estável; aplicável a toda série ou segmentos mensal/trimestral/anual).
4. Decomposição de séries (tendência + sazonalidade + ruído; ex.: STL — Seasonal-Trend decomposition using Loess).
5. Identificação de mudanças de tendência (derivadas discretas; cruzamento de médias móveis de períodos diferentes). *(Regra explícita — pág. 17–18)*

## 4. Cálculo da fatura (energia elétrica) *(pág. 17)*
- "A fatura de energia elétrica é composta pela **soma das tarifas aplicáveis a cada componente de demanda e consumo**." *(Regra explícita — pág. 17)*
- É necessário analisar **cada uma das 14 componentes individualmente** (Azul 5 + Verde 5 + Convencional 3 + Geração 1). *(Regra explícita — pág. 16–17)*

## 5. Lacunas explícitas (não determinadas pelo documento)
- **Fórmula de faturamento de demanda** (contratada vs medida, fator de carga, reativos) — não apresentada. *(Não determinado)*
- **EPI / ACR × ACL** — não mencionado neste documento. *(Não determinado)*
- **Tributos** (PIS/COFINS, ICMS, CIP) incidem na fatura, mas o documento apenas informa que a base é **líquida (sem tributos)**; não fornece fórmula de aplicação dos tributos. *(Regra explícita a ausência — pág. 8)*
- **Bandeiras tarifárias** — não mencionadas. *(Não determinado)*
