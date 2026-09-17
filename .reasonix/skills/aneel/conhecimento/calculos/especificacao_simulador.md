# Especificação do Simulador de Fatura — Grupo A (+ B futuro)

> Documento consolidado a partir da **engenharia reversa real** do arquivo
> `Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm` (Kevin Wu),
> executada com leitura célula a célula (openpyxl) e **decodificação do VBA**
> (`vbaProject.bin` via oletools). Rastreabilidade: Arquivo → Aba → Célula /
> módulo VBA.
>
> Hierarquia de confiança: regulamentação oficial (REN 1.000/2021) > dados
> ANEEL > PRORET > metodologia do projeto > Kevin Wu (referência) > inferência.

## 1. Objetivo
Simulador de Fatura de Energia Elétrica (**Grupo A agora; Grupo B em sprint
futura**) que, a partir dos parâmetros de uma unidade consumidora e das
tarifas ANEEL vigentes, calcula a fatura **deterministicamente** e compara as
modalidades tarifárias aplicáveis. A lógica vive no `core/motor_calculo`,
sem dependência de banco/arquivo no core.

## 2. Escopo atual
- Grupo A: Azul e Verde.
- Comparação das modalidades com marcação de "indisponível".
- Base tarifária ANEEL já ingerida (tabela `tarifa_aplicacao_componente`),
  com normalização/sobreposição resolvidas por `detalhe` (padrão
  `Não se aplica`) e horo-sazonal seca/úmida mapeada por mês.
- Tributos **opcionais** (base líquida no MVP; fórmula oficial aditiva quando
  ativados).
- Grupo B (Monômia/Branca), SCEE, Tarifa Social e mínimo faturável: **fora
  desta especificação** (backlog futuro).

## 3. Entradas (perfil do consumidor)
Do `Painel Inicial` (cols B–D, F–H, J–M, O) + validações:
| Campo | Origem planilha | Observação |
|---|---|---|
| Distribuidora | `C5` (dropdown) | casa com `sig_agente` |
| Subgrupo | `C8` (A1..B4) | |
| Modalidade | `C11` | parâmetro da simulação |
| REH | `C14` | resolução ANEEL das tarifas |
| Leitura anterior/atual | `F18`/`F24` (dia/mês/ano C/D 19/24) | valida vigência e ≤1 mês |
| Demanda faturada P/FP | `L5`/`M5` | em kW |
| Demanda contratada P/FP | `L6`/`M6` | em kW |
| Consumo P/FP | `L7`/`M7` | em kWh |
| Reativos (energia/demanda) | `L8..M9` | kVArh / kVAr |
| PIS / COFINS / ICMS / CIP | `H4`/`H5`/`H6`/`H7` | |
| Tipo faturamento ICMS | `R4`/`R5` | por fora=1 / por dentro=2 |
| % consumo mês atual×anterior | `L13`/`M13` | rateio de leitura |
| % intermediário no FP | `L16` | |
| Bandeira (mês anterior/atual) | `F12`/`F13` | VLOOKUP `valores Bandeira` |
| Outros valores | `L20` | doações/taxas |
| Tipo ligação / atividade / cooperativa / GD | `C29`/`C32`/`C35`/`C38` | |

## 4. Regras de validação (Painel Inicial + VBA `Confirmar3`)
- Tributos PIS/COFINS/ICMS ∈ [0,1]; CIP ≥ 0 (G8/G9).
- Consumo/geração/reativos ≥ 0 (K10).
- %mês e %INT/FP ∈ [0,1] (K14/K18/L16).
- Leitura anterior ≥ início vigência (H18) e leitura atual ≤ fim vigência
  (H24); diferença entre leituras ≤ 1 mês (C26/H26).
- `Confirmar3` valida C15/C20/C25/G8/G9/K10/K14/K18/C26 via `CelulaInvalida`
  (nota: bug no VBA — `verificar7` é sobrescrito; irrelevante para o domínio).

## 5. Estrutura do cálculo — Grupo A
Aba `Fatura de Energia - 1` (e `-2`, idênticas salvo tributos).
Para cada modalidade são montadas linhas de cobrança C18:C39 (Verde) e
N18:X39 (Azul):

| Linha | Fórmula (quantidade) | Tarifa |
|---|---|---|
| TUSD demanda P/FP (Azul) | `=I4`/`=J4` (maior p/ Verde: `LARGE`) | `BuscarTarifaMelhorado(...,"R$/kW")` |
| TUSD energia P/FP | `=consP × %mês` | busca R$/MWh ÷1000 |
| TE P/FP | idem | busca TE R$/MWh ÷1000 |
| Bandeira anterior/atual | `=consP × %mês` | VLOOKUP bandeira |
| Ultrapassagem P/FP | `=IF((medida−contratada)>=0, dif, 0)` | `=2 × tarifa_demanda` |
| Reativos energia P/FP | `=I7`/`=J7` | proxy B1 Conv. Residencial |
| Reativos demanda P/FP | `=I8`/`=J8` | proxy tarifa demanda |
| CIP/COSIP | `-` | `=F6` (fixo) |
| Outros | `-` | `=I9` (fixo) |
| **Total** | — | soma das linhas |

