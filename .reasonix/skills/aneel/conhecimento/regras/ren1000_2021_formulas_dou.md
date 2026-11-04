# Fórmulas da REN 1.000/2021 publicadas como imagem no DOU (extração 17/09/2026)

> **Origem:** Diário Oficial da União — REN ANEEL nº 1.000, de 7 de dezembro de 2021.
> Publicado em: **20/12/2021 | Edição 238 | Seção 1 | Página 206**.
> Link: https://www.in.gov.br/en/web/dou/-/resolucao-normativa-aneel-n-1.000-de-7-de-dezembro-de-2021-368359651
>
> **Método de extração:**
> 1. Texto integral extraído do HTML da página (814 KB) — artigos e legendas em texto.
> 2. As **12 fórmulas** estão publicadas como **imagens JPG** (nomes
>    `1_MME_14112904_001` a `1_MME_14112904_012`) e foram **transcritas manualmente**
>    das imagens pelo usuário em 17/09/2026.
> 3. Conferência independente (web): art. 293 §1º e art. 301 §1º conferidos em
>    cópias oficiais da REN 1.000/2021 — **idênticos à transcrição**.
>
> **Hierarquia de confiança:** nível **1 (legislação/regulação oficial)**.
> **Atenção:** a versão vigente é a **consolidada** (REN 1.000/2021 + alterações
> posteriores, ex.: REN 1.059/2023 que alterou o art. 301). Antes de implementar,
> conferir a redação consolidada vigente.

## Índice das 12 imagens

| Imagem | Artigo | Fórmula |
|---|---|---|
| 001 | Art. 109 caput | `ERD` — encargo de responsabilidade da distribuidora |
| 002 | Art. 109 | `K` — fator de cálculo do ERD |
| 003 | Art. 109 | `FRC` — fator de recuperação do capital |
| 004 | Art. 109 | `n` — vida útil em função da depreciação `d` |
| 005 | Art. 173 §2º | `TP` — tarifa proporcional |
| 006 | Art. 293 caput | `FEA(p)` — faturamento de energia ativa do Grupo A |
| 007 | Art. 293 §1º | `FEA(p)` — com excedente de energia contratada (MWmédio) |
| 008 | Art. 301 §1º | `CULTRAPASSAGEM(p)` — ultrapassagem |
| 009 | Art. 304 | `ERE` e `DRE(p)` — reativos excedentes |
| 010 | Art. 440 | Compensação por descumprimento de prazos |
| 011 | Art. 441 | Compensação por suspensão indevida |
| 012 | Art. 472 | Consumo estimado de iluminação pública |

---

## IMAGEM 001 — Art. 109 caput — `ERD`

**Contexto antes:** *"Art. 109. O encargo de responsabilidade da distribuidora é
determinado pela seguinte equação:"*

```text
ERD = DEMANDAERD × K
```

**Legenda (texto após a imagem):** `ERD` = encargo de responsabilidade da
distribuidora; `DEMANDAERD` = demanda a ser atendida ou acrescida para o cálculo
do ERD, em quilowatt (kW); `K` = fator de cálculo do ERD.

---

## IMAGEM 002 — Art. 109 — `K`

**Contexto antes:** *"K = fator de cálculo do ERD, calculado pela seguinte equação:"*

```text
K = 12 × (TUSD Fio B FP) × (1 − a) × (1 / FRC)
```

**Legenda:** `TUSD Fio B FP` = parcela da TUSD no posto tarifário fora de ponta,
composta pelos custos regulatórios decorrentes do uso dos ativos da distribuidora,
que remunera o investimento, o custo de operação e manutenção e a depreciação dos
ativos, em R$/kW; `a` = relação entre os custos de operação e manutenção (pessoal,
material, serviços de terceiros e outras despesas) e os custos gerenciáveis totais
da distribuidora — Parcela B, definidos na última revisão tarifária; `FRC` = fator
de recuperação do capital.

