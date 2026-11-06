# Entradas do simulador: obrigatórias, opcionais e casos de histórico

Regra geral: **o que o usuário não informou nunca vira zero escondido.**
Obrigatório vazio bloqueia o cálculo com a lista do que falta; opcional vazio
usa um padrão que aparece no relatório ("Conferência e premissas").
Implementação: `frontend/src/lib/validacao.ts`.

## Fluxo e dados de cada cálculo

| Etapa | Endpoint | Usa |
|---|---|---|
| Fatura do mês | `/api/calculo/fatura` | identificação, consumo, demanda, tributos, reativo |
| Conferência (D7) | front | total impresso na fatura (opcional) |
| Comparação de modalidades | `/api/calculo/comparar` | idem + elegibilidade Optante B |
| Planejamento de demanda | `/api/planejamento/comparar` | meses (histórico + mês da fatura), DC atual |
| E-PI | `/api/epi/calcular` | consumo, tributos, k = 3%, encargos, OPEX/CAPEX |

## Obrigatórios

| Campo | Quando |
|---|---|
| Distribuidora, subgrupo, data de referência | sempre |
| Consumo ponta e fora de ponta | Grupo A e Branca (0 só se digitado) |
| Consumo intermediário | Branca |
| Demanda medida e contratada única (≥ 30 kW) | Verde |
| Demanda medida e contratada ponta/fora ponta | Azul |
| Critério do art. 292 (kVA, hotelaria ou refletores) | modalidade atual Optante B |
| PIS, COFINS, ICMS | tributos ligados (ICMS 0 se digitado) |
| Tarifa de reativo | reativo informado e busca automática desligada |
| Horizonte de amortização | CAPEX > 0 |
| Histórico sem linhas ilegíveis ou meses repetidos | se houver histórico |

## Opcionais (padrão declarado)

Classe/subclasse/detalhe ("Não se aplica"), bandeira (automática), demanda
isenta de ICMS (API calcula contratada − medida), reativos (não cobrados),
CIP/outros (fora do custo técnico, D4), elegibilidade Optante B para Verde/Azul
(sem ela: **não avaliado**, não "inelegível"), encargos do ACL (0, declarado),
OPEX/CAPEX (E-PI simplificado), proposta ACL, total da fatura (sem
conferência), código e nome da UC.

## Histórico

Formatos por linha: `MM/AAAA; dP; dFP; eP; eFP` (por posto) ou
`MM/AAAA; demanda única; eP; eFP` (fatura Verde).

| Caso | Comportamento |
|---|---|
| Sem histórico | planejamento só com o mês da fatura; "parcial", DC indicativa, sem anualizar |
| 2–11 meses | só os meses informados, sem extrapolar; aviso de picos ausentes |
| 12 meses | análise completa |
| > 12 meses | 12 mais recentes, com aviso |
| Mês da fatura no histórico com os mesmos valores | mantém a linha do histórico (pode ter demanda por posto) |
| Mês da fatura difere do histórico | vale o formulário, com aviso |
| Linha incompleta, mês inválido ou repetido | erro com o nº da linha; bloqueia o cálculo |
| Meses faltando no meio | não entram (nunca zero); aviso |
| Só demanda única (Verde) | Azul simulada com o mesmo valor nos dois postos; aviso de custo de ponta superestimado |