Conversões na planilha: tarifa R$/MWh é **dividida por 1000** antes de
multiplicar por kWh (consumo fica em kWh direto). No motor o contrato usa
MWh × R$/MWh (equivalente).

## 6. Busca de tarifas (VBA `BuscarTarifaMelhorado`)
- **Fonte:** `Processamento de Dados`, colunas 28–42 (AB:AP), normalizadas.
- **Assinatura:** 15 critérios (sigla, REH, início/fim vigência, base,
  subgrupo, modalidade, classe, subclasse, detalhe, acessante, posto,
  unidade, TUSD, TE) + `colunaResultado` (1..15 → AB..AP) + `ocorrencia`.
- **Regra:** para i=2..10000, linha casa se **todos** os critérios não-vazios
  forem **igualdade estrita** (`crit="" OR célula=crit`); retorna a
  `ocorrencia`-ésima linha (`célula(27+colunaResultado)`).
- **Erros:** coluna/ocorrência inválida → `#VALUE`; não achou → string
  `"Ocorrência N não encontrada."`. Por isso as fórmulas usam `IFERROR`/`ISTEXT`.
- **Vigência/REH/posto:** SEM lógica interna no VBA — o fallback
  seca/úmida e a vigência ficam **nas fórmulas** (`IFERROR(busca "Ponta
  seca"; busca "Ponta")`). Nosso banco resolve vigência via SQL `BETWEEN`.
- `BuscarTarifa` (função antiga) = mesma coisa sem `ocorrencia` (1ª linha).

## 7. Vigência
- Tarifa aplicável na data de referência: banco usa
  `dat_inicio_vigencia <= data <= dat_fim_vigencia` (equivalente ao VLOOKUP
  TRUE/intervalo da planilha). Fora de vigência → erro 422 (nenhuma tarifa).
- REH selecionada restringe o conjunto (filtro de igualdade).

## 8. REH e seca/úmida
- `C12/C13 = IF(AND(mês>=5, mês<=11), "seca", "úmida")` — **maio a novembro =
  seco; dezembro a abril = úmido** (horo-sazonal pré-REN 1.000/2021).
- Busca tenta `CONCATENATE("Ponta ", C12)` (ex.: "Ponta seca") e, se não
  houver, cai para "Ponta" (`IFERROR`). **Implementado no service**
  (`_posto_sazonal_de`).

## 9. Postos tarifários
- Grupo A: Ponta (3h) e Fora ponta; Intermediário é **exclusivo da Branca**
  (REN 1.000/2021) — fora do Grupo A.
- Horários de ponta por distribuidora: tabela `horario_posto_distribuidora`
  (103 distribuidoras, origem aba `Horários P, INT e FP`).

## 10. Demanda
- **Demanda faturável = máx(contratada, medida)** (REN 1.000/2021, arts.
  292/301) — implementado no motor.
- **Piso da planilha:** `=IF(faturamento=0, 30, valor)` — se não informada,
  usa 30 kW (simplificação do XLSM; exposto como parâmetro `piso_demanda_kw`,
  default 0).
- **Azul** (horária): tarifas de demanda separadas por posto (P/FP).
- **Verde** (horária): **UMA única tarifa de demanda** (REN 1.000/2021,
  inciso II) → demanda faturável **única** = `máx(demanda_medida_unica,
  demanda_contratada_unica)` — SEM separação por posto e **SEM LARGE entre
  P/FP** (o `LARGE` era um artefato do XLSM ao reaproveitar os campos da
  Azul; corrigido em favor da fonte oficial/didática).

## 11. Consumo e rateio
- Consumo do mês é **rateado entre leituras** por `%mês atual × mês anterior`
  (`I13/J13`): `quant_mês_ant = cons × %mês`; `quant_mês_atual = cons × (1−%mês)`.
- **Pendente no motor:** hoje o motor usa o consumo direto, sem `%mês`.
- Branca (futuro): FP é rateado ainda por `%INT/FP`.

## 12. Ultrapassagem (decisão do projeto — BD)
- **Regra adotada (slide didático/XLSM; decisão do usuário):**
  - Aplica-se às modalidades **binômias Azul E Verde**.
  - **Gatilho:** demanda medida excede a contratada em **5%**.
  - **Base:** excedente **TOTAL** `(PAM − PAC)` — sem descontar os 5%.
  - **Fator:** **2×** a tarifa de demanda.
  - Fórmula: `D_ultrapassagem = 2 × VR × (PAM − PAC)`.
