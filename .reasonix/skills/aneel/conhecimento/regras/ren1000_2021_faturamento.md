# Regras oficiais de faturamento e modalidades — REN 1.000/2021 (ANEEL)

> **Origem:** pesquisa em fontes oficiais (ANEEL / Governo Federal) realizada para fechar
> pendências do motor ACR. Fontes citadas ao final.
> **Status:** **confirmado no texto integral do DOU** (edição de 20/12/2021) em
> 17/09/2026 — texto extraído do HTML e fórmulas transcritas das imagens do DOU.
> Detalhes completos em **`ren1000_2021_formulas_dou.md`** (fórmulas + arts. 281–326).
> Antes de implementar, conferir a **redação consolidada vigente** (REN 1.000/2021 já
> foi alterada por REN posteriores, ex.: REN 1.059/2023 no art. 301).
> **Hierarquia de confiança:** esta fonte está no nível **1 (legislação/regulação oficial)** —
> prevalece sobre o projeto anterior e sobre inferências.

## 1. Faturamento de demanda *(REN 1.000/2021, arts. 292, 301)*

- **Demanda faturável** = **maior valor entre demanda contratada e demanda medida**
  (para unidade consumidora convencional ou horo-sazonal; há exceções para
  Rural/sazonal e outras condições específicas).
- **Ultrapassagem de demanda:** cobrada quando a demanda medida exceder a contratada em:
  - **5%** — consumidores em geral;
  - **1%** — geradores/importadores/exportadores;
  - **10%** — outra distribuidora.
- **Fórmula da ultrapassagem** (art. 301 §1º, imagem 008 do DOU):
  ```
  CULTRAPASSAGEM(p) = [ DAM(p) − DAC(p) ] × 2 × VRDULT(p)
  ```
  onde `DAM(p)` = demanda ativa medida, `DAC(p)` = demanda ativa contratada e
  `VRDULT(p)` = valor de referência de ultrapassagem (tarifa de demanda do posto `p`
  aplicável aos subgrupos A ou TUSD-Consumidores-Livres). A cobrança incide sobre a
  **diferença total** `DAM − DAC`, ao **dobro** da tarifa, quando a demanda medida
  exceder a contratada além da tolerância (5% consumidor; 1% gerador/importador/
  exportador; 10% outra distribuidora). ⚠️ REN 1.059/2023 alterou os incisos do caput
  (demanda de injeção × demanda de consumo).
- **Demanda proporcional** (período de faturamento < 27 ou > 33 dias): aplicar fator
  de proporcionalidade `FD_pr` (fórmula específica no art. 301).
- **Fator de potência:** limite mínimo **0,92** (indutivo ou capacitivo).
  Abaixo disso, cobra-se **energia/demanda reativa excedente**.
- **Reativos excedentes:** valor = quantidade de reativo excedente (kVArh na energia,
  kVAr na demanda) × tarifa correspondente.

### 1.1 Fórmulas oficiais confirmadas no DOU (transcrição das imagens)

- **Energia ativa do Grupo A — art. 293, caput (imagem 006):**
  ```
  FEA(p) = EEAM(p) × TECOMP(p)
  ```
- **Energia ativa com excedente — art. 293 §1º (imagem 007):** quando
  `EEAMCICLO > MWmédioCONTRATADO × HORASCICLO`:
  ```
  FEA(p) = MWmédioCONTRATADO × HORASCICLO × TECOMP(p) × EEAM(p) / EEAMCICLO
  ```
  (faturamento limitado ao montante contratado, rateado por posto pela medição).
- **Reativos excedentes — art. 304 (imagem 009):**
  ```
  ERE    = Σ_T [ EEAMT × ( fR/fT − 1 ) ] × VRERE
  DRE(p) = [ max_T ( DAMT × fR/fT ) − DAF(p) ] × VRDRE
  ```
  somente nos intervalos `T` com `fT < 0,92` — **capacitivo** na janela de 6h entre
  23h30 e 6h30; **indutivo** no período complementar. `fR = 0,92`;
  `VRERE` = TE bandeira verde do B1; `VRDRE` = tarifa de demanda fora de ponta da Azul.
- **Demais fórmulas** (ERD, K, FRC, n, tarifa proporcional, compensações arts. 440/441,
  iluminação pública art. 472) → ver **`ren1000_2021_formulas_dou.md`**.

## 2. Elegibilidade de modalidades *(REN 1.000/2021, arts. 219, 220)*

| Grupo | Modalidade | Aplicação |
|---|---|---|
| **A** | **Azul** | Todos os subgrupos A; **obrigatória** em A1, A2, A3 (tensão ≥ 69 kV) |
| **A** | **Verde** | **Apenas A3a, A4 e AS** (tensão < 69 kV) |
| **A** | **Convencional Binômia** | **Extinta** — não é mais publicada na revisão tarifária |
| **B** | **Convencional Monômia** | Compulsória/automática |
| **B** | **Branca** | Opcional; **vedada** a baixa renda, iluminação pública e pré-pagamento |

- **Limite Grupo A → Grupo B:** unidade com **potência total dos transformadores
  ≤ 112,5 kVA** pode optar por tarifa do Grupo B (art. 292).
