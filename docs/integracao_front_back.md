# Integração front ↔ back — contrato de parâmetros

> Fonte: repo `vitorserrao/SIMULADOR-FATURA` (front, sincronizado em
> `frontend/`) × API FastAPI (`api/`, `schemas/`, `services/`).
> Data: 09/10/2026. Esta tabela é a referência única para a integração.

## Endpoints da API (base: `http://127.0.0.1:8000`; prefixo `/api`)

| Endpoint | Uso no front |
|---|---|
| `POST /api/calculo/fatura?modalidade=...` | Fatura de UMA modalidade (`FaturaResponse{fatura, notas}`) |
| `POST /api/calculo/comparar` | Ranking Azul×Verde×Optante B (`ComparacaoResponse{comparacao{disponiveis, indisponiveis, melhor}, notas}`) |
| `GET /api/distribuidoras` | Lista real de distribuidoras (substitui `DISTRIBUTORS` hardcoded) |
| `GET /api/subgrupos` | Subgrupos reais do banco (substitui `SUBGROUPS` hardcoded) |
| `GET /api/modalidades`, `GET /api/classes` | Listas reais de modalidades/classes |
| `GET /api/bandeira?competencia=AAAA-MM-DD` | Bandeira vigente + valor (substitui tabela fixa) |
| `GET /api/bandeiras?competencia=AAAA-MM-DD` | Opções de bandeira + valores vigentes |
| `GET /api/tarifas?...` | Consulta de tarifas por filtros (tela de auditoria) |

- **Atualização 04/11/2026 (front mínimo):** o front chama também
  `POST /api/epi/calcular` (E-PI simplificado ou com OPEX/CAPEX) e, quando o
  usuário cola o histórico de 12 meses, `POST /api/planejamento/comparar`.
  O motor de demonstração (`calculateAudit`) foi **removido**: sem API não há
  relatório (o front mostra o erro e não estima valores). O custo no ACL só
  aparece quando há proposta: `custo ACR − (E-PI − preço) × base ACL`.
- CORS configurado em `api/main.py` (`FRONTEND_ORIGINS`).

### Atualização 06/11/2026 — simulação front × API real

Achados ao rodar o código do front contra a API + PostgreSQL reais (7 cenários
seguidos). O que mudou:

| Ponto | Antes | Agora |
|---|---|---|
| `GET /api/bandeiras` | front enviava `competencia=AAAA-MM`; a API exige **AAAA-MM-DD** (`date.fromisoformat`) → **400 em toda consulta** | front envia a data completa (`dataReferenciaIso`) |
| `bandeira_valor` (tabela) | **vazia**: a API devolvia `valor_kwh: 0` em todas as bandeiras (a bandeira manual cairia em R$ 0) | carregar com `scripts/cargar_bandeira_valores.py` (30 registros). `bandeira_tarifaria` só cobre até 06/2025 |
| `POST /api/calculo/comparar` | ignorava em silêncio `demanda_isenta_icms`, `demanda_isenta_icms_kw`, `arredondar_centavos`, `tributar_reativos` (totais divergiam do `/fatura`: 10.297,70 × 9.851,96) | flags aceitas e repassadas; totais iguais aos do `/fatura` |
| `POST /api/epi/calcular` `modalidade="Optante B"` | **400 "TE indisponível"**: o E-PI buscava a modalidade "Optante B", que não existe no dataset (art. 292 manda usar a Convencional do Grupo B) | `core.motor_calculo.tarifa_b_do_optante()` é a fonte única; o E-PI aceita também `atividade` (B1/B2/B3) |
| Conexões | cada request criava uma `Engine` nova → `FATAL: sorry, too many clients already` após ~7 análises | `get_session_factory()` compartilhada (`infra/database.py`) |

Contrato do E-PI (`EPISolicitacao`) ganhou **`atividade`** (default
`"Comercial ou Industrial"`); o front envia `form.atividade`.

## Parâmetros do formulário (front) → Consumidor/query (back)