- **Azul:** PAM/PAC por posto (P e FP), cada posto cobrado separadamente.
- **Verde:** PAM/PAC únicos (campos `demanda_medida_unica_kw`
  / `demanda_contratada_unica_kw`), uma única cobrança.
- **Divergência documentada (REN):** a interpretação literal da REN
  ("excedente acima do limite de tolerância") sugeriria descontar os 5% da
  base; por decisão explícita do usuário, adotamos a fórmula do slide/XLSM
  (excedente total).

## 13. Reativos
- Fator de potência < **0,92** (indutivo/capacitivo) → cobra excedente de
  energia (kVArh) e demanda (kVAr).
- **Proxy do XLSM:** energia reativa usa a tarifa **TUSD energia de B1
  Convencional Residencial** (`N11`); demanda reativa usa tarifa de demanda
  (`N12`). Não há tarifa de reativo própria no dataset.
- Motor atual: proxy = TUSD energia do próprio perfil (aproximação) —
  **pendência a alinhar**.

## 14. Bandeiras
- Origem: aba `valores Bandeira Tarifária`; fatura usa `VLOOKUP(mês/ano,
  B:C, 2, 0)` — colunas B (competência) e C (R$/kWh).
- **Tabela `Tabela11`:** competência mensal de jan/2015 em diante; categorias
  Verde/Amarela/Vermelha P1/Vermelha P2; valores R$/MWh com
  `R$/kWh = R$/MWh ÷ 1000`.
- Histórico oficial (J:O): Resolução Homologatória + link ANEEL + vigência;
  ex.: Amarela 15→29,89; Vermelha P1 30→65; Vermelha P2 35→97,95; Escassez
  Hídrica 142 (R$/MWh). **Referência de auditoria.**
- **Decisão (projeto):** criar tabela `bandeira_tarifaria`
  (competência, bandeira, R$/MWh, R$/kWh, início/fim vigência, fonte) e o
  serviço consulta por competência; competências **anteriores a jan/2015 →
  adicional 0** (o `IFERROR(...,0)` da planilha).

## 15. Tributos (decisão do projeto)
- **Fórmula oficial adotada (aditiva):**
  `tarifa_com_tributos = tarifa / (1 − PIS − COFINS − ICMS)`, + CIP/COSIP.
- **Inconsistência do XLSM (registrar):** `Fatura-1` usa multiplicativa
  (`/((1−PIS−COFINS)×(1−ICMS))`, célula K18); `Fatura-2` usa aditiva
  (`/(1−PIS−COFINS−ICMS)`, célula K18). O próprio arquivo diverge.
  O motor usa **apenas a oficial aditiva** (não manter as duas).
- MVP: base **líquida por padrão** (dados ANEEL são líquidos); tributos como
  camada opcional — confirmado.

## 16. CIP/COSIP
Valor fixo mensal (R$) adicionado à fatura (linha C38/X38). No XLSM é entrada
manual (`Painel Inicial H7`).

## 17. Outros valores
Doações/taxas/serviços — valor fixo (R$), linha C39/X39 (entrada `L20`).

## 18. Elegibilidade (modalidades disponíveis)
- Azul: todos os subgrupos A (obrigatória A1–A3); Verde: A3a/A4/AS
  (REN 1.000/2021).
- `IFERROR(total, "…não disponibilizado pela distribuidora")` quando a
  distribuidora não publica a modalidade.
- Funções no core: `modalidades_elegiveis` e `motivo_indisponibilidade`.

## 19. Cálculo das modalidades
- **Verde:** demanda única (`máx(medida_única, contratada_única)`) +
  consumo P/FP + TE P/FP.
- **Azul:** demanda P + demanda FP (cada uma `máx(medida, contratada)`) +
  consumo P/FP + TE P/FP.
- (futuro) Monômia: consumo P+INT+FP sem demanda; Branca: 3 postos.

## 20. Comparação
Aba Fatura-1 bloco E46:J55: tabela comparativa por modalidade (TUSD demanda,
TUSD energia, TE, ultrapassagem, reativos, bandeira, CIP, outros) e o **Valor
da Fatura (R$)**. Sistema expõe `POST /api/calculo/comparar` que ranqueia as
modalidades elegíveis por menor `custo_total` e lista as indisponíveis com
motivo (ex.: Verde fora de A3a/A4/AS).

## 21. Regras históricas
- **Horo-sazonal pré-2014/2021:** seca (mai–nov) × úmida (dez–abr) — já
  mapeada no service.