- **Consumidor potencialmente livre:** avaliar enquadramento conforme tensão/potência
  e as condições de migração (fora do escopo direto desta nota).

## 3. Estrutura de cada modalidade *(REN 1.000/2021, arts. 213, 214)*

- **Verde (Grupo A):** **1 tarifa de demanda única** (R$/kW, sem posto) +
  1 tarifa de consumo ponta + 1 consumo fora ponta (R$/MWh).
- **Azul (Grupo A):** **1 tarifa de demanda ponta + 1 demanda fora ponta** (R$/kW)
  \+ 1 consumo ponta + 1 consumo fora ponta (R$/MWh).
- **Branca (Grupo B):** três postos (ponta, intermediário, fora ponta) de consumo.

## 4. Postos tarifários *(REN 1.000/2021)*

- **Ponta:** **3 horas consecutivas** (definidas por resolução), exceto sábados,
  domingos e feriados.
- **Intermediário:** **1 hora antes + 1 hora depois** da ponta — **exclusivo da
  Tarifa Branca (Grupo B)**.
- **Fora ponta:** as demais horas.
- **Consequência para o motor ACR (Grupo A):** só são necessários **Ponta** e
  **Fora Ponta**; `Intermediário` **não se aplica** ao Grupo A.

## 5. Tributos na conta (para comparação ACR × ACL) *(fonte oficial: MME/ANEEL)*

- A **conta de luz** = tarifa ANEEL **+ tributos** (ICMS, PIS, COFINS) **+ CIP**.
- **Fórmula oficial da conta:**
  ```
  Valor da conta = Consumo × ( Tarifa / (1 − PIS − COFINS − ICMS) ) + CIP
  ```
- ⚠️ **Conflito com o projeto anterior (registrar, não esconder):**
  - **Fonte oficial:** `tarifa / (1 − PIS − COFINS − ICMS)` (todos somados no denominador).
  - **Projeto anterior (Kevin Wu):** `tarifa / ((1 − PIS − COFINS) × (1 − ICMS))`
    (ICMS aplicado de forma multiplicativa).
  - **Pela hierarquia de confiança, prevalece a fonte oficial.**
  - **Observação do novo projeto:** a base de dados ANEEL usada é **líquida**
    (sem tributos). A decisão de incluir ou não tributos na fatura do MVP
    permanece **do usuário** (ver `pontos_pendentes_pesquisa.md`).

## 6. O que esta fonte AINDA NÃO resolve

- **Precedência entre vigências sobrepostas** (P6) — não localizado nem no texto
  integral extraído do DOU (ver `pontos_pendentes_pesquisa.md`).
- **Arredondamento monetário** (P7) — não localizado no texto extraído do DOU.
- **EPI / ACR × ACL** — nenhuma fórmula oficial encontrada em fonte ANEEL/Governo;
  tratar como metodologia (ver `pontos_pendentes_pesquisa.md`).
- **Consolidação com REN posteriores** — a redação original de 20/12/2021 já foi
  alterada (ex.: REN 1.059/2023 no art. 301). Usar a versão consolidada vigente.

## Fontes

- ANEEL — "Modalidades Tarifárias" (gov.br/aneel).
- REN ANEEL nº 1.000/2021 — **texto integral do DOU** (20/12/2021, Edição 238,
  Seção 1, Página 206), extraído em 17/09/2026 de
  https://www.in.gov.br/en/web/dou/-/resolucao-normativa-aneel-n-1.000-de-7-de-dezembro-de-2021-368359651
  — arts. 213, 214, 219, 220, 281–326 (faturamento), 109, 173, 440, 441, 472.
  Fórmulas (imagens do DOU) transcritas em `ren1000_2021_formulas_dou.md`.
- MME/ANEEL — composição da conta de luz (tributos e fórmula).
- REN ANEEL nº 414/2010 (consolidada/alterada pela REN 1.000/2021).

## Itens de verificação (antes de implementar)

1. ✅ Fórmula da ultrapassagem (art. 301 §1º) — confirmada no DOU e em cópias
   oficiais (imagem 008).
2. ✅ Faturamento de energia ativa do Grupo A (art. 293 caput e §1º) — confirmado
   (imagens 006/007).
3. ✅ Reativos excedentes (art. 304) — fórmula e condições confirmadas (imagem 009).
4. ⚠️ Conferir a **redação consolidada vigente** (REN 1.059/2023 e posteriores) para
   os artigos alterados (especialmente art. 301).
5. ⚠️ Revisar as transcrições das imagens 010, 011 e 012 (compensações e iluminação
   pública) — ver notas em `ren1000_2021_formulas_dou.md`.
6. Confirmar **consequências para ACR × ACL**: incluir tributos ou usar base líquida.

## Uso futuro

- **Motor ACR:** demanda faturável, ultrapassagem e reativos (item 1);
  estrutura de parcelas (item 3).
- **Otimização:** elegibilidade das modalidades por subgrupo (item 2).
- **Normalização:** posto Intermediário fica fora do Grupo A (item 4).
- **Modelo de saída:** tributos sim/não e fórmula oficial (item 5).
