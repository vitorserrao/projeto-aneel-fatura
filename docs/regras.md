# Regras — Sprint Comparação Verde × Azul a partir da fatura Verde

Projeto ACR×ACL (PIBITI/GESE-IFSC). Arquitetura em 5 camadas (`core` puro /
`infra` / `services` / `api` / `app`). O `core` não importa infraestrutura
(teste `tests/unit/test_core_independencia.py` garante).

## Objetivo

Simular a modalidade **Azul** a partir de dados de uma fatura **Verde**, com
otimização das demandas contratadas, e devolver um veredito
**Verde / Azul / Inconclusivo**.

Motivação: a abordagem anterior repetia a demanda única da Verde na ponta da
Azul (`Dp = Dfp`), supondo que o pico do consumidor sempre ocorre na ponta e
penalizando a Azul (em um teste a diferença passou de R$ 10 mil).
**Nenhum valor da Verde pode ser copiado para a ponta da Azul.**

## Regras gerais (não negociáveis)

1. **Não inventar fórmula nem valor tarifário.** Tarifas vêm sempre do
   `TarifaRepository` (via `CalculoService.parcelas_vigentes`).
2. **Parâmetros regulatórios ficam em configuração** (`config.py`), nunca
   fixos no código, cada um com comentário `# TODO: confirmar artigo REN 1000/2021`:
   - `DEMANDA_MINIMA_KW = 30`
   - `TOLERANCIA_ULTRAPASSAGEM = 0.05`
   - `FATOR_ULTRAPASSAGEM = 2`
   - `HORAS_PONTA_POR_DIA = 3` (por distribuidora, se o dado existir)
3. **Regra de dados:** sem histórico, analisa só o mês informado; com
   histórico, só os meses existentes. **Dado ausente nunca vira zero** — é
   `None` e tratado explicitamente (o mês é excluído com aviso ou a função
   recusa).
4. **TUSD Energia ponta e fora ponta sempre buscadas separadamente**,
   inclusive na Azul, onde os valores costumam ser iguais. Não presumir
   igualdade no código.
5. A TE é diferenciada por posto nas duas modalidades.
6. Retenções de IRPJ/CSLL/PIS/COFINS (órgãos federais, IN RFB 1.234/2012)
   **não entram na comparação**. A comparação é sempre pelo **valor bruto**
   da fatura.

## Componentes implementados

### `core/otimizador.py` (puro)

- `otimizar_contratada(demandas_medidas, piso, tolerancia, fator) ->
  (dc_otima, custo_em_kw_mes)`

  Custo em unidades de kW·mês (independe da tarifa, que é fator
  multiplicativo):

  ```
  C(Dc) = Σ_m [ max(D_m, Dc) + fator·(D_m − Dc) se D_m > (1+tol)·Dc ]
  ```

  Candidatos: `{piso} ∪ {D_m} ∪ {D_m/(1+tol)}`, filtrando `≥ piso`.
  Empate: vence a menor demanda contratada. Usado separadamente para
  Azul ponta, Azul fora ponta e Verde (demanda única).

- `demanda_verde_mensal(dp, dfp)` — `max(Dp, Dfp)` quando o histórico traz
  os dois postos; com um só posto, usa o existente; sem nenhum, recusa.
- `faixa_demanda_ponta(Ep_kwh, horas_ponta, D_verde, piso) -> (min, max)` —
  `min = max(Ep/horas_ponta, piso)`; `max = D_verde`.
- `horas_ponta(data_leitura_anterior, data_leitura_atual, feriados,
  horas_por_dia)` — dias úteis no intervalo `(anterior, atual]` (os dias
  efetivamente faturados no ciclo), sem sábados/domingos e feriados
  nacionais, × horas por dia. Feriados são passados por parâmetro.

### `core/motor_calculo.py`

`fatura_verde(...)` e `fatura_azul(...)` mensais, puras, devolvendo
`FaturaMensal` **por componente** (`tusd_demanda`,
`tusd_demanda_ponta/fora_ponta`, `tusd_energia_ponta/fora_ponta`,
`te_energia_ponta/fora_ponta`, `ultrapassagem`, `reativos`, `bandeira`).

- Verde: TUSD demanda única × demanda faturada (`max(medida, contratada)`)
  + ultrapassagem; TUSD energia P/FP × kWh P/FP; TE P/FP × kWh P/FP.
- Azul: TUSD demanda ponta e fora ponta, cada uma com sua contratada e
  ultrapassagem; TUSD energia P/FP; TE P/FP.
- **Demanda faturada — Súmula 391 do STJ** (implementada em
  `fatura_verde`/`fatura_azul`, ativada por
  `config.ICMS_DEMANDA_NAO_UTILIZADA = False`):
  - faturada = `max(medida, contratada)`;
  - utilizada = `medida` (limitada à faturada) → PIS/COFINS + ICMS;
  - não utilizada = `faturada − medida` (só existe se
    `medida < contratada`) → só PIS/COFINS, sem ICMS.
  Na Azul a regra é aplicada **por posto** (ponta e fora ponta). A
  **ultrapassagem é uma parcela separada** e não entra nessa divisão.
