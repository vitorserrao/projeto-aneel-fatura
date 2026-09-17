# Ambientes de Comercialização e Tarifas (aula IFSC — RTE)

> **Fonte:** `RTE_aula_12_Ambientes de Comercialização e Tarifas.pdf` — Prof. Pedro César
> Cordeiro Vieira (IFSC, Campus Florianópolis, 2025), disciplina *Regulação Técnica e
> Econômica*. Material didático do próprio IFSC (não é documento normativo, mas cita e
> organiza a regulação).
> **Hierarquia:** material **didático** (nível 3–4) — útil para entendimento e para
> referenciar; as regras devem ser confirmadas nas fontes oficiais citadas.

## 1. Ambientes de comercialização (ACR × ACL) *(pág. 3)*

O novo modelo do Setor Elétrico Brasileiro (SEB) instituiu **dois ambientes** de
comercialização — **Decreto nº 5.163/2004**:

| Ambiente | Quem participa | Como se contrata |
|---|---|---|
| **ACR** — Ambiente de Contratação Regulada | Distribuidoras (consumidores cativos) | Contratos resultantes de **leilões** |
| **ACL** — Ambiente de Contratação Livre | Consumidores livres e especiais, comercializadores e varejistas | Contratos **livremente negociados** |

**Vendedores** nos dois ambientes: geradores de serviço público, produtores
independentes, comercializadores e autoprodutores. *(pág. 3)*

## 2. Requisitos para migrar ao ACL *(págs. 4–5)*

- **Consumidor Livre:** demanda ≥ **0,5 MW** (a partir de janeiro/2023); qualquer fonte.
- **Consumidor Especial:** demanda entre **0,5 MW e 1,0 MW**; exige **fontes incentivadas**
  (PCH, eólica, solar, biomassa).
- **Portaria MME 465/2019:** previu redução do requisito para 0,5 MW até jan/2023 e
  abertura total nos anos seguintes.

### Abertura do Mercado Livre (cronograma) *(pág. 5)*
| Etapa | Data | Quem entra |
|---|---|---|
| 1ª | janeiro/2024 | **Todos os consumidores do Grupo A** (A1, A2, A3, A3a, A4, AS) |
| 2ª | janeiro/2026 | Parte do Grupo B (B3 demais empresas, B4 iluminação pública) |
| 3ª | janeiro/2028 | Demais consumidores do Grupo B (B1 residencial e baixa renda, B2 rural) |

## 3. ACR × ACL — quem paga o quê *(pág. 6)*

```
Consumidor CATIVO:  paga Tarifa Regulada (TE + TUSD) à distribuidora
Consumidor LIVRE:   paga o Preço Livremente Negociado (energia) ao gerador/comercializador
                    + Uso da Rede (TUSD) à distribuidora
```
Ponto-chave: **mesmo no ACL, o consumidor continua pagando o uso da rede** (fio).

## 4. PRORET *(págs. 7–8)*

- Aprovado pela **Resolução Normativa nº 435/2011**; organizado em **12 módulos**,
  subdivididos em submódulos.
- **Caráter normativo**: consolida a regulamentação dos processos tarifários.
- Disponível em: gov.br/aneel → Procedimentos de Regulação Tarifária (PRORET).

## 5. Tarifa de fornecimento *(págs. 9–15)*

- **Tarifa de Fornecimento (TF) = TE + TUSD** *(pág. 55; fonte: PRORET 7.1)*.
- Estabelecida pela ANEEL; assegura ao consumidor valor justo e à concessionária o
  equilíbrio econômico-financeiro *(pág. 10)*.
- Dois componentes: **energia (R$/kWh)** e **demanda (R$/kW)** — nem todos os
  consumidores pagam demanda *(pág. 10)*.
- Objetivos do valor da tarifa *(pág. 11)*: valor justo; cobrir custos com qualidade;
  remunerar investimentos prudentes; estimular eficiência; atendimento sem distinção.

## 6. Composição da Receita Requerida *(págs. 16–19)*

### Parcela A — custos não gerenciáveis (repassados)
- **Compra de energia:** Cota de Itaipu Binacional; Cota de Angra 1 e 2; Cota de
  Concessões Renovadas (Garantia Física); Cota do PROINFA; Contratos Bilaterais;
  Geração Distribuída; Leilões; Geração Própria.
- **Encargos setoriais:** CDE, RGR, TFSEE, PROINFA, ONS, ESS, P&D+EE, EER, CFURH.
- **Transporte de energia:** Rede Básica; Transporte de Itaipu; Conexão.

*(págs. 17–18)*

### Parcela B — custos gerenciáveis (págs. 19)
- **Custos operacionais** — operação, manutenção, tarefas comerciais/administrativas
  (leitura, entrega de faturas, vistoria, podas, operação de subestações); definidos por
  **benchmarking**.
- **Remuneração do capital** — rentabilidade do negócio (custo de oportunidade).
- **Cota de depreciação** — recomposição do capital (taxa de depreciação × Base de
  Remuneração Regulatória).
