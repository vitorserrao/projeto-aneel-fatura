# Cartilha 2013 — Fórmulas (consolidação)

> Fonte: `PorDentrodaContadeLuz_2013.pdf` (ANEEL, 6ª edição, março 2013).
> Índice consolidado das fórmulas/procedimentos apresentados, por página, com classificação.

| # | Fórmula / procedimento | Página | Classificação |
|---|---|---|---|
| F1 | Composição da tarifa = energia gerada + transporte (transmissão+distribuição) + encargos setoriais; sobre ela incidem tributos | 9 | Regra explícita |
| F2 | TFSEE = **0,4%** do benefício econômico anual (antes 0,5%) | 12 | Regra explícita |
| F3 | CFURH = **6,75%** × MWh produzidos × TAR; divisão 45/45/10 | 13 | Regra explícita |
| F4 | PIS **1,65%** + COFINS **7,60%** (não-cumulativo) | 15 | Regra explícita |
| F5 | Alíquota efetiva PIS/COFINS = (débito − crédito) / faturamento bruto | 15 | Regra explícita (exemplo 5,55%) |
| F6 | ICMS "por dentro": impacto > nominal (25% → ~33%; R$100 → R$133) | 16 | Regra explícita |
| F7 | Reajuste anual = **Parcela A (atualizada) + Parcela B × (IGP-M − Fator X)** | 18 | Regra explícita |
| F8 | Revisão periódica = **Parcela A atualizada + novo valor da Parcela B**; depreciação = base × taxa depreciação; remuneração = base × taxa retorno | 19 | Regra explícita |
| F9 | P&D/EE = **0,5%** da receita operacional líquida (distribuidoras); **1%** demais agentes | 14 | Regra explícita |
| F10 | Exemplo composição R$100 (pré Lei 12.783): energia 35,80; transmissão 6,70; distribuição 23,60; encargos 9,50; tributos 24,50 | 10 | Regra explícita (valor) |
| F11 | Exemplo composição R$100 (pós Lei 12.783, redução média 20,2%): energia 30,20; transmissão 2,60; distribuição 23,60; encargos 3,90; tributos 19,50 | 10–11 | Regra explícita (valor) |

## Observações de classificação
- **Regras explicitamente apresentadas:** F1–F11 (com valores e fórmulas).
- **Interpretação (nossa):** nossa ferramenta usa os valores **líquidos** da base ANEEL (sem tributos); os tributos e encargos já estão embutidos nas TUSD/TE que armazenamos, não precisamos modelá-los no MVP.
- **Não determinado:** fórmula de faturamento de demanda (contratada/medida/reativos), EPI/ACL, bandeiras tarifárias — ausentes deste documento.

## Mapeamento para os demais arquivos da KB
- Composição → `cartilha_2013_composicao_tarifa.md`
- Encargos → `cartilha_2013_encargos_setoriais.md`
- Tributos → `cartilha_2013_tributos.md`
- Reajuste/revisão → `cartilha_2013_reajuste_revisao.md`
- Modalidades → `cartilha_2013_modalidades_tarifarias.md`