- Ultrapassagem: gatilho `medida > contratada × (1+tol)`; base = excedente
  total `(medida − contratada)`; tarifa = `fator × tarifa de demanda`
  (mesma interpretação do `calcular_fatura`).
- **Ultrapassagem × ICMS:** as faturas reais validadas até aqui (Copel 04/2023
  e CEMIG CII_112 12/2023) **não trazem ultrapassagem**; a única referência
  validada no projeto (artigo ERIAC/CPFL) tributa a ultrapassagem com
  PIS/COFINS/ICMS cheio. `fatura_verde`/`fatura_azul` mantêm esse tratamento
  (fator cheio) e a pendência de validar contra uma fatura real com
  ultrapassagem fica registrada.
- Tributos por dentro (valor bruto): `1/((1−PIS−COFINS)×(1−ICMS))` no
  padrão `tipo_icms="fora"`; `1/(1−PIS−COFINS−ICMS)` no `"dentro"`.
- Reativo excedente e bandeira entram como valores finais (R$) e são
  **iguais nas duas modalidades** — cancelam na comparação.

### `services/comparacao_verde_azul.py`

**Nível 1 — com histórico** (`dp` e `dfp` medidos em todos os meses):

1. Otimiza `Dc_p` (série Dp), `Dc_fp` (série Dfp) e `Dc_verde`
   (série `max(Dp, Dfp)`).
2. Calcula Verde atual (contratada informada), Verde otimizada e Azul
   otimizada.
3. Resultado exato: `Δ = Verde atual − Azul`; `Δ > 0 → AZUL`,
   `Δ < 0 → VERDE`, `Δ = 0 → INCONCLUSIVO`.

**Nível 2 — sem histórico de ponta** (só a demanda única da Verde):

1. `Dfp = D_verde` (limite superior; conservador para a Azul).
2. Faixa de `Dp` por mês com `faixa_demanda_ponta`.
3. Simula a Azul duas vezes, com `Dc_p` reotimizada em cada uma:
   - **Azul mínima:** `Dp` = mínimo da faixa em todos os meses.
   - **Azul máxima:** `Dp` = máximo da faixa em todos os meses.
4. Veredito:
   - `Verde atual < Azul mínima` → `VERDE`
   - `Verde atual > Azul máxima` → `AZUL`
   - caso contrário → `INCONCLUSIVO`, com `dp_equilibrio` por bisseção
     (custo da Azul é monotônico não decrescente em `Dp`).
5. **Nunca** usar o valor do meio da faixa para decidir. Estimativa
   central, se existir, é só informativa e marcada como estimativa.

Saída (`ResultadoComparacaoVerdeAzul`): `nivel`, `veredito`,
`verde_atual`, `verde_otimizada`, `azul` (valor no nível 1;
`{min, max}` no nível 2), `dc_otimas {p, fp, verde}` (no nível 2, `p` é
`{min, max}`), `dp_equilibrio` (opcional), `meses_analisados`, `avisos`.

### `api/`

`POST /api/comparacao/verde-azul` — recebe distribuidora, subgrupo, classe,
detalhe, data de referência (fallback), tributos (`pis`, `cofins`, `icms`,
`tipo_icms`), contratada atual e a lista de meses (`data_referencia`,
`data_leitura_anterior`, `data_leitura_atual`, `dp`, `dfp` opcionais,
`d_verde`, `ep_kwh`, `efp_kwh`, campos `reativo_*` opcionais).

## Parâmetros regulatórios pendentes de confirmação

Todos em `config.py` com `# TODO: confirmar artigo REN 1000/2021`:

- `DEMANDA_MINIMA_KW = 30`
- `TOLERANCIA_ULTRAPASSAGEM = 0.05`
- `FATOR_ULTRAPASSAGEM = 2`
- `HORAS_PONTA_POR_DIA = 3`

Pendências acessórias registradas:

- Feriados de posto tarifário em `config.FERIADOS_POSTO_TARIFARIO`
  (`fixos`, `carnaval`, `paixao_de_cristo`, `corpus_christi`), calculados por
  `core/calendario.py` (Páscoa por Meeus/Jones/Butcher). O 20/11 (Consciência
  Negra) é item configurável desligado por padrão
  (`config.INCLUIR_CONSCIENCIA_NEGRA = False`).
- Feriados estaduais e municipais continuam fora da contagem de dias úteis.
- Horas de ponta por distribuidora: usa-se o padrão de 3 h/dia
  (`HORAS_PONTA_POR_DIA`) até o dado por distribuidora existir.
- No nível 2 sem datas de leitura, usa-se como fallback o mês-calendário da
  data de referência (com aviso).
- O ciclo de leitura pode atravessar a virada do ano: os feriados são
  calculados para cada ano coberto pelo ciclo.

## Fora do escopo

Front (próxima sprint), optante pelo Grupo B, EPI e Monte Carlo.
