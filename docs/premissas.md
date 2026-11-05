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

### P2 — EPI simplificado ✅ resolvido (ver docs/epi.md)
- Fórmula fechada implementada em `core.epi.calcular_pi` / `calcular_pi_meses`
  (adaptada de Lemos, 2025): energia TE ponta/fora ponta + bandeira, tributos
  multiplicativos, perdas `k`, OPEX/CAPEX do ACL com horizonte de amortização.

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

### A6 — Reativos excedentes (art. 304) por agregado mensal por posto
Implementação de 17/09/2026. A fórmula oficial exige medições horárias
(`fT` por intervalo `T` de 1 hora e `max_T`), que o perfil atual não possui.
O motor usa **aproximação por agregado mensal**:
- `fp = EA / √(EA² + ER²)` com os totais do ciclo por posto/natureza;
- energia: `EEAM(p) × (0,92/fp − 1) × VRERE` (MWh);
- demanda: `[D_medida × 0,92/fp − DAF] × VRDRE` (kW).
A janela capacitiva (0h–6h) é alocada proporcionalmente às horas do fora
ponta (6h/21h) e é sempre fora ponta. Os campos `reativo_*_ponta/fora_ponta`
representam a parcela **indutiva**; `reativo_*_capacitiva_*` a **capacitiva**.
É uma aproximação documentada — não substitui a fórmula horária oficial se
vierem a existir dados de memória de massa.

**Modo `reativos_direto` (faturas antigas, 18/09/2026):** para replicar o
Simulador/XLSM e o artigo XX ERIAC 2025, os mesmos campos podem ser tratados
como **excedente pronto** (kVArh/kVAr) e cobrados com tarifas diretas
(R$/kVArh e R$/kVAr) informadas por quem chama — sem passar pelo art. 304.

**Tributação da ultrapassagem (18/09/2026):** validado contra o artigo XX
ERIAC 2025 (CPFL Piratininga A4 2018) — `aplicar_tributos=True` tributa as
linhas TARIFA **e ULTRAPASSAGEM** (as demais linhas permanecem sem tributos).

## Decisões das faturas reais (18/09/2026)

- Referência de validação passa a ser **faturas reais** (não a planilha do
  projeto anterior, que pode conter erros). A planilha/artigo ficam como
  comparação secundária documental.
- `demanda_isenta_icms` e `tributar_reativos` adicionados ao motor e à API,
  conforme evidenciado nas faturas Copel/CEMIG/Equatorial.
- Tolerância de aceite: **≤ R$ 0,05 por linha e ≤ R$ 1,00 no total**.

## Decisões da fase do artigo ERIAC (04/11/2026)

### D1 — Padrão de tributação multiplicativo
`tipo_icms="fora"` (`tarifa / ((1 − PIS − COFINS) × (1 − ICMS))`) passa a ser o
padrão do motor, do `CalculoService` e da API: é a forma que reproduz as faturas
reais da Copel, CEMIG e Equatorial. A forma aditiva (`"dentro"`) continua
disponível por parâmetro.

### D2 — Entradas são as grandezas FATURADAS (perdas de transformação)
Quando a medição fica no secundário do transformador do consumidor, a
distribuidora acrescenta um percentual de perdas às grandezas medidas
(REN 1.000/2021, art. 305; 2,5% nas faturas Copel 04/2023 e Equatorial
Tucuruí Núcleo 12/2024 — ex.: 2.600 kWh medidos × 1,025 = 2.665 kWh faturados).
O acréscimo não aparece como linha da fatura: já vem embutido na coluna
"Faturado" e no "Histórico de Consumo". **Premissa:** o sistema recebe as
grandezas faturadas (energia, demanda e reativo), que já incluem as perdas.
Um campo "medição no secundário (+%)" só será necessário se o sistema passar a
ler dados direto do medidor (trabalho futuro).

### D3 — Reativo excedente no Optante B (divergência em aberto)
O art. 302 fixa o fator de potência de referência (0,92) para o Grupo A e o
art. 303 diz que o Grupo B não paga reativo excedente. O Optante B (art. 292)
continua sendo unidade do Grupo A atendida em média tensão, apenas **faturada**
com tarifa do Grupo B. A fatura real da Equatorial (Tucuruí Núcleo, 12/2024,
classificação "B-Optante") cobra reativo excedente (164 kvarh × 0,290980 R$/kvarh).
Não foi encontrada regra explícita para o caso.

```
Fatura real (Equatorial): cobra reativo excedente do B-Optante
Fonte oficial (arts. 302–303): FP de referência para o Grupo A; Grupo B isento
Diferença: enquadramento técnico (A) × faturamento (B)
Impacto: R$ 62,43 na fatura de 12/2024
```

**Decisão provisória:** o motor cobra o reativo do Optante B **somente quando o
usuário informa** o excedente (comportamento atual, sem regra automática).
Pergunta registrada para o orientador.

## O que o Sprint 1 NÃO implementa (permanece pendente)

- ~~Fórmula do EPI (P2)~~ — ✅ implementada em `core/epi.py` (ver docs/epi.md).
- Regra de elegibilidade de modalidades (P4).
- Tratamento/estruturação de TE e TUSD (P1).
- Regra de faturamento de demanda (P3).
- Mapeamento do dataset real (P5).
- Precedência entre resoluções sobrepostas (P6).
- Arredondamento monetário (P7).
