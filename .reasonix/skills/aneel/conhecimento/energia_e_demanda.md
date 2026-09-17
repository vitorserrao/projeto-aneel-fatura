# Energia e demanda

> Fonte: `Base de Dados e Análise das Tarifas das Distribuidoras de Energia Elétrica.pdf` (Guia Básico ANEEL).
> Classificação: *Regra explícita* / *Interpretação* / *Não determinado*.

## 1. Unidades de medida *(pág. 2, 12, 14)*
- **Demanda** é expressa em **R$/kW**. *(Regra explícita)*
- **Energia (consumo/TE)** é expressa em **R$/MWh**. *(Regra explícita)*
- Filtro "Unidade" da ferramenta:
  - `R$/kW` → TUSD Demanda.
  - `R$/MWh` → TUSD Consumo e TE. *(Regra explícita — pág. 2)*

## 2. Discretização dos valores (eixo vertical) *(pág. 8)*
Formas consideradas no documento para o Grupo A (excluindo acessantes especiais):
- **I — Conjunta**: demanda (TUSDdemanda) + energia (TUSDenergia + TE).
- **II — Discretizada por postos**: cada componente de demanda e energia individualmente (17 combinações listadas + 1 de geração).
- **III — Discretizada por subgrupo × modalidade × posto**: 64 possibilidades (tarifação antiga + atual + inalterada). *(Regra explícita — pág. 8–13)*

## 3. Médias de valor apresentadas *(pág. 7, 14)*
- TUSD Demanda (R$/kW): **27,96717142**
- TUSD Energia (R$/MWh): **353,5591671**
- TE (R$/MWh): **134,3132201** *(Regra explícita — pág. 7 e 14)*

## 4. Escala/conversão dos valores
- O documento alerta que demanda (R$/kW) e energia (R$/MWh) estão em **escalas diferentes** e que é necessário **pelo menos uma discretização por componente tarifário** para comparação adequada. *(Regra explícita — pág. 14)*
- Implicação de cálculo: não somar R$/kW com R$/MWh sem conversão/fator (consumo/demanda a definir pelo perfil). *(Interpretação)*

## 5. Tarifas extremas (valores de referência) *(pág. 6–7)*
- Maior **TUSD Demanda**: 193.498,5 R$/kW (RGE anterior, REH 1.153/2011, A1 Azul APE Fora ponta).
- Maior **TUSD Energia**: 5.121,38 R$/MWh (Ceral Araruama, REH 3.446/2025, A4 Verde SCEE Ponta).
- Maior **TE**: 794,54 R$/MWh (CPFL Santa Cruz anterior, REH 1.858/2015, A4 Verde Ponta). *(Regra explícita — pág. 5–6)*
- Menor **TUSD Demanda**: -0,53 R$/kW (Energisa MS, REH 0.958/2010).
- Menor **TUSD Energia**: -122,63 R$/MWh (Equatorial CEA, A3a Azul).
- Menor **TE**: -289,92 R$/MWh (DMED, A4 Convencional SCEE). *(Regra explícita — pág. 6–7)*

## 6. A fatura é a soma das tarifas aplicáveis *(pág. 17)*
- "A fatura de energia elétrica é composta pela **soma das tarifas aplicáveis a cada componente de demanda e consumo**." *(Regra explícita — pág. 17)*
- Para a melhor adequação tarifária, analisar **cada uma das 14 componentes individualmente**, dependendo do perfil de demanda e consumo. *(Regra explícita — pág. 17)*

## 7. Cálculo de demanda — observação de lacuna
- O documento identifica **quais** componentes de demanda existem e que a fatura é soma, mas **não detalha** a regra de faturamento de demanda (demanda contratada vs medida, fator de carga, reativos, multa por ultrapassagem). *(Não determinado — não completar)*