- **Receitas irrecuperáveis** — parcela de baixa expectativa de arrecadação (inadimplência).

### Comparação com a cartilha oficial
A cartilha "Por Dentro da Conta de Luz" (2013) apresenta a mesma divisão Parcela A/B —
consistente. *(ver `cartilha_2013_reajuste_revisao.md`)*

## 7. Reajuste, revisão e Fator X *(págs. 21–27)*
O material cita os mecanismos (revisão e reajuste tarifário) e o **Fator X**, sem
detalhar as fórmulas — que já estão documentadas em
[`cartilha_2013_reajuste_revisao.md`](../cartilha_2013_reajuste_revisao.md).

## 8. Classificação dos consumidores *(págs. 31–33; REN 1.000/2021, art. 23)*

### Por nível de tensão (critério de enquadramento)
| Nível de tensão | Carga instalada | Demanda contratada |
|---|---|---|
| Secundária em rede aérea | ≤ 75 kW | Não se aplica |
| Secundária em sistema subterrâneo | Conforme padrão da distribuidora | — |
| Primária < 69 kV | ≥ 75 kW | ≤ 2.500 kW |
| Primária ≥ 69 kV | Indiferente | ≥ 2.500 kW |

### Grupo A (tensão ≥ 2,3 kV ou subterrâneo) — tarifa binômia
- A1 ≥ 230 kV; A2 88–138 kV; A3 69 kV; A3a 30–44 kV; A4 2,3–25 kV; AS < 2,3 kV subterrâneo.

### Grupo B (tensão < 2,3 kV) — tarifa monômia
- B1 residencial; B2 rural; B3 demais classes; B4 iluminação pública.

## 9. Sistema tarifário do mercado cativo *(pág. 34; REN 1.000/2021)*

| Grupo | Modalidade | Disponibilidade |
|---|---|---|
| A (alta tensão) | **Azul** (horária) | Obrigatória A1, A2, A3; opcional A3a, A4, AS |
| A | **Verde** (horária) | Opcional A3a, A4 e AS |
| B (baixa tensão) | **Convencional Monômia** | B1, B2, B3, B4 |
| B | **Branca** | Opcional B1, B2, B3 |

**Tarifa Monômia:** só consumo (R$/kWh) — Grupo B e Grupo A com transformação ≤ 112,5 kVA (por opção).
**Tarifa Binômia:** consumo (R$/kWh) + demanda (R$/kW) — Grupo A. *(pág. 30)*

## 10. Tarifa Social de Baixa Renda *(pág. 35)*
- Público: famílias no Cadastro Único, BPC, ou renda até 3 salários mínimos com uso
  continuado de equipamentos.
- **Desconto por faixa de consumo (PCM):** ≤30 kWh → 65%; 30–100 kWh → 40%;
  100–220 kWh → 10%.
- Famílias indígenas/quilombolas: desconto de **100% até 50 kWh/mês**.

## 11. Mínimo faturável do Grupo B *(pág. 36)*
- Monofásico: **30 kWh**; Bifásico: **50 kWh**; Trifásico: **100 kWh** (mesmo sem consumo).

## 12. Postos tarifários *(págs. 39–41, 43)*
- **Ponta:** 3 horas consecutivas (definidas pela distribuidora, aprovadas pela ANEEL),
  exceto sábados, domingos e feriados nacionais.
- **Intermediário:** 2 horas (1 antes + 1 depois da ponta) — **Grupo B (Branca)**.
- **Fora de ponta:** horas complementares.
- Exemplo CELESC (grupo A, SC): ponta das **18h30 às 21h30**. Grupo B (Branca): 18h30–21h29.
- Branca: nos fins de semana e feriados, o valor é **sempre fora de ponta**.

## 13. Fórmulas de cálculo das modalidades *(págs. 44–47)*

### Horária Verde
```
Valor pago pelo consumo = (Tarifa consumo ponta × Consumo medido ponta)
                        + (Tarifa consumo fora ponta × Consumo medido fora ponta)
Valor pago pela demanda = Tarifa de demanda (única) × Demanda faturável
Demanda faturável = máx(Demanda medida ; Demanda contratada)
```

### Horária Azul
```
Valor pago pelo consumo = (Tarifa consumo ponta × Consumo ponta)
                        + (Tarifa consumo fora ponta × Consumo fora ponta)
Valor pago pela demanda = (Tarifa demanda ponta × Demanda faturável ponta)
                        + (Tarifa demanda fora ponta × Demanda faturável fora ponta)
Demanda faturável = máx(Demanda medida ; Demanda contratada)
```

### Tarifa de Ultrapassagem *(pág. 47)*
- Aplica-se às tarifas binômias **Azul e Verde**.
- Aplica-se quando a demanda medida excede a contratada em **5%**.
- A tarifa de ultrapassagem equivale a **2× o valor da tarifa de demanda**.
```
D_ultrapassagem = 2 × VR × (PAM − PAC)
  VR  = tarifa de demanda da modalidade (R$/kW)
  PAM = demanda medida (kW)
  PAC = demanda contratada (kW)
```
**Confirma a regra da REN 1.000/2021** registrada em
[`ren1000_2021_faturamento.md`](ren1000_2021_faturamento.md).