- **Bandeiras** só a partir de jan/2015; antes → 0.
- **Limite de Grupo B:** 112,5 kVA — constante de enquadramento (não
  regulatória no mesmo sentido atual).

## 22. Divergências XLSM × regulamentação
| Tema | XLSM | Regulamentação | Decisão |
|---|---|---|---|
| Ultrapassagem | sem tolerância, excedente integral | 5% de tolerância, excedente acima | **oficial (5%)** |
| Tributos | Fatura-1 multiplicativa / Fatura-2 aditiva | aditiva | **oficial aditiva** |
| Piso demanda 30 kW | se não informado | não previsto | a decidir |
| Limite coop. 1125 kVA | `IF(coop="Sim",1125,112.5)` | provável erro (112,5) | não reproduzir |
| Reativo proxy B1 Residencial | XLSM | sem tarifa própria no dataset | alinhar proxy |

## 23. GAP XLSM × sistema atual
| Regra | XLSM | Sistema atual | Gap |
|---|---|---|---|
| Busca de tarifa | VBA igualdade+ocorrência | SQL com vigência `BETWEEN` | ✅ superior |
| Fallback seca/úmida | fórmulas IFERROR | service `_posto_sazonal_de` | ✅ |
| Filtro `detalhe` | igualdade | filtro `detalhe` padrão | ✅ |
| Demanda faturável | máx + piso 30 | máx(contratada,medida) | ⚠️ falta piso + LARGE |
| Consumo rateio %mês | `cons × %mês` | consumo direto | ❌ |
| Ultrapassagem | sem tolerância | `[PAM−PAC×1.05]×2` | ✅ (oficial já) |
| Tributos | inconsistente | base líquida + opcional | ⚠️ padronizar oficial |
| Reativos | proxy B1 Conv. Resid. | proxy TUSD perfil | ⚠️ alinhar |
| Bandeiras | VLOOKUP histórico | entrada manual | ❌ falta tabela |
| Elegibilidade | 300 kW / 112,5 kVA | não existe | ❌ |
| Comparação 5 modalidades | tabela E46:J55 | não existe | ❌ |
| Grupo B | Monômia/Branca | não existe | ❌ sprint futura |

## 24. Backlog
**Concluído (Sprint Grupo A na API):**
1. ✅ Demanda faturável (máx contratada/medida) + demanda única da Verde.
2. ✅ Consumo com rateio `%mês`.
3. ✅ Ultrapassagem (gatilho 5%, excedente total `PAM−PAC`, 2×) — decisão BD.
4. ✅ Tabela `bandeira_tarifaria` + lookup por competência (antes 2015 → 0).
5. ✅ Elegibilidade (`modalidades_elegiveis` + `motivo_indisponibilidade`).
6. ✅ Comparação/ranqueamento via `POST /api/calculo/comparar`.
7. ✅ Tributos opcionais (aditiva "dentro" + multiplicativa "fora").
8. ⏭️ Reativos proxy B1 — refinamento não bloqueador.

**Próximas frentes (a priorizar):**
- Grupo B (Monômia + Branca, mínimo faturável, custo de disponibilidade).
- Validação numérica Caso 1 (depende de Excel com macro).
- SCEE, Tarifa Social, ACR×ACL/EPI.

## 25. Critérios de aceite
1. `POST /api/calculo/comparar` ranqueia disponíveis por menor custo e lista
   indisponíveis com motivo.
2. Tributos propagados a todas as modalidades da comparação.
3. Determinístico; suíte verde (unitário + integração).

## 26. Casos de teste
| Caso | Entrada | Esperado |
|---|---|---|
| 1 | Amazonas Energia, A4, Verde, REH 1.077, nov–dez/2010 | total = XLSM (recálculo) |
| 2 | CPFL JAGUARI, A2, Azul, 2010-06 | TE = Ponta seca/Fora ponta seca |
| 3 | idem, 2011-01 | TE = Ponta úmida/Fora ponta úmida |
| 4 | demanda > contratada+5% | `[PAM−PAC]×2×tarifa` |
| 5 | data ≥ 2015 | bandeira do histórico |
| 6 | (futuro) B1 Branca 3 postos | sprint Grupo B |

## Rastreabilidade
- VBA: `Módulo1` — `BuscarTarifaMelhorado` (linhas 534–601),
  `BuscarTarifa` (472–533), `Confirmar1/2/3`, `Botao1/2`, `FiltrarTarifasOficial`.
- Fórmulas: `Fatura-1` C18:L39 (Verde), N18:X39 (Azul), Z18:BE39 (B), E46:J55
  (comparação); `Painel Inicial` validações.
- Bandeiras: `valores Bandeira Tarifária` Tabela11 + histórico J:O.
- Fonte ANEEL: dadosabertos.aneel.gov.br (bandeiras) e REN 1.000/2021.
