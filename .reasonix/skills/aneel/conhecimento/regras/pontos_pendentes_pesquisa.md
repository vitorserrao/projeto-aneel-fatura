# Pontos pendentes de pesquisa / definição

> Lista viva das lacunas que **ainda não têm fonte oficial fechada** ou que
> dependem de **decisão do projeto**. Atualizada após a pesquisa em fontes
> oficiais (ANEEL/Governo) registrada em
> [`ren1000_2021_faturamento.md`](../regras/ren1000_2021_faturamento.md).

## ✅ Resolvidos por fonte oficial (não pendentes mais)

| Tema | Regra oficial encontrada |
|---|---|
| Demanda faturável | Maior entre contratada e medida (REN 1.000/2021) |
| Ultrapassagem | Tolerância 5% (geral); fórmula `[PAM−PAC] × 2 × VD_ult` |
| Reativos | Fator de potência limite 0,92; excedente cobrado |
| Elegibilidade | Azul = todos A (obrig. A1-A3); Verde = A3a/A4/AS; Branca = B (vedada baixa renda/IP/pré-pagamento) |
| Demanda da Verde | Demanda **única** (sem posto) |
| Posto Intermediário | Exclusivo da Branca (Grupo B) — **fora do Grupo A** |
| Tributos | Fórmula oficial `Tarifa / (1 − PIS − COFINS − ICMS) + CIP` |

## 🔴 Ainda pendentes (sem fonte oficial encontrada)

### P6 — Precedência entre vigências sobrepostas
- **Pergunta:** quando há dois registros na mesma data/subgrupo/modalidade
  (ex.: `detalhe` = "APE" vs "Não se aplica"), qual prevalece?
- **O que pesquisar:** regras de vigência/publicação das REH; texto integral da
  REN 1.000/2021; comportamento da base ANEEL.
- **Impacto:** hoje o motor **soma** as linhas sobrepostas e apenas sinaliza
  (`duplicidade_vigencia`) — pode dobrar o custo.

### P7 — Arredondamento monetário
- **Pergunta:** quantas casas decimais e qual critério (bancário/truncamento)?
- **O que pesquisar:** REN 1.000/2021 (texto integral) e formato das células do
  Excel de referência do projeto anterior.
- **Impacto:** comparabilidade com a validação.

### P2 — EPI / ACR × ACL
- **Pergunta:** fórmula fechada do Preço de Indiferença e critério de comparação
  com o preço do ACL.
- **Situação:** **nenhuma fórmula oficial** (ANEEL/Governo) encontrada.
- **Pista nova (aula IFSC / RTE):** o material da disciplina aponta para o GESE —
  *"Preço de indiferença, ferramenta para análise"* em
  https://gese.florianopolis.ifsc.edu.br/produções/ — como **referência metodológica**.
  Também remete às fórmulas de viabilidade de migração ACR → ACL (custos/economias).
- **Alternativas (não oficiais):** artigo XXERIAC 2025 (próprio projeto); dissertações do
  GESE; material da aula RTE (ver `ambientes_comercializacao_e_tarifas_aula.md`, item 18).
- **Impacto:** bloqueia o módulo EPI.

### Conflito adicional — fórmula de tributos (3 fontes)
- **Projeto anterior (Kevin Wu):** `tarifa / ((1 − PIS − COFINS) × (1 − ICMS))` (multiplicativa).
- **Aula IFSC / RTE (pág. 52):** mesma forma **multiplicativa** (com exemplo numérico).
- **MME/ANEEL:** `tarifa / (1 − PIS − COFINS − ICMS)` (aditiva).
- **Ação:** prevalece a fonte oficial; registrar que o material didático usa a forma
  multiplicativa.

## 🟡 Decisões do projeto (não são "pesquisa", são escolha)

1. **Tributos na fatura do MVP:** incluir (fórmula oficial) ou usar base
   **líquida** (como a base ANEEL)? *Recomendação: base líquida no MVP; tributos
   como camada futura — registrar o conflito com o projeto anterior.*
2. **Perfil persistido?** Decidido: **motor stateless** (sem novas tabelas).
3. **Escopo de validação:** quais casos do projeto anterior usar como referência
   (ver [`casos_de_teste.md`](../validacao/casos_de_teste.md)).

## Registro de conflitos entre fontes

```text
Tema: tributos na conta
Projeto anterior: tarifa / ((1 − PIS − COFINS) × (1 − ICMS))
Fonte oficial:    tarifa / (1 − PIS − COFINS − ICMS)
Diferença:        forma de composição do ICMS (multiplicativo vs aditivo)
Impacto:          valores de conta divergem; prevalece a fonte oficial
```