**Interpretação:** o ERD é um pagamento único que equivale ao valor presente da
receita anual de 12 meses da TUSD Fio B FP líquida da parcela de O&M (`1 − a`),
descontada pelo fator de recuperação de capital (`1/FRC`).

---

## IMAGEM 003 — Art. 109 — `FRC`

**Contexto antes:** *"FRC = o fator de recuperação do capital que traz a valor
presente a receita uniforme prevista, sendo obtido pela equação:"*

```text
FRC = [ WACC × (1 + WACC)^n ] / [ (1 + WACC)^n − 1 ]
```

**Legenda:** `WACC` = custo médio ponderado do capital definido na última revisão
tarifária da distribuidora, antes dos impostos; `n` = período de vida útil, em anos,
associado à taxa de depreciação percentual anual `d`.

---

## IMAGEM 004 — Art. 109 — `n`

**Contexto antes:** *"n = o período de vida útil, em anos, associado à taxa de
depreciação percentual anual "d" definida na última revisão tarifária, sendo obtido
pela equação:"*

```text
n = 100 / d
```

**Interpretação:** `d` é percentual anual (ex.: `d = 5` → `n = 20` anos).

---

## IMAGEM 005 — Art. 173 §2º — `TP` (tarifa proporcional)

**Contexto antes:** *"Caso haja alteração na tarifa no decorrer do ciclo de
faturamento, a distribuidora deve aplicar tarifa proporcional, determinada por:"*

```text
TP = Σ(i=1..n) ( Ti × Pi ) / D
```

**Legenda:** `TP` = Tarifa Proporcional a ser aplicada ao faturamento do período;
`Ti` = Tarifa em vigor durante o período `i` de fornecimento; `Pi` = número de dias
em que esteve em vigor a tarifa `i`; `D` = número de dias de efetivo fornecimento,
decorridos entre duas datas consecutivas de leitura.

**Confirmação (pergunta do usuário):** entendimento correto — é a **média ponderada**
das tarifas vigentes no ciclo pelos dias de vigência de cada uma, dividida pelos dias
de efetivo fornecimento.

---

## IMAGEM 006 — Art. 293 caput — `FEA(p)` Grupo A

**Contexto antes:** *"Art. 293. A distribuidora deve faturar o consumo de energia
elétrica ativa da unidade consumidora do grupo A, e, caso aplicável, das instalações
dos demais usuários, exceto nos casos de opção de faturamento pelo grupo B, pela
seguinte fórmula:"*

```text
FEA(p) = EEAM(p) × TECOMP(p)
```

**Legenda (após §1º):** `FEA(p)` = faturamento da energia elétrica ativa, por posto
tarifário `p`, em R$; `EEAM(p)` = montante de energia elétrica ativa medido em cada
posto tarifário `p` do ciclo, em MWh; `TECOMP(p)` = para consumidor livre ou especial
com CCER celebrado, tarifa de energia `TE` por posto `p` aplicável aos subgrupos do
grupo A, em R$/MWh, ou, para as demais unidades consumidoras, a tarifa final de
energia elétrica ativa homologada por posto `p`; `p` = posto tarifário, ponta ou fora
de ponta, para as modalidades tarifárias horárias.

---

## IMAGEM 007 — Art. 293 §1º — `FEA(p)` quando EEAM > MWmédio × HORASCICLO

**Contexto antes:** *"§ 1º Para consumidor livre ou especial, quando o montante de
energia elétrica ativa medida for maior que o produto do número de horas do ciclo pelo
limite estabelecido para a energia elétrica ativa contratada, fixado em MWmédio, a
distribuidora deve faturar a energia elétrica ativa por:"*

```text
FEA(p) = MWmédioCONTRATADO × HORASCICLO × TECOMP(p) × EEAM(p) / EEAMCICLO
```

**Legenda:** `MWmédioCONTRATADO` = limite estabelecido para a energia elétrica ativa
contratada, fixado em MWmédio para cada ciclo de faturamento; `EEAMCICLO` = montante
de energia elétrica ativa medido no ciclo de faturamento, em MWh; demais variáveis
como na IMAGEM 006.

