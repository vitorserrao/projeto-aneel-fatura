# Regras tarifárias

> **Estado atual (pós-Sprint 1):** nenhuma **regra regulatória** foi definida
> nem implementada. O que o Sprint 1 implementou é a **mecânica linear
> determinística** (`custo = quantidade × valor`), uma premissa estrutural
> (A1), que depende de parcelas já normalizadas pela ingestão. Cada fórmula e
> critério regulatório continua listado abaixo como "a validar" e será
> preenchido apenas com fonte documental da ANEEL — nunca por suposição.
>
> **Exceção (17/09/2026):** a cobrança de **reativos excedentes** (art. 304 da
> REN 1.000/2021) foi fechada com fonte oficial e implementada — ver seção
> "Regras implementadas".

## Regras implementadas

### Reativos excedentes — REN ANEEL nº 1.000/2021, art. 304

**Fonte:** texto integral do DOU (20/12/2021) + fórmulas transcritas das
imagens (`conhecimento/regras/ren1000_2021_formulas_dou.md`, imagem 009).
Aproximação de cálculo registrada na premissa A6 (`docs/premissas.md`).

**Condição:** consumidor do Grupo A (inclusive optante pela tarifa do Grupo B)
com fator de potência abaixo de **0,92** — indutivo ou capacitivo.

**Fórmulas oficiais:**
```text
ERE    = Σ_T [ EEAMT × ( fR/fT − 1 ) ] × VRERE
DRE(p) = [ max_T ( DAMT × fR/fT ) − DAF(p) ] × VRDRE
```

**Implementação (aproximação A6, agregados mensais por posto):**
- `fp = EA / √(EA² + ER²)` por posto/natureza (sem dados horários).
- **Energia (ERE):** `EEAM(p) × (0,92/fp − 1) × VRERE` em MWh —
  indutivo em ponta e fora ponta; **capacitivo** apenas no fora ponta
  (janela 0h–6h, alocação proporcional 6h/21h).
- **Demanda (DRE):** `[D_medida × 0,92/fp − DAF] × VRDRE` em kW —
  Azul: por posto (ponta e fora ponta); Verde: linha única com a demanda única.
- **`VRERE`** = tarifa de energia `TE` do subgrupo **B1** (bandeira verde), R$/MWh.
- **`VRDRE`** = tarifa de demanda `TUSD` do posto **fora ponta** da modalidade
  **Azul** do subgrupo do consumidor, R$/kW (vale para Azul e Verde).
- Tarifa de referência ausente ou ambígua → linhas de reativos **omitidas** e
  `Nota` na resposta (decisão do usuário; coerente com a premissa A5).
- **§3º do art. 304 implementado (18/09/2026):** quando o `VRDRE` do subgrupo
  for nulo, o serviço usa o **nível de tensão imediatamente inferior**
  (ordem A1 → A2 → A3 → A3a → A4 → AS).

**Decisões do usuário (17/09/2026):**
- Campos `reativo_*_ponta/fora_ponta` = parcela **indutiva**; campos
  `reativo_*_capacitiva_*` = parcela **capacitiva** (janela 0h–6h, fora ponta).
- Verde: excedente de demanda reativa em **linha única** com demanda única.

### Tributação da fatura e ultrapassagem

- `aplicar_tributos=True` tributa as linhas **TARIFA** e **ULTRAPASSAGEM**
  (fórmula "dentro" aditiva ou "fora" multiplicativa, conforme `tipo_icms`).
  Demais linhas (reativos, bandeira, CIP, outros) **não** são tributadas.
- **Fonte/validação:** artigo XX ERIAC 2025 (K. Wu / F.Y.K. Takigawa), Consumidor 1
  — CPFL Piratininga A4 Verde 05/2018. Com PIS 1,35% + COFINS 6,20% + ICMS 18%
  e ultrapassagem tributada, o motor reproduz TUSD Demanda, TUSD Energia, TE e
  Ultrapassagem do artigo com diferença ≤ R$ 0,06 (o artigo tem typos: PIS
  impresso 1,55% mas calculado 1,35%; demanda FP impressa 289,27 kW mas
  calculada 283,27 kW).

### Reativos — modo "excedente direto" (faturas antigas)

- `reativos_direto=True` replica o Simulador/XLSM do projeto anterior: os campos
  `reativo_energia_*_kvArh`/`reativo_demanda_*_kvAr` são o **excedente já
  calculado** e são cobrados com `tarifa_reativo_energia_r_kvarh` (R$/kVArh) e
  `tarifa_reativo_demanda_r_kvar` (R$/kVAr) **sem tributos**.
- A tarifa de energia reativa do modo direto deve ser **calculada** como
  `TE B1 Residencial / 1000` (regra da planilha). Ex.: CPFL-PIRATININGA
  05/2018 → 282,09 R$/MWh / 1000 = 0,28209 R$/kVArh → 39,36 × 0,28209 =
  R$ 11,10.
- Divergência documentada: o artigo XX ERIAC 2025 imprime R$ 14,91 para
  39,36 kVArh, o que implicaria ~0,37881 R$/kVArh — tarifa não publicada;
  o projeto **não** adota esse valor derivado.

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

## Regras confirmadas por faturas reais (18/09/2026)

Validadas contra faturas reais (Copel 04/2023, CEMIG 09/2023, Equatorial 12/2024
e ENEL 01/2021 — ver `docs/validacao_faturas_reais/relatorio_final.md`):

1. **TE/TUSD de energia** — fórmula "por fora"
   `tarifa / ((1 − PIS − COFINS) × (1 − ICMS))` reproduz as faturas em centavos.
2. **Demanda** — `faturada = máx(medida, contratada)`. Quando
   `faturada > medida`, a parcela `faturada − medida` (contratada não
   utilizada) é **isenta de ICMS** (só PIS/COFINS) — `demanda_isenta_icms`.
3. **Reativo excedente (modo direto)** — quantidade informada × tarifa direta;
   **pode ser tributado** conforme a distribuidora (`tributar_reativos`):
   CEMIG e Equatorial tributam; Copel e o artigo não.
4. **Bandeira** — adicional por kWh confere (ENEL Δ +0,19).
5. **Pendente:** modo ENEL "só ICMS" (PIS/COFINS em linhas próprias) e bandeira
   por posto.

## Reativos — tarifa automática (VRERE/VRDRE) — 25/09/2026

- No modo **"excedente direto"**, se o chamador **não** informar as tarifas,
  o serviço busca automaticamente:
  - **Energia reativa (kVArh)** → `VRERE / 1000` = TE bandeira verde B1 / 1000
    (R$/kVArh).
  - **Demanda reativa (kVAr)** → `VRDRE` = TUSD demanda Fora Ponta da Azul do
    subgrupo (R$/kVAr), com §3º (nível de tensão inferior se nulo).
- Tarifa manual informada tem **prioridade** (override) — necessário para
  exceções como a Copel (fatura usa 0,333333, diferente do VRERE/1000).
- Validado contra faturas reais: CEMIG (0,31364 = 313,64/1000) e Equatorial
  (0,290980 = 290,98/1000) batem exato; Copel é a exceção documentada.
- Front: checkbox "Buscar tarifa de reativo automaticamente (VRERE/VRDRE)"
  ligado por padrão — o usuário informa só as quantidades.

## Proveniência e rastreabilidade

- Cada regra registrada aqui deve citar a fonte (documento ANEEL, versão do
  dataset, resolução).
- Nenhuma regra é implementada sem sua entrada correspondente neste documento.
- Assunções explícitas e pendências também ficam em [`premissas.md`](premissas.md).
