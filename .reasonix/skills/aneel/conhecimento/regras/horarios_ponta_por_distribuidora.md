# Horários de Ponta / Intermediário por distribuidora (carga concluída)

## Origem
- Planilha: `Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm` (Kevin Wu)
  -> aba `Horários P, INT e FP` (103 distribuidoras).
- Script de carga: `scripts/cargar_horarios.py`.
- Tabela: `horario_posto_distribuidora` (lida/escrita só por infra; **não** é
  usada pelo core diretamente — o motor de fatura continua puro).

## Estrutura da tabela
| Coluna | Conteúdo |
|---|---|
| `distribuidora_id` | FK -> `distribuidora(id)` |
| `intermedio_1` | faixa antes da ponta (texto, ex.: `17:00 - 18:00`) |
| `hora_ponta` | faixa da ponta (ex.: `18:00 - 21:00`) |
| `intermedio_2` | faixa depois da ponta (ex.: `21:00 - 22:00`) |
| `reh` | REH que definiu os horários (ex.: `3.206/2023`) |
| `hora_inicio_*`/`hora_fim_*`/`n_horas_*` | versão numérica (TIME/numeric) |

## Resultado da carga
- **102 registros** carregados (103 linhas da planilha).
- Casamento: normalização (acentos/hífens) + tabela de equivalência
  (confirmada com o usuário). Ex.: `Enel SP -> ELETROPAULO`,
  `Roraima Energia -> ÂMBAR ENERGIA RR`, `Amazonas Energia -> Âmbar Amazonas`,
  `CPFL Piratininga -> CPFL-PIRATININGA`, `RGE (agrupada) -> RGE + RGE SUL`, etc.
- **Correção de dado:** CNPJ `89435598000155` estava como `Não Informado`;
  é a **Creral** (corrigido via SQL + equivalência no script).
- **Pendência (2):** `Forcel` e `Nova Palma` — sem CNPJ confirmado; prováveis
  ausências no dataset ANEEL (não têm tarifa publicada no CSV carregado).

## Nota de arquitetura
A tabela é um **catálogo de consulta** (infra). O motor de cálculo permanece
stateless e determinístico; os horários servem para exibição/análise e,
futuramente, para a regra P5 se precisarmos ratear consumo por horário.
