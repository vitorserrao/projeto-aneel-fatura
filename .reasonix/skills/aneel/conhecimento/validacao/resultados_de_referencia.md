# Projeto anterior — Resultados de referência (ground truth)

> Resultados numéricos extraídos das planilhas; **referência de validação**, não verdade automática.

## 1. Percentuais SCEE GDII (mais confiáveis — colunas numéricas estáveis)

| Subgrupo | Modalidade | Classe/Subclasse | Posto | %TUSD (GDII) |
|---|---|---|---|---|
| A2 | Azul | NA/NA | P, FP | 1,000000 |
| A3 | Azul | NA/NA | P, FP | 1,000000 |
| A3a | Azul | NA/NA | P, FP | 1,000000 |
| A3a | Verde | NA/NA | P | 0,8177540 |
| A4 | Verde | NA/NA | P | 0,8177540 |
| B1 | Branca | Residencial/Residencial | P | 0,8360673 |
| B1 | Branca | Residencial/Residencial | INT | 0,8579386 |
| B1 | Branca | Residencial/Residencial | FP | 0,9147882 |
| B1 | Convencional | Residencial | NA | 0,8822862 |
| B1 | Convencional | Baixa Renda | NA | 0,8261256 |
| B2 | Branca | Rural | P | 0,8327947 |
| B3 | Branca | NA | P | 0,8278823 |
| B4 | Convencional | IP B4a | NA | 0,8822873 |
| B4 | Convencional | IP B4b | NA | 0,8822850 |

**Fonte:** `Calculador de Porcentagens SCEE/...xlsm` → aba `Porcentagens SCEE` (coluna final).

## 2. Tarifas de referência (exemplo Amazonas Energia, REH 1.077)
Valores observados na aba `Processamento de Dados` (base reduzida):
- A3 Azul Fora ponta R$/kW: Base Econômica 4,84 / Tarifa de Aplicação 5,01.
- A3 Azul Fora ponta R$/MWh: BE 15,66 / TA 16,67.
- A4 Azul Fora ponta R$/kW: BE 10,60 / TA 10,98.
- TE Fora ponta seca (A3 Azul): BE 140,05 / TA 144,52.
- TE Ponta seca (A3 Azul): BE 241,37 / TA 249,08.

**Fonte:** `Ferramenta de Recriar Faturas...xlsm` → aba `Processamento de Dados` (colunas TUSD/TE).

## 3. Comparação com o novo sistema
```
Exemplo de aplicação futura:
Caso X -> Resultado planilha anterior: R$ ?
        -> Resultado novo sistema: R$ ?
        -> Diferença: ...
```
Os números finais de fatura dependem de recalcular no Excel original (macro) e serão preenchidos na etapa de validação.
