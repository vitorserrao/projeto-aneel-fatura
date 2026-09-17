# Regras tarifárias

> **Estado atual (pós-Sprint 1):** nenhuma **regra regulatória** foi definida
> nem implementada. O que o Sprint 1 implementou é a **mecânica linear
> determinística** (`custo = quantidade × valor`), uma premissa estrutural
> (A1), que depende de parcelas já normalizadas pela ingestão. Cada fórmula e
> critério regulatório continua listado abaixo como "a validar" e será
> preenchido apenas com fonte documental da ANEEL — nunca por suposição.

## Regras a documentar (a validar)

As regras abaixo aparecem no escopo do MVP, mas ainda **não** possuem fórmula
fechada. Devem ser preenchidas apenas quando uma definição formal estiver
disponível, referenciando a fonte (documento/dataset ANEEL) — nunca por suposição.

1. **Cálculo de energia** — custo associado ao consumo de energia (MWh) por
   posto e componente.
2. **Cálculo de demanda** — custo associado à demanda contratada (kW) por posto
   e componente.
3. **TE (Tarifa de Energia)** — tratamento e aplicação.
4. **TUSD (Tarifa de Uso do Sistema de Distribuição)** — tratamento e aplicação.
5. **Cálculo ACR** — composição do custo total.
6. **Comparação de modalidades** — azul, verde e convencional (quando aplicável).
7. **EPI simplificado** — fórmula fechada a definir.
8. **Projeção** — baseline estatístico simples (ex.: médias móveis), a definir.

## Proveniência e rastreabilidade

- Cada regra registrada aqui deve citar a fonte (documento ANEEL, versão do
  dataset, resolução).
- Nenhuma regra é implementada sem sua entrada correspondente neste documento.
- Assunções explícitas e pendências também ficam em [`premissas.md`](premissas.md).