| Front (`InvoiceFormData`) | Back | Observação |
|---|---|---|
| `distribuidora` (sigAgente) | `Consumidor.distribuidora` | vir de `GET /distribuidoras` |
| `subgrupo` | `Consumidor.subgrupo` | **corrigir**: "Optante B" não é subgrupo — remover da lista; subgrupos reais A1–AS/B1–B4 |
| `modalidadeAtual` (`verde/azul/optante_b/branca/convencional`) | query `modalidade` (`Verde/Azul/Optante B/Branca/Convencional Monômia`) | remover `grupo_b` (alias inventado) |
| `dataReferencia` (`DD/MM/AAAA`) | `data_referencia` (`AAAA-MM-DD`) | converter |
| `classe`, `subclasse`, `detalhe` | `Consumidor.classe/subclasse/detalhe` | **faltam no front** — necessários p/ tarifa B (B1/B3) |
| `consumoPonta/ForaPonta/Intermediario` | `consumo_ponta_kwh/fora_ponta_kwh/intermediario_kwh` | ok |
| `demandaMedida/Contratada` (únicos) | Verde: `demanda_medida_unica_kw/contratada_unica_kw` | ok p/ Verde |
| — | Azul: `demanda_ponta_kw`, `demanda_fora_ponta_kw`, `demanda_contratada_ponta_kw`, `demanda_contratada_fora_ponta_kw` | **faltam no front** (só existe demanda única) |
| `demandaIsentaIcms` | query `demanda_isenta_icms=true` + `demanda_isenta_icms_kw` | adicionar toggle + valor |
| `outrosValores` | `outros_rs` | ok |
| `percentualConsumoMesAnterior` | `percentual_mes_anterior` | ok |
| `precoMedioACL` | sem endpoint no back (EPI esqueleto) | manter estimativa local documentada |
| `bandeiraAutomatica`/`bandeira` | `bandeira_adicional_r_kwh` (0 = automática via `GET /bandeira`) | valores fixos do front estão errados (amarela 0,01885 vs oficial 0,01874) — usar `/bandeiras` |
| `buscarReativoAuto` | `reativos_direto=false` (art. 304) / `true` com tarifas manuais | mapear |
| tarifas manuais de reativo | query `tarifa_reativo_energia_r_kvarh`, `tarifa_reativo_demanda_r_kvar` | adicionar inputs no modo manual |
| `consumoReativoPonta/ForaPonta`, `demandaReativaPonta/ForaPonta` | `reativo_energia_*_kvArh`, `reativo_demanda_*_kvAr` | ok |
| — | `reativo_energia_capacitiva_kvArh`, `reativo_demanda_capacitiva_kvAr` | **faltam no front** (capacitivos 0h–6h) |
| `aplicarTributos`, `pis/cofins/icms` (%), `tipoIcms` | query `aplicar_tributos`, `pis`, `cofins`, `icms` (frações), `tipo_icms` | converter % → fração |
| `cipCosip` | `cip_cosip_rs` | ok |
| `ucCode`, `unidadeNome` | sem equivalente | metadados locais (manter no front) |
| — | `atividade`, `tipo_ligacao`, `pre_pagamento`, `potencia_transformadores_kva`, `cooperativa_eletrificacao_rural`, `hotelaria_turismo`, `carga_refletores_kw`, `carga_instalada_total_kw` | **faltam no front** — bloco Optante B (art. 292) |
| — | query `tributar_reativos`, `arredondar_centavos`, `base_tarifaria` | toggles opcionais no front (base fixa "Tarifa de Aplicação") |

## Contrato de resposta → tipos do front

- `FaturaOut`: `{modalidade, base_tarifaria, linhas[{descricao, categoria,
  quantidade, tarifa, custo}], custo_tarifas, custo_total, aplicar_tributos,
  tarifas_nao_mapeadas}`.
- **`categoria` do back** ∈ `TARIFA | ULTRAPASSAGEM | REATIVOS | BANDEIRA |
  ENCARGO | OUTROS` → mapear para as categorias de exibição do front
  (`TE/TUSD/Demanda` derivadas da `descricao` + `TARIFA`; `ULTRAPASSAGEM` →
  Demanda; `REATIVOS` → Outros/Reativos; `BANDEIRA` → Bandeira; `ENCARGO`/
  `OUTROS` → Outros; tributos calculados pelo front quando `aplicar_tributos`).
- `ComparacaoOut`: `{disponiveis[], indisponiveis[{modalidade, motivo}],
  melhor}` → ranking/economia do relatório.
- `notas[]: {tipo, mensagem}` → exibir no relatório (ex.: `tarifa_ambigua`).

## Divergências do motor demo (`calculator.ts`) a corrigir no fallback

- Convencional com cobrança de demanda (Grupo B monômia não fatura demanda).
- Branca = Convencional × 0,94 (inventado) — usar tarifa de 3 postos.
- `grupo_b` = Convencional × 1,08 (inventado) — remover.
- Valores de bandeira fora do oficial (REN 479/2012).
- Optante B tratado como subgrupo — corrigir para modalidade do Grupo A com
  os 4 critérios do art. 292 (mesma regra do `core/motor_calculo.py`).