**Interpretação:** para livre/especial, quando a medição excede o contratado, o
faturamento de energia ativa fica **limitado ao montante contratado**
(`MWmédioCONTRATADO × HORASCICLO`), rateado entre os postos tarifários pela
participação medida `EEAM(p) / EEAMCICLO`.

**Nota:** `HORASCICLO` não aparece na legenda em texto da página do DOU (só na
fórmula/imagem); a variável foi confirmada em cópia oficial da REN 1.000/2021.

---

## IMAGEM 008 — Art. 301 §1º — `CULTRAPASSAGEM(p)` (ultrapassagem)

**Contexto antes:** *"Art. 301. A distribuidora deve adicionar ao faturamento regular
a cobrança pela ultrapassagem se a demanda medida exceder os seguintes valores em
relação à contratada: I - 1%: para gerador, importador ou exportador; II - 5%: para
consumidor; e III - 10%: para outra distribuidora conectada. § 1º A cobrança pela
ultrapassagem deve ser calculada por:"*

```text
CULTRAPASSAGEM(p) = [ DAM(p) − DAC(p) ] × 2 × VRDULT(p)
```

**Legenda:** `CULTRAPASSAGEM(p)` = valor correspondente à cobrança pela demanda
excedente, por posto tarifário `p`, caso aplicável, em R$; `DAM(p)` = demanda de
potência ativa medida, em cada posto `p` no período de faturamento, em kW; `DAC(p)` =
demanda de potência ativa contratada, por posto `p`, em kW; `VRDULT(p)` = valor de
referência de ultrapassagem, equivalente às tarifas de demanda de potência aplicáveis
aos subgrupos do grupo A ou às TUSD-Consumidores-Livres; `p` = ponta ou fora de ponta.

**Conferência independente:** fórmula idêntica em cópias oficiais da REN 1.000/2021. ✓

**Atenção:** a **REN 1.059/2023** alterou os incisos I e II do caput (passou a tratar
separadamente demanda de **injeção** e de **consumo** de consumidor e gerador).
Usar a **redação consolidada vigente**.

---

## IMAGEM 009 — Art. 304 — `ERE` e `DRE(p)` (reativos excedentes)

**Contexto antes:** *"Art. 304. A distribuidora deve cobrar o montante de energia
elétrica e demanda de potência reativas excedentes da unidade consumidora do grupo A,
incluindo a que optar pelo faturamento com a aplicação da tarifa do grupo B, conforme
as seguintes equações:"*

```text
ERE    = Σ(T=1..n) [ EEAMT × ( fR/fT − 1 ) ] × VRERE

DRE(p) = [ max(T=1..n) ( DAMT × fR/fT ) − DAF(p) ] × VRDRE
```

**Legenda:** `ERE` = valor da energia elétrica reativa excedente à quantidade permitida
pelo fator de potência de referência `fR`, no período de faturamento, em R$;
`EEAMT` = energia elétrica ativa medida em cada intervalo `T` de uma hora, em MWh;
`fR` = fator de potência de referência igual a **0,92**; `fT` = fator de potência da
unidade consumidora, calculado em cada intervalo `T` de uma hora; `VRERE` = valor de
referência equivalente à tarifa de energia `TE` da **bandeira verde** aplicável ao
subgrupo **B1**, em R$/MWh; `DRE(p)` = valor da demanda de potência reativa excedente,
por posto `p`, em R$; `DAMT` = demanda de potência ativa medida no intervalo de
integralização de uma hora `T`, em kW; `DAF(p)` = demanda de potência ativa faturável,
em cada posto `p`, em kW; `VRDRE` = valor de referência, em R$/kW, equivalente às
tarifas de demanda de potência — para o posto **fora de ponta** — das tarifas
aplicáveis aos subgrupos do grupo A para a modalidade tarifária horária **azul**;
`MAX` = função que identifica o valor máximo da equação, dentro dos parênteses
correspondentes, em cada posto `p`; `T` = intervalo de uma hora; `n` = número de
intervalos `T` por posto `p` no período de faturamento.

