# Dataset ANEEL — Tarifas de Aplicação

> **Estado atual:** o dataset real ainda **não foi carregado** nesta etapa.
> Nenhum dado fictício deve ser criado para aparentar que ele foi importado.

## Fonte

Fonte primária: dataset **Tarifas de Aplicação** da ANEEL.

A ingestão será feita por `infra/ingestion/` e orquestrada por
`scripts/ingest_aneel.py`.

## Campos a preservar

A ingestão deve **preservar** os campos disponíveis do dataset, sem eliminar
informações silenciosamente:

- distribuidora;
- resolução;
- início da vigência;
- fim da vigência;
- base tarifária;
- subgrupo;
- modalidade;
- classe;
- subclasse;
- detalhe;
- acessante / tipo de acesso;
- posto;
- unidade;
- TUSD;
- TE.

Toda transformação de dados deve ser documentada.

## Estrutura do diretório de dados

- `data/raw/` — arquivos brutos como obtidos da ANEEL.
- `data/processed/` — dados limpos/estruturados após ingestão.
- `data/samples/` — amostras pequenas usadas em testes/fixtures (dados reais,
  não inventados).

## Pendências

- Confirmar a versão/estrutura oficial do dataset a ser utilizada (varia entre
  anos: ex. nomenclatura de "posto"/"período", "detalhe").
- Definir mapeamento de colunas e normalização em `docs/premissas.md` (P5).

## Proveniência

- Registrar a origem exata de cada arquivo (URL de download, data de obtenção,
  versão) para fins acadêmicos.
- Nunca inventar valores tarifários.
