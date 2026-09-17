# Regras oficiais de faturamento e modalidades — REN 1.000/2021 (ANEEL)

> **Origem:** pesquisa em fontes oficiais (ANEEL / Governo Federal) realizada para fechar
> pendências do motor ACR. Fontes citadas ao final.
> **Status:** *encontrado em fonte oficial* — **confirmar no texto integral** da
> REN 1.000/2021 nos artigos indicados antes de implementar (ver "Itens de verificação").
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
- **Fórmula da ultrapassagem** (art. 301):
  ```
  D_ultrapassagem(p) = [ PAM(p) − PAC(p) ] × 2 × VD_ult(p)
  ```
  onde `PAM` = potência ativa medida, `PAC` = potência ativa contratada e
  `VD_ult` = valor da tarifa de demanda do posto `p` (a cobrança incide sobre o
  excedente **acima do limite de tolerância**, ao **dobro** da tarifa).
- **Demanda proporcional** (período de faturamento < 27 ou > 33 dias): aplicar fator
  de proporcionalidade `FD_pr` (fórmula específica no art. 301).
- **Fator de potência:** limite mínimo **0,92** (indutivo ou capacitivo).
  Abaixo disso, cobra-se **energia/demanda reativa excedente**.
- **Reativos excedentes:** valor = quantidade de reativo excedente (kVArh na energia,
  kVAr na demanda) × tarifa correspondente.

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

- **Precedência entre vigências sobrepostas** (P6) — não localizado em busca;
  requer leitura do texto integral (regras de vigência/publicação das REH).
- **Arredondamento monetário** (P7) — não localizado; requer texto integral.
- **EPI / ACR × ACL** — nenhuma fórmula oficial encontrada em fonte ANEEL/Governo;
  tratar como metodologia (ver `pontos_pendentes_pesquisa.md`).

## Fontes

- ANEEL — "Modalidades Tarifárias" (gov.br/aneel).
- REN ANEEL nº 1.000/2021 (Regras de Prestação do Serviço Público de Distribuição
  de Energia Elétrica) — arts. 213, 214, 219, 220, 292, 301.
- MME/ANEEL — composição da conta de luz (tributos e fórmula).
- REN ANEEL nº 414/2010 (consolidada/alterada pela REN 1.000/2021).

## Itens de verificação (antes de implementar)

1. Confirmar no **texto integral da REN 1.000/2021** os arts. 292 e 301 (demanda
   faturável, tolerâncias e fórmula da ultrapassagem).
2. Confirmar a lista de subgrupos elegíveis por modalidade (arts. 219/220).
3. Confirmar **consequências para ACR × ACL**: incluir tributos ou usar base líquida.
4. Confirmar se `Intermediário` permanece exclusivo da Branca na revisão vigente.

## Uso futuro

- **Motor ACR:** demanda faturável, ultrapassagem e reativos (item 1);
  estrutura de parcelas (item 3).
- **Otimização:** elegibilidade das modalidades por subgrupo (item 2).
- **Normalização:** posto Intermediário fica fora do Grupo A (item 4).
- **Modelo de saída:** tributos sim/não e fórmula oficial (item 5).