**§1º — condição de apuração (texto):**
- No período de **6 horas consecutivas** definido pela distribuidora **entre 23h30 e
  6h30**: apenas os `fT` **menores que 0,92 capacitivo**, verificados em cada hora.
- No período diário **complementar**: apenas os `fT` **menores que 0,92 indutivo**.

**§3º — quando `VRDRE` for nulo:** usar o valor do **nível de tensão imediatamente
inferior**.

---

## IMAGEM 010 — Art. 440 — compensação por descumprimento de prazos

**Contexto antes:** *"Art. 440. No caso de não cumprimento dos prazos do Anexo IV, a
distribuidora deve creditar ao consumidor e demais usuários a seguinte compensação:"*

```text
Compensação = k1 + k2 × VRC × log( Pv / Pr )
```

**Legenda:** `Pv` = Prazo verificado; `PR` = Prazo regulatório; `VRC` = valor
monetário base para o cálculo da compensação, que corresponde ao Encargo de Conexão
Parcela B — `ECCD(PB)` para unidades do subgrupo A1, ou ao Encargo de Uso do Sistema
de Distribuição correspondente à parcela TUSD Fio B — `EUSDB`, para os demais
subgrupos; `k1` = coeficiente de majoração da parte fixa da compensação (50% do custo
administrativo de inspeção homologado pela ANEEL, conforme o tipo de conexão);
`k2` = coeficiente de majoração da parte variável da compensação.

> ⚠️ **A conferir:** notação do `log` (natural?) e se `k1` entra como valor absoluto
> somado (a legenda define `k1` como percentual do custo administrativo).

---

## IMAGEM 011 — Art. 441 — compensação por suspensão indevida

**Contexto antes:** *"Art. 441. No caso de suspensão indevida do fornecimento de
energia elétrica ... a distribuidora deve creditar ao consumidor e demais usuários a
seguinte compensação:"*

```text
Compensação = ( VRC / 730 ) × T × 200
```

**Legenda:** `VRC` = idem IMAGEM 010; `730` = número médio de horas no mês;
`T` = tempo compreendido entre o início da suspensão indevida e o restabelecimento do
fornecimento, em horas e centésimos de horas.

> ⚠️ **A conferir:** o fator `200` (pode ser `2`/`200%`?); conferir na imagem e na
> redação consolidada.

---

## IMAGEM 012 — Art. 472 — consumo estimado de iluminação pública

**Contexto antes:** *"IV - nas demais situações: o consumo mensal por ponto de
iluminação deve ser estimado considerando a seguinte expressão:"*

```text
Consumo Mensal (kWh) = [ Carga × ( n × Tempo − DIC/2 ) ] / 1.000
```

**Legenda:** `Carga` = potência nominal total do ponto de iluminação em Watts,
incluídos os equipamentos auxiliares, conforme art. 473, devendo ser proporcionalizada
em caso de alteração durante o ciclo; `Tempo` = tempo considerado para o faturamento
diário da iluminação pública: 24 horas para logradouros que necessitem de iluminação
permanente, ou tempo médio anual por município homologado no Anexo I da Resolução
Homologatória ANEEL nº 2.590, de 13 de agosto de 2019; `DIC` = Duração de Interrupção
Individual da unidade consumidora que agrega os pontos de iluminação.

> ⚠️ **A conferir:** definição de `n` (dias do ciclo?) e o termo `DIC/2`.

---

## Regras do Capítulo X (Do Faturamento) confirmadas no texto integral

> Extraídas do HTML do DOU em 17/09/2026. Números dos artigos da redação original
> de 20/12/2021 (consolidar com REN posteriores antes de implementar).

- **Art. 281** — faturamento mensal; vedado mais de um faturamento no mesmo mês civil,
  exceto nas situações previstas na Resolução.
