# Projeto anterior — Fórmulas de cálculo (extraídas das planilhas Excel)

> Rastreabilidade: **Arquivo → Aba → Célula**.
> Fonte base: `Simulador de Fatura/Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm`.

## 1. Tributos "por dentro" (fórmula central)

**Nome:** Tarifa com imposto
- Arquivo: `Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm`
- Aba: `Fatura de Energia - 1`
- Célula: `K20`
- Entradas: `G20` (tarifa sem imposto), `H20` (PIS/PASEP), `I20` (COFINS), `J20` (ICMS)
- **Fórmula original:** `=G20/((1-H20-I20)*(1-J20))`
- Significado: `tarifa_com_imposto = tarifa_sem_imposto / ((1 − PIS − COFINS) × (1 − ICMS))` — impostos "por dentro" (embutidos na base).
- Observação: PIS e COFINS são somados como taxa (não-cumulativo simplificado); ICMS entra multiplicativo.

## 2. Valor da linha de cobrança

**Nome:** Valor (R$)
- Célula: `L20`
- **Fórmula original:** `=F20*K20`
- Significado: `valor = quantidade_faturada × tarifa_com_imposto`.
- Quantidade em `F` (ex.: `F20 = I6*I13` — consumo ponta × %mês); tarifa em `K`.

## 3. Parcelas de quantidade por posto (exemplos)

| Cálculo | Célula (F) | Fórmula | Significado |
|---|---|---|---|
| Demanda faturada ponta | F20 | `=I6*I13` | demanda ponta × proporção do mês |
| Demanda fora ponta | F21 | `=I6*(1-I13)` | demanda × (1 − proporção) |
| Consumo ponta mês anterior | — | `=I6*(1-I13)` | divisão seca/úmida por leitura anterior/atual |

(Os nomes `I6`, `I13`, `M5`, `M6` referem-se ao Painel Inicial: consumo/demanda e percentual de mês.)

## 4. Parâmetros padrão encontrados (Painel Inicial / Fatura)

| Parâmetro | Valor no exemplo | Unidade | Observação |
|---|---|---|---|
| PIS/PASEP | 0,0025 (0,25%) | % | tributação simplificada |
| COFINS | 0,0115 (1,15%) | % | |
| ICMS | 0,25 (25%) | % | alíquota variável por estado |
| CIP/COSIP | 133,20 | R$ | tributação municipal (fixo no exemplo) |
| Limite potência aparente (Grupo B) | 112,5 | kVA | enquadramento |
| Limite potência ativa (Convencional Binômia) | 300 | kW | enquadramento |
| % Consumo Intermediário no FP | 0,10 | fração | |
| Tipo faturamento ICMS | 1 (por fora) / 2 (por dentro) | — | seletor |

## 5. Linhas de cobrança (componentes) por modalidade (aba Fatura - 1)
- TUSD demanda (R$/kW)
- TUSD energia (R$/MWh)
- TE (R$/MWh)
- Adicional Bandeira Tarifária (R$/kWh)
- Ultrapassagem de Demanda
- Consumo Excessivo de Energia Reativa (R$/kVArh)
- Demanda Excessiva de Energia Reativa (R$/kVAr)
- Imposto Municipal — CIP/COSIP
- Outros valores

## 6. SCEE — percentual de desconto (calculador)

**Nome:** %TUSD (GDII)
- Arquivo: `Calculador de Porcentagens - SCEE - Macro Habilitada.xlsm`
- Aba: `Porcentagens SCEE`
- Célula: coluna `TUSD (NA) - total` e coluna final `%TUSD` (ex.: `0.817753...` para A3a Verde P)
- **Lógica:** relação entre a **TUSD sem os componentes do Fio A** e a **TUSD total**, por subgrupo/modalidade/posto. Representa o percentual da TUSD que permanece na energia compensada (SCEE).
- Exemplos reais (referência): A3a Verde P → 0,8178; A2 Azul → 1,0000; B1 Convencional → 0,8823.

## 7. Discretização (referência metodológica)
- Arquivo: `Discretização tarifas - eixo vertical.xlsx`
- Confirma a discretização por componente (TUSD demanda/energia, TE) × posto (ponta/intermediária/fora ponta/seca/úmida/sem posto) × modalidade (Azul/Verde/Convencional/Monômia/Branca/Geração).
