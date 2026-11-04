# Planejamento anual de modalidades (Azul × Verde × Optante B)

> Status: **core implementado** (`core/planejamento.py`). A integração com o
> motor completo e a API ficam na camada de serviço.

## Premissas adotadas (registro formal)

1. **Horizonte de 12 meses.** A troca de modalidade vale por no mínimo 12
   meses; o comparador aceita 1 a 12 meses e **avisa** quando recebe menos
   de 12 (resultado parcial). `Σ_m Fatura_motor(m, DC)` é o custo anual.
2. **Demanda medida ausente (fatura Verde sem ponta).** Quando só existe
   `d_med_unica`: Verde usa `D = d_med_unica`; Azul usa
   `Dp = Dfp = d_med_unica` (estimativa conservadora) + aviso, e calcula a
   **demanda de ponta de equilíbrio** (item C). Se o usuário informar
   `d_med_ponta`/`d_med_fora_ponta` (ex.: Histórico de Consumo HP/HFP),
   o split prevalece; Verde usa `max(ponta, fora)`.
3. **Faturamento de demanda (referência do motor):** `D_faturável = max(DC,
   D_med)`; ultrapassagem `(D_med − DC)·2·T` quando `D_med > 1,05·DC`
   (art. 301); ociosidade `max(DC − D_med, 0)`.
4. **Critério de otimização:** `DC* = argmin Σ_m Fatura_motor(m, DC)` com
   busca discreta de **passo 1 kW**; **DC_min = 30 kW** (mínimo regulatório
   do Grupo A); **DC_max = ceil(max(D_med)·1,2)**. Empate escolhe a **menor
   DC**. Azul otimiza ponta e fora de ponta **separadamente** (custos
   independentes) e confirma o total.
5. **Tolerância de 5%** para ultrapassagem (art. 301) e **fator 2** na
   tarifa de ultrapassagem.
6. **Caráter de referência:** a demanda ótima exibida está sujeita às regras
   de alteração contratual da REN 1.000/2021 (não implementadas) — aviso
   exibido no resultado.
7. **Decomposição do ganho:**
   `Ganho_total = Custo(atual, contrato atual) − Custo(melhor, demanda ótima)`;
   `Ganho_demanda = Custo(atual, contrato atual) − Custo(atual, demanda ótima)`;
   `Ganho_modalidade = Ganho_total − Ganho_demanda`.
8. **PI:** calculado sobre a **melhor alternativa do cenário demanda
   otimizada** (a fórmula do PI não muda — `core/epi.py`).
9. **Fora do escopo:** prazo/regras de alteração contratual, sazonalidade de
   contrato e geração distribuída.

## Itens implementados no core (`core/planejamento.py`)

| Item | Função |
|---|---|
| A | `montar_demanda` / `montar_demandas` |
| B | `otimizar_contrato` / `otimizar_contrato_azul` / `custo_demanda_mensal` |
| C | `demanda_ponta_equilibrio` |
| D | `comparar_planejamento` / `decompor_ganho` |

O core recebe funções de custo injetáveis (`custo_fn`): nos testes, funções
sintéticas só de demanda; no serviço, o custo mensal real do motor completo.

## Integração (service + API)

- `services/planejamento_service.py` injeta o **custo mensal do motor
  completo com tributos** no otimizador (`calcular_fatura` com as parcelas
  vigentes de cada mês) — `custo_demanda_mensal` fica restrito aos testes
  sintéticos (teste de consistência garante que a parcela de demanda dela é
  igual à linha de demanda do motor para os mesmos dados).
- As tarifas são buscadas **em cada mês do histórico** (a data de referência
  de cada mês seleciona a vigência, tratando reajustes dentro do período);
  as parcelas são pré-carregadas uma vez por mês/modalidade via
  `CalculoService.parcelas_vigentes` (mesmas regras de filtro/ambiguidade/
  sazonalidade do cálculo validado).
- O Optante B usa a **elegibilidade já existente** (`modalidades_elegiveis`).
- O PI do período é calculado **somando mês a mês**
  (`PI = (Σ C_E_ACR[m] − n·OPEX − n·CAPEX/N) / Σ BASE_ACL[m]`, com TE e
  bandeira de cada mês); o **PI mensal** é mantido apenas como informação.
- **Reativos são considerados constantes** nesta versão (os campos do perfil
  base valem para todos os meses do histórico).
- **Busca de DC por pontos de quebra:** `{30} ∪ {ceil(D_med/1,05)} ∪ {D_med}`
  por posto — exato e mais rápido que a busca de 1 kW; teste garante
  resultado idêntico à busca exaustiva (sintético e CEMIG-D 2023).
- Endpoint: `POST /api/planejamento/comparar` (schemas em
  `schemas/planejamento.py`).
- Teste de integração anual: histórico jan–dez/2023 da fatura CEMIG-D
  CII_112; o cenário "contrato atual" de dez/2023 reproduz a fatura real
  dentro da tolerância (R$ 0,05 por item / R$ 1,00 no total).