- **Art. 282** — faturamento corresponde ao mês civil para grupo A e para grupo B em
  que a distribuidora optou pela não instalação de medição (art. 228 §1º).
- **Art. 283** — faturar com as leituras do sistema de medição; exceções sem leitura:
  encerramento contratual (com concordância, art. 141), defeito na medição (art. 255),
  impedimento de acesso (art. 277), leitura plurimensal sem autoleitura (art. 288),
  estimativa por inexistência de medição (art. 319), ausência temporária de medição
  (art. 320), emergência/calamidade/força maior (art. 321).
- **Art. 284** — pode usar memória de massa para faturar.
- **Art. 285** — grupo B com leitura fora do intervalo: < 27 dias → faturar o medido,
  vedado custo de disponibilidade; > 33 dias → proporcionalizar pelo máximo de dias.
- **Art. 286** — grupo A fora do mês civil: < mês civil → faturar o medido;
  > mês civil → proporcionalizar o consumo pelos dias do mês civil; demanda → art. 294.
- **Art. 287** — migração para o ACL: se período < 27 dias, proporcionalizar a demanda
  final pelos dias de efetivo fornecimento em relação a 30 dias.
- **Art. 288** — leitura plurimensal: faturar mensalmente por leitura, autoleitura ou
  média aritmética dos 12 últimos ciclos; sem histórico → custo de disponibilidade
  (art. 291) + valores contratados se aplicável.
- **Art. 289** — impedimento de acesso: demanda ativa = contratada ou média dos 12
  últimos ciclos; demais grandezas = médias dos 12 últimos ciclos.
- **Art. 290** — grupo B fatura o **maior** entre consumo de energia ativa e custo de
  disponibilidade; exceções: iluminação pública, SIGFI/MIGDI, pré-pagamento.
- **Art. 291** — custo de disponibilidade: **30 kWh** (monofásico/bifásico a 2
  condutores), **50 kWh** (bifásico a 3 condutores), **100 kWh** (trifásico).
  Baixa renda: benefício tarifário aplica sobre o custo de disponibilidade.
- **Art. 292** — grupo A pode optar por faturamento do grupo B se: transformadores
  ≤ 112,5 kVA; ou ≤ 1.125 kVA (cooperativa de eletrificação rural); ou hotelaria/
  pousada em área de veraneio/turismo (qualquer potência); ou carga de refletores de
  iluminação ≥ 2/3 da carga instalada (atividades esportivas/parques agropecuários).
- **Art. 293** — `FEA(p)` — ver IMAGENS 006/007. §2º: sem avaliação por posto,
  segmentar proporcionalmente às horas de cada segmento. §3º: com CUSD, a TUSD em
  R$/MWh incide sobre o total de energia ativa medida, observando postos.
- **Art. 294** — demanda faturável:
  - rural ou sazonal: **maior** entre a demanda medida no ciclo ou **10% da maior
    demanda medida nos 11 ciclos anteriores**;
  - demais usuários: **maior** entre a demanda medida no ciclo e a **contratada**.
  - Regras adicionais para central geradora, importador/exportador (§§1º–3º).
- **Arts. 295–299** — sazonalidade: solicitação do consumidor; atividade com
  matéria-prima de agricultura/pecuária/pesca/extração de sal/calcário; relação entre
  soma dos 4 menores e 4 maiores consumos ≤ 20% nos 12 ciclos; análise em 5 dias úteis
  (10 com vistoria); reavaliação a cada 12 ciclos.
- **Art. 300** — demanda complementar (rural/sazonal sem medição por posto): a cada 12
  ciclos, no mínimo 3 demandas faturadas ≥ contratadas; senão, cobrar complementares
  pelas maiores diferenças entre contratada e faturada.
- **Art. 301** — ultrapassagem — ver IMAGEM 008 (tolerâncias 1%/5%/10%; fórmula com
  fator 2; isenções §2º; reserva de capacidade §3º).
- **Art. 302** — `fR` = **0,92** (indutivo ou capacitivo) para grupo A.
- **Art. 303** — grupo B (sem fator de potência de referência) **não paga** reativo
  excedente.
