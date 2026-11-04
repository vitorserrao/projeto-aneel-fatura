# Desenho — Decisão ACR × ACL com Preço de Indiferença Probabilístico

> Status: **proposta para discussão** (não implementado).
> Este documento define o *módulo de decisão sob incerteza* do projeto: dado um
> perfil de consumo, comparar o custo no ACR (mercado cativo, motor já
> validado) com o custo no ACL (mercado livre, dados CCEE) e responder **não
> só "quanto economiza", mas "qual a probabilidade dessa economia se
> materializar"** — incorporando a evolução futura de preços dos dois mercados,
> bandeiras, encargos e incerteza de consumo.
>
> Regra do projeto preservada: nada aqui cria regra tarifária. O EPI é um
> **modelo de decisão** (metodologia de mercado), não uma regra da ANEEL; todas
> as premissas metodológicas ficam registradas e revisáveis (ver "Decisões em
> aberto").

## 1. Motivação (a pergunta que o módulo responde)

O EPI determinístico responde: *"qual o preço máximo de energia no ACL que
empata com a minha fatura ACR?"* Se o preço negociado estiver abaixo do EPI,
a economia pontual é, por exemplo, **R$ 3.000/mês**.

Mas isso supõe futuro congelado. As perguntas reais são:

1. Qual a probabilidade de a economia projetada **se realizar** (`P(economia > 0)`)?
2. Qual a probabilidade de atingir **a meta** (`P(economia ≥ R$ 3.000)`)?
3. Quanto se perde nos cenários ruins (P10, VaR/CVaR)?
4. Em quanto tempo o investimento de migração **se paga**, com que chance?
5. Vale mais migrar **agora ou esperar** 12 meses?
6. Qual fator mais move o resultado (sensibilidade)?

## 2. Arquitetura em camadas

```
+-----------------------------------------------------------------------+
|  CAMADA 1 — Determinística (existente + a fechar)                     |
|  Fatura_ACR = motor_calculo (REN 1.000/2021, validado em faturas reais)|
|  Custo_ACL  = E × (P_acl + FioB + Encargos_CCEE) + Tributos           |
|  EPI        = preço P* tal que Custo_ACL(P*) = Fatura_ACR             |
+-----------------------------------------------------------------------+
|  CAMADA 2 — Incerteza (distribuições das variáveis de entrada)        |
|  P_acl(t), TE/TUSD(t), Bandeiras(t), Encargos(t), Consumo(t)          |
+-----------------------------------------------------------------------+
|  CAMADA 3 — Simulação (Monte Carlo correlacionado, horizonte 12–60 m) |
|  Cenários conjuntos; correlação hidrologia → PLD ↑ e bandeira ↑       |
+-----------------------------------------------------------------------+
|  CAMADA 4 — Decisão (métricas probabilísticas + sensibilidade)        |
|  P(econ>0), P10/P50/P90, VaR/CVaR, payback, agora × esperar           |
+-----------------------------------------------------------------------+
```

### 2.1 Camada 1 — fórmulas propostas (a validar, pendência P2)

Custo no ACL de um consumidor com energia medida `E` (MWh/mês), posto
único (consumidor livre não paga demanda à distribuidora — **premissa a
confirmar para o perfil elegível**):

```
Custo_ACL(P) = E × P        ... energia (contrato ou exposição ao PLD)
             + E × FioB      ... TUSD Fio B (uso da rede, pago à distribuidora)
             + Encargos      ... encargos setoriais/CCEE repassáveis
             + Tributos      ... PIS/COFINS/ICMS sobre as parcelas aplicáveis
```

EPI (preço de indiferença, em R$/MWh):

```
EPI = [ Fatura_ACR − E × FioB − Encargos_ACL − Tributos_não_energéticos ]
      / [ E × (1 + τ_energia) ]
```

onde `τ_energia` é a alíquota combinada dos tributos sobre a parcela de
energia (forma oficial aditiva: `Tarifa / (1 − PIS − COFINS − ICMS)`; a
forma multiplicativa do projeto anterior foi **descartada** por conflito com
a fonte oficial — ver base de conhecimento `regras/ren1000_2021_faturamento.md`).

Observações metodológicas (a registrar como premissas):

- A `Fatura_ACR` já inclui bandeira e reativos; no ACL **não há bandeira** —
  a escassez já está embutida no PLD. O EPI captura isso naturalmente.
- `FioB` é o gargalo de dado: o CSV da ANEEL só traz TUSD total
  (`VlrTUSD`), sem o split Fio A/Fio B. **Decisão em aberto** (ver §7).
- O preço do ACL é **negociado** (a CCEE publica médias, não contratos
  individuais). O EPI é um **limiar de referência**, não uma cotação.

### 2.2 Camada 2 — variáveis estocásticas e fontes

| # | Variável | Distribuição/modelo | Fonte de dados |
|---|---|---|---|
| 1 | `P_acl(t)` | Percentis históricos do PLD, bootstrap em blocos, ou quantis previstos por ML (quantile regression/forests) | CCEE `pld_horario`/`pld_media_mensal` (2001–2026); features: `custo_variavel_unitario_*`, `mre_*`, `garantia_fisica_*`, `geracao_horaria_submercado` |
| 2 | Spread contrato×PLD | Distribuição empírica do prêmio/desconto do contrato sobre o PLD | CCEE `rrv_mensal` ÷ montantes de `contrato_montante_*` (preço médio implícito) |
| 3 | `TE/TUSD(t)` no ACR | Projeção com intervalo (ETS/ARIMA/baseline) + reajustes | CSV ANEEL `fcf2906c-….csv` (2010–2026, por distribuidora/posto) |
| 4 | `Bandeiras(t)` | Estados discretos com probabilidades condicionais à hidrologia | CCEE `credito_debito_ccrbt` + histórico de bandeiras |
| 5 | `Encargos(t)` | Séries históricas + cenários | CCEE `recursos_financeiros_conta_setorial` (CDE/CCC/RGR) |
| 6 | `Consumo(t)` | Perfil horário/sazonal do ramo | CCEE `consumo_horario_perfil_agente`, `consumo_ramo_atividade` |
| 7 | `FioB` | Determinístico (ou faixa) — premissa documentada | ANEEL (REH) ou fonte a definir (§7) |

### 2.3 Camada 3 — Monte Carlo correlacionado

- **N ≈ 10.000 iterações**, passo mensal, horizontes `H ∈ {12, 24, 36, 60}` meses.
- **Correlação é obrigatória**: hidrologia ruim → PLD alto **e** bandeira
  vermelha **e** pressão sobre reajustes. Sem isso, o risco é subestimado.
  Métodos propostos (em ordem de preferência):
  1. **Bootstrap em blocos do histórico conjunto** (reamostrar o mês inteiro
     preserva a correlação contemporânea — simples e defensável);
  2. Cópulas gaussianas/t sobre os resíduos das séries;
  3. Modelo estrutural: fator hidrológico latente (ENA/GSF proxy) dirigindo
     PLD + bandeiras.
- Cada iteração produz `economia_i(t) = Fatura_ACR_i(t) − Custo_ACL_i(t)` e o
  **VPL** da migração com taxa de desconto definida pelo usuário.

### 2.4 Camada 4 — métricas de decisão

```
P(economia > 0)          = média das iterações com economia positiva
P(economia ≥ meta)       = meta definida pelo usuário (ex.: R$ 3.000/mês)
P10 / P50 / P90          = percentis da economia média no horizonte
VaR_5% / CVaR_5%         = perda nos 5% piores cenários
Payback                  = distribuição do tempo até VPL acumulado > 0
Agora × Esperar          = compara E[VPL(migrar agora)] vs E[VPL(esperar 12 m)]
Sensibilidade (tornado)  = variação do P50 ao chocar cada variável ±1σ
```

### 2.5 Camada ML (diferencial acadêmico, com baseline honesto)

- **Baseline estatístico primeiro** (`forecast/baseline.py` — o esqueleto já
  exige isso): bootstrap/percentis do histórico. É a régua para mostrar se o
  ML agrega.
- **ML**: previsão probabilística do PLD por quantile regression / quantile
  forests (LightGBM), features exógenas: CVU conjuntural/estrutural,
  MRE/GSF, geração por fonte e submercado, calendário. Saída: quantis 10/50/90
  mensais → alimentam a Camada 2.
- **Backtest walk-forward**: treinar até `t`, prever `t+1..t+H`, comparar com
  o realizado; métricas: PIT (cobertura dos quantis), CRPS, comparação contra
  o baseline. Janela sugerida: 2018–2024, reestimando a cada 3–6 meses.
- **Clusterização (opcional, P7)**: k-means sobre `consumo_ramo_atividade`/
  `consumo_horario_perfil_agente` para oferecer perfis típicos no dashboard.

## 3. Exemplo ilustrativo (números fictícios, só para fixar o conceito)

Consumidor com 10.000 kWh/mês; fatura ACR = R$ 8.000; preço ACL atual =
R$ 312,40/MWh → economia pontual = **R$ 3.000/mês**.

Após 10.000 simulações (horizonte 36 meses):

```
P(economia > 0)        = 87%
P(economia ≥ 3.000)    = 41%
P10 / P50 / P90        = −R$ 500 / R$ 2.800 / R$ 6.200 por mês
VaR_5%                 = −R$ 700/mês
Payback P50            = 14 meses
```

Leitura para o TCC: *"o caso base aponta R$ 3.000/mês, mas há 13% de chance
de resultado negativo nos cenários extremos de preço; a decisão depende da
aversão a risco do consumidor."*

## 4. Ingestão de dados (produto P1)

- Portal CKAN 2.10: `GET /api/3/action/package_show?id=<dataset>` → resources
  CSV anuais em `pda-download.ccee.org.br` (licença CC-BY-4.0).
- Primeiro lote (8 datasets): `pld_horario`, `pld_media_mensal`,
  `custo_variavel_unitario_conjuntural`, `custo_variavel_unitario_estrutural`,
  `credito_debito_ccrbt`, `recursos_financeiros_conta_setorial`,
  `consumo_mensal_ambiente_comercializacao`, `rrv_mensal`,
  `contrato_montante_mensal_tipo`.
- Onde ficam: `infra/` (ingestão), `data/raw/` (cache), `core/` **nunca**
  depende de infra. A API da CCEE é bloqueada por WAF para alguns IPs —
  no ambiente do usuário o acesso funciona; prever fallback de CSV manual.
- O TUSD **Fio B não existe na CCEE** (é ANEEL) — fora deste lote.

## 5. Roteiro e dependências

```
P1 (ingestão CCEE) ──► P2 (preço real ACL no lugar do 312,4 fixo)
        │                    └─► P3 (EPI determinístico — precisa Fio B)
        └─► P4 (validação bandeiras via CCRBT) ──► P6 (projeção ACR)
P2 + P3 + P6 ──► P5 (EPI probabilístico + ML) ──► P7 (dashboard de decisão)
P1 ──► P8 (análise de migração ACR→ACL — pode ser a qualquer momento)
```

- **P1+P2**: ~1–2 semanas, sem bloqueador, primeiro resultado visível.
- **P3**: ~2 semanas + decisão do Fio B.
- **P5**: ~3–4 semanas (baseline → ML → métricas).
- **P6**: ~2–3 semanas (ETS/ARIMA + backtest com REHs).
- **P7**: ~2–3 semanas (dashboard + relatório exportável).

## 6. Enquadramento no TCC

- **Contribuição**: *"ferramenta de apoio à decisão de migração ACR→ACL com
  preço de indiferença probabilístico"*.
- **Metodologia**: motor regulatório validado (REN 1.000/2021) + modelo de
  decisão sob incerteza + simulação Monte Carlo correlacionada + previsão
  probabilística com backtest walk-forward.
- **Resultados**: distribuidoras reais (validação já existente em
  `docs/validacao_faturas_reais/`), cenários por submercado, sensibilidade,
  artigo estilo ERIAC.

## 7. Decisões em aberto (para discutir antes de codar)

1. **TUSD Fio B** — resgatar arquivo do projeto anterior, extrair da ANEEL
   por REH, ou proxy temporário documentado?
2. **Horizonte padrão e taxa de desconto** — sugerido: 24 e 60 meses, taxa
   configurável (SELIC/IPCA).
3. **Regra de decisão do painel** — só mostrar métricas, ou sugerir
   "migre/aguarde" com limiar configurável de `P(economia > 0)`?
4. **Escopo do ML** — quantile forests no PLD bastam, ou incluir modelo
   conjunto PLD + bandeiras?
5. **Perfis de consumo** — usar ramos do CCEE (comercial/industrial) ou
   perfis manuais do usuário no MVP?
6. **Submercado padrão** — o consumidor cativo está ligado à distribuidora
   (submercado único); assumir o submercado da distribuidora como padrão?
