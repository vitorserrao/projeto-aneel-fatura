# Premissas e questões a validar

> **Regra:** nunca inventar regras tarifárias, valores, fórmulas ou critérios
> regulatórios. Quando uma regra da ANEEL não estiver claramente definida nos
> dados/documentos fornecidos, registrar a dúvida aqui como premissa/questão a
> validar — **não assumir uma solução.**

## Pendências abertas (NENHUMA implementada ainda)

Nenhuma premissa formal foi fechada nesta etapa. As questões abaixo precisam ser
resolvidas com base em dados/documentos antes de qualquer implementação.

### P1 — Tratamento TE/TUSD
- Qual a regra exata de "tratamento/estruturação" dos componentes TE e TUSD
  (componentização, reajuste, tributação)? A ser definida a partir do dataset e
  documentos.

### P2 — EPI simplificado
- Quais componentes entram no cálculo (só TUSD? TE? energia?) e qual a fórmula
  fechada? A "simplificação" precisa de equação explícita.

### P3 — Demanda tarifável
- Regra de faturamento de demanda por modalidade (única vs ponta/fora de ponta).

### P4 — Cobertura de modalidades e classes
- Quais subgrupos, modalidades (azul, verde, branca, convencional) e classes o
  motor cobre no MVP? Em que condições a "convencional" é aplicável?

### P5 — Dataset ANEEL
- Versão(ões) do dataset "Tarifas de Aplicação" suportadas e estrutura oficial
  (varia entre anos). Confirmar campos e mapeamento de valores.

### P6 — Vigência e precedência
- Regra de tratamento de resoluções sobrepostas, reajustes retroativos e
  precedência temporal no motor.

### P7 — Precisão e arredondamento
- Regra de precisão monetária e arredondamento a adotar para garantir
  comparabilidade com a ferramenta Excel.

## Premissas técnicas (estruturais, não tarifárias)

- Python 3.14+ como ambiente base.
- O `core/` é determinístico e independente de infraestrutura.
- A comparação com o Excel (`Recriar Faturas.xlsm`) é um experimento de
  validação, não uma dependência do sistema.

## Premissas adotadas no Sprint 1 (não regulatórias, reversíveis)

> São decisões de **estrutura do código**, não regras regulatórias da ANEEL.
> Todas podem ser revisadas quando as pendências P1–P7 forem validadas.

### A1 — Aplicação linear das parcelas
O motor calcula cada parcela como `custo = quantidade × valor unitário`, com a
quantidade derivada da `grandeza` (ENERGIA/DEMANDA) e do `posto` (PONTA/FORA
PONTA). `MWh` usa fator 0,001 sobre kWh. **Isto não captura** nenhuma regra de
componentização, tributos ou bandeiras — que permanecem pendentes (P1/P3).

### A2 — Vocabulário normalizado do contrato
O core usa identificadores fixos: postos `PONTA`/`FORA PONTA`, grandezas
`ENERGIA`/`DEMANDA`, componentes `TE`/`TUSD`, unidades `R$/MWh`, `R$/kWh`,
`R$/kW`. O mapeamento dos códigos oficiais do dataset para esses valores é
responsabilidade da ingestão (Sprint 2; pendência P5).

### A3 — Vigência aberta
`inicio_vigencia=None` significa "sem limite inferior" e `fim_vigencia=None`
significa "sem limite superior". Intervalos são inclusivos.

### A4 — Sem arredondamento no core
O core devolve ponto flutuante determinístico sem política de arredondamento.
A política monetária para comparabilidade com o Excel é P7 (pendente) e será
aplicada nas bordas (Sprint 3) ou adicionada quando validada.

### A5 — Precedência recusada em vez de assumida
Quando mais de uma tarifa atende aos critérios, o core lança
`AmbiguidadeTarifaria` em vez de escolher por suposição. A regra de
precedência real é P6 (pendente).

## O que o Sprint 1 NÃO implementa (permanece pendente)

- Fórmula do EPI (P2) — `core/epi.py` falha explicitamente.
- Regra de elegibilidade de modalidades (P4).
- Tratamento/estruturação de TE e TUSD (P1).
- Regra de faturamento de demanda (P3).
- Mapeamento do dataset real (P5).
- Precedência entre resoluções sobrepostas (P6).
- Arredondamento monetário (P7).