## 14. Tributos e cálculo da tarifa final *(págs. 51–54)*

- Tributos na fatura: **ICMS** (estadual), **PIS** e **COFINS** (federais),
  **COSIP** (municipal — em Florianópolis, valor fixo).
- **Fórmula da tarifa com tributos (material IFSC):**
```
Tarifa Final = Tarifa Homologada / [ (1 − (PIS + COFINS)/100) × (1 − ICMS/100) ]
```
- **Exemplo (págs. 52–53):** consumidor residencial, 220 kWh (nov/2020):
  - Tarifa homologada B1 = 0,50599 R$/kWh; PIS 0,97%; COFINS 4,46%;
    ICMS 12% até 150 kWh e 25% acima.
  - Até 150 kWh → **0,608 R$/kWh**; após 150 kWh → **0,713 R$/kWh**.
  - Fatura = 0,608 × 150 + 0,713 × 70 = **R$ 141,138**.
- ⚠️ **Observação importante sobre conflito de fórmulas:** este material usa a forma
  **multiplicativa** `(1 − PIS+COFINS) × (1 − ICMS)` — a mesma do projeto anterior (Kevin
  Wu) — enquanto a fonte MME/ANEEL consultada usa a forma **aditiva**
  `(1 − PIS − COFINS − ICMS)`. **Registrar a divergência** (ver seção de conflitos).
- **COSIP** (Florianópolis, LC nº 109/2002): reajustado junto com as tarifas da CELESC.

## 15. Excedente reativo *(pág. 56)*
- Consumidores do Grupo A (inclusive optante B) são cobrados por excedente de demanda
  e energia reativa quando o **fator de potência < 0,92** (indutivo ou capacitivo).
- Cobrança diferenciada por posto (ponta/fora ponta), conforme a modalidade (azul/verde).
- **6 horas consecutivas** (a critério da distribuidora) para excedente **capacitivo**
  (ex.: 0h–6h); demais horas para excedente **indutivo** (6h–24h).
- Excedente de **energia**: tarifa do B1 bandeira verde.
- Excedente de **demanda**: tarifa de demanda azul fora de ponta.

## 16. Bandeiras tarifárias *(págs. 57–59; REN 479/2012)*
Criadas em 2015 para sinalizar o custo de geração (valores atualizados em fev/2022):

| Bandeira | Condição | Acréscimo (por kWh, sem tributos) |
|---|---|---|
| Verde | Favorável | R$ 0,00 |
| Amarela | Menos favorável | R$ 0,01874 |
| Vermelha — Patamar 1 | Mais custosa | R$ 0,03971 |
| Vermelha — Patamar 2 | Mais custosa | R$ 0,09492 |
| Escassez hídrica (a partir de 2021) | Severa | R$ 0,1420 |

- As distribuidoras divulgam a bandeira do subsistema de sua região.
- Acionamento relacionado ao **GSF (Fator de Redução do MRE)**.

## 17. Exemplo de tarifa para consumidor industrial *(págs. 61–62)*
O material apresenta exemplos aplicados (sem fórmula nova além das já registradas).

## 18. Exercício proposto na aula *(pág. 63)*
- Grupo B: planilha de cálculo comparando **Convencional × Branca**.
- Grupo A: planilha de cálculo e análise de **viabilidade de migração para o ACL**
  (custos, economias).
- Referência ao GESE: **"Preço de indiferença, ferramenta para análise"** —
  https://gese.florianopolis.ifsc.edu.br/produções/
  → **pista metodológica para o EPI** (que não tem fonte oficial).

## 19. Referências citadas pelo material *(pág. 65)*
- PRORET; REN 414/2010; REN 479/2012; PROCEL (Manual de Tarifação, 2011);
  ANEEL "Por Dentro da Conta de Luz" (7ª ed., 2016); ANEEL "Entendendo a Tarifa";
  ANEEL "Bandeiras Tarifárias"; ANEEL "Cálculo Tarifário e Metodologias";
  CELESC "Tudo sobre a Tarifa Branca" (2020); Comerc 2023.

## Uso futuro no projeto
- **Motor ACR:** fórmulas de consumo/demanda das modalidades Azul e Verde (item 13);
  ultrapassagem (item 13); reativos (item 15); bandeiras (item 16).
- **Otimização:** elegibilidade por subgrupo (item 9).
- **Comparação ACR × ACL:** conceito de ambientes, quem paga o quê e o cronograma de
  abertura do mercado (itens 1–3) — base para a discussão de migração.
- **EPI:** pista do GESE ("preço de indiferença") para a metodologia (item 18).
- **Validação:** exemplo numérico de tarifa com tributos (item 14) — caso de teste.
