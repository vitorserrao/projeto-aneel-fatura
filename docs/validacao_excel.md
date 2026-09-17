# Validação com a ferramenta Excel

## Referência

A ferramenta Excel **`Recriar Faturas.xlsm`** do projeto anterior é a referência
de validação. O sistema Python **NÃO depende** do Excel para funcionar; a
comparação é um experimento de validação/validação de referência.

## Objetivo

Comparar os resultados gerados pelo sistema Python com os do Excel, para um
conjunto selecionado de **5 a 10 casos reais**, registrando as diferenças.

## Estrutura da comparação (`scripts/validar_excel.py`)

Para cada caso, comparar:

- entradas;
- TE;
- TUSD;
- demanda;
- energia;
- total;
- diferença absoluta;
- diferença percentual.

## Critérios de aceite (a definir)

- Tolerância de diferença entre sistemas a ser definida (ex.: limites de
  diferença absoluta e percentual por componente).
- Casos serão escolhidos posteriormente junto ao projeto anterior.

## Rastreabilidade

Cada resultado de validação deve ser registrado (entradas, tarifas, saídas,
diferenças) para sustentar a análise acadêmica e científica.