- **Art. 304** — `ERE`/`DRE` — ver IMAGEM 009.
- **Art. 305** — compensação de perdas técnicas quando medidor no secundário do
  transformador do consumidor: **1%** se tensão ≥ 69 kV; **2,5%** se < 69 kV.
- **Art. 306** — perdas em linhas/instalações de interesse restrito: metodologia PRODIST.
- **Art. 307** — bandeiras aplicadas sobre o **consumo faturado**, com tarifa
  proporcional aos dias de vigência de cada bandeira.
- **Art. 308** — período de aplicação = mês subsequente à divulgação; se não houver
  tempo hábil, usar bandeira do mês anterior e compensar diferenças no mês seguinte.
- **Art. 309** — bandeira diferente de verde: adicionar à tarifa de energia o valor
  fixado pela ANEEL; benefícios tarifários **não incidem** sobre o adicional, exceto
  tarifa social baixa renda e redução de irrigação/aquicultura.
- **Art. 310** — revisão de faturamento e recuperação de receita consideram as
  bandeiras vigentes em cada ciclo.
- **Arts. 311–317** — período de testes e ajustes: 3 ciclos; enquadramento Azul testa
  só a ponta; acréscimo de demanda > 5% da contratada abre teste; ultrapassagem no
  teste: início de fornecimento > 35% da inicial; demais: nova contratada + 5% da
  anterior + 30% da adicional; ajuste de fator de potência sem cobrança por 3 ciclos.
- **Art. 318** — baixos valores: acumular cobrança por até 3 ciclos.
- **Art. 319** — estimativa sem medição: carga instalada × período × fatores de
  carga/demanda típicos.
- **Art. 320** — ausência temporária de medição: média dos 12 últimos ciclos; não
  cobrar reativos excedentes; > 30 dias sem medidor por responsabilidade da
  distribuidora → custo de disponibilidade (+ demanda contratada se aplicável).
- **Art. 321** — emergência/calamidade/força maior: faturar pela média dos 12 ciclos;
  acerto no ciclo subsequente, sem limitação de 3 ciclos e sem devolução em dobro.
- **Art. 322** — suspensão do fornecimento: grupo B → maior entre custo de
  disponibilidade e consumo; grupo A → demanda contratada enquanto vigente o contrato.
- **Art. 323** — faturamento incorreto (responsabilidade da distribuidora):
  a menor → cobrar limitado aos últimos 3 ciclos; a maior → devolver (em dobro, com
  IPCA e juros de 1% a.m. pro rata die) os últimos 60 ciclos; devolução simples se
  motivo atribuível exclusivamente ao consumidor ou a terceiro qualificado.
- **Art. 324** — faturamento incorreto (responsabilidade do consumidor): cobrar/
  devolver com IPCA; prazo até 36 meses.
- **Art. 325** — compensação do faturamento: notificação por escrito, reclamação em
  até 30 dias, Ouvidoria com efeito suspensivo da cobrança.
- **Art. 326** — diferenças a cobrar/devolver: aplicar tarifa vigente à época do
  faturamento incorreto (procedimento irregular) etc.

## Uso futuro

- **Motor ACR:** `FEA(p)` (art. 293), demanda faturável (art. 294), ultrapassagem
  (art. 301), reativos excedentes (art. 304), perdas técnicas (art. 305), bandeiras
  (arts. 307–310).
- **Motor ACL/CCER:** limite de faturamento de energia do livre/especial
  (`MWmédioCONTRATADO × HORASCICLO`) — art. 293 §1º.
- **Conexão/orçamento:** ERD/K/FRC/n (art. 109) para encargos de conexão.
- **Qualidade do serviço:** compensações (arts. 440/441) e iluminação pública (art. 472).
- **Pendências P6/P7:** continuam sem localização no texto extraído (precedência de
  vigências sobrepostas e arredondamento monetário não aparecem no Capítulo X).
