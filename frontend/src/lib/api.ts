/**
 * Cliente da API FastAPI (Projeto ANEEL) — contrato documentado em
 * docs/integracao_front_back.md.
 *
 * Mapeia o formulário (InvoiceFormData) para o schema Consumidor da API
 * (snake_case) e para os query params de /api/calculo/fatura e /comparar.
 * Nenhuma regra de negócio vive aqui além do mapeamento de contrato.
 */
import type { BandeiraTarifaria, InvoiceFormData, TariffModalidade } from '../types/energy';

const API_BASE: string =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? 'http://127.0.0.1:8000';

export const BASE_TARIFARIA = 'Tarifa de Aplicação';

/** Modalidade do formulário → valor aceito pelo back (query `modalidade`). */
const MODALIDADE_QUERY: Record<TariffModalidade, string> = {
  verde: 'Verde',
  azul: 'Azul',
  optante_b: 'Optante B',
  branca: 'Branca',
  convencional: 'Convencional Monômia',
};

/** Valores oficiais REN 479/2012 — fallback quando a API está indisponível. */
const BANDEIRA_VALOR: Record<BandeiraTarifaria, number> = {
  verde: 0,
  amarela: 0.01874,
  vermelha1: 0.03971,
  vermelha2: 0.09492,
};

/** Nome da bandeira na API (`GET /api/bandeiras` → opcoes[].bandeira). */
const BANDEIRA_API: Record<BandeiraTarifaria, string> = {
  verde: 'Verde',
  amarela: 'Amarela',
  vermelha1: 'Vermelha P1',
  vermelha2: 'Vermelha P2',
};

/** Bandeira da API (`Vermelha P1`) → id do formulário (`vermelha1`). */
export function bandeiraApiParaForm(nome: string): BandeiraTarifaria {
  const n = nome.toLowerCase();
  if (n.includes('vermelha') && n.includes('2')) return 'vermelha2';
  if (n.includes('vermelha')) return 'vermelha1';
  if (n.includes('amarela')) return 'amarela';
  return 'verde';
}

/** Valor R$/kWh da bandeira manual: opções da API (se disponíveis) ou oficial. */
export function bandeiraValorKwh(
  bandeira: BandeiraTarifaria,
  opcoes?: { bandeira: string; valor_kwh: number }[] | null,
): number {
  if (opcoes && opcoes.length > 0) {
    const alvo = BANDEIRA_API[bandeira];
    const encontrada = opcoes.find((o) => o.bandeira === alvo);
    if (encontrada) return encontrada.valor_kwh;
  }
  return BANDEIRA_VALOR[bandeira];
}

/** Converte DD/MM/AAAA (exibição) para AAAA-MM-DD (API). */
export function dataReferenciaIso(dataReferencia: string): string {
  const d = dataReferencia.trim();
  const br = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(d);
  if (br) return `${br[3]}-${br[2]}-${br[1]}`;
  const iso = /^\d{4}-\d{2}-\d{2}$/.exec(d);
  if (iso) return d;
  return d;
}

/** Competência AAAA-MM a partir da data de referência (exibição). */
export function competenciaIso(dataReferencia: string): string {
  return dataReferenciaIso(dataReferencia).slice(0, 7);
}

/** InvoiceFormData → corpo Consumidor da API (schemas/consumidor.py). */
export function paraConsumidor(
  form: InvoiceFormData,
  bandeirasOpcoes?: { bandeira: string; valor_kwh: number }[] | null,
): Record<string, unknown> {
  return {
    distribuidora: form.distribuidora,
    subgrupo: form.subgrupo,
    classe: form.classe || 'Não se aplica',
    subclasse: form.subclasse || 'Não se aplica',
    detalhe: form.detalhe || 'Não se aplica',
    data_referencia: dataReferenciaIso(form.dataReferencia),
    consumo_ponta_kwh: form.consumoPonta,
    consumo_fora_ponta_kwh: form.consumoForaPonta,
    consumo_intermediario_kwh: form.consumoIntermediario,
    demanda_ponta_kw: form.demandaPontaKw,
    demanda_fora_ponta_kw: form.demandaForaPontaKw,
    demanda_contratada_ponta_kw: form.demandaContratadaPontaKw,
    demanda_contratada_fora_ponta_kw: form.demandaContratadaForaPontaKw,
    demanda_medida_unica_kw: form.demandaMedida,
    demanda_contratada_unica_kw: form.demandaContratada,
    percentual_mes_anterior: form.percentualConsumoMesAnterior,
    // 0 = automática (a API resolve a bandeira vigente pela competência).
    bandeira_adicional_r_kwh: form.bandeiraAutomatica
      ? 0
      : bandeiraValorKwh(form.bandeira, bandeirasOpcoes),
    cip_cosip_rs: form.cipCosip,
    outros_rs: form.outrosValores,
    reativo_energia_ponta_kvArh: form.consumoReativoPonta,
    reativo_energia_fora_ponta_kvArh: form.consumoReativoForaPonta,
    reativo_demanda_ponta_kvAr: form.demandaReativaPonta,
    reativo_demanda_fora_ponta_kvAr: form.demandaReativaForaPonta,
    reativo_energia_capacitiva_kvArh: form.reativoEnergiaCapacitiva,
    reativo_demanda_capacitiva_kvAr: form.reativoDemandaCapacitiva,
    atividade: form.atividade,
    tipo_ligacao: form.tipoLigacao,
    pre_pagamento: form.prePagamento,
    potencia_transformadores_kva: form.potenciaTransformadoresKva,
    cooperativa_eletrificacao_rural: form.cooperativaEletrificacaoRural,
    hotelaria_turismo: form.hotelariaTurismo,
    carga_refletores_kw: form.cargaRefletoresKw,
    carga_instalada_total_kw: form.cargaInstaladaTotalKw,
  };
}

/** Query params de /api/calculo/fatura e /api/calculo/comparar. */
export function queryParamsFatura(
  form: InvoiceFormData,
  modalidade: TariffModalidade,
): Record<string, string> {
  const params: Record<string, string> = {
    modalidade: MODALIDADE_QUERY[modalidade],
    base_tarifaria: BASE_TARIFARIA,
    aplicar_tributos: String(form.aplicarTributos),
    pis: String(form.pis / 100),
    cofins: String(form.cofins / 100),
    icms: String(form.icms / 100),
    tipo_icms: form.tipoIcms,
    // buscarReativoAuto=true → a API busca VRERE/VRDRE (reativos_direto=false).
    reativos_direto: String(!form.buscarReativoAuto),
    arredondar_centavos: String(form.arredondarCentavos),
    tributar_reativos: String(form.tributarReativos),
    demanda_isenta_icms: String(form.demandaIsentaIcmsAtiva && form.demandaIsentaIcms > 0),
  };
  if (!form.buscarReativoAuto) {
    if (form.tarifaReativoEnergia > 0) {
      params.tarifa_reativo_energia_r_kvarh = String(form.tarifaReativoEnergia);
    }
    if (form.tarifaReativoDemanda > 0) {
      params.tarifa_reativo_demanda_r_kvar = String(form.tarifaReativoDemanda);
    }
  }
  if (form.demandaIsentaIcmsAtiva && form.demandaIsentaIcms > 0) {
    params.demanda_isenta_icms_kw = String(form.demandaIsentaIcms);
  }
  return params;
}

/* ------------------------------------------------------------------ */
/* Contratos de resposta (espelho de schemas/fatura.py e consulta.py)   */
/* ------------------------------------------------------------------ */

export interface LinhaFaturaApi {
  descricao: string;
  categoria: string;
  quantidade: number;
  tarifa: number;
  custo: number;
}

export interface FaturaApi {
  modalidade: string;
  base_tarifaria: string;
  linhas: LinhaFaturaApi[];
  custo_tarifas: number;
  custo_total: number;
  aplicar_tributos: boolean;
  tarifas_nao_mapeadas: number;
}

export interface NotaApi {
  tipo: string;
  mensagem: string;
}

export interface FaturaResponseApi {
  fatura: FaturaApi;
  notas: NotaApi[];
}

export interface ComparacaoApi {
  disponiveis: FaturaApi[];
  indisponiveis: { modalidade: string; motivo: string }[];
  melhor: string | null;
}

export interface ComparacaoResponseApi {
  comparacao: ComparacaoApi;
  notas: NotaApi[];
}

export interface DistribuidoraApi {
  num_cnpj: string;
  sig_agente: string;
}

export interface BandeirasApi {
  competencia: string;
  ativa: string | null;
  opcoes: { bandeira: string; valor_kwh: number }[];
}

/* ------------------------------------------------------------------ */
/* HTTP                                                                */
/* ------------------------------------------------------------------ */

async function getJson(path: string): Promise<unknown> {
  const resp = await fetch(`${API_BASE}${path}`);
  if (!resp.ok) {
    const corpo = await resp.text().catch(() => '');
    throw new Error(`GET ${path} → ${resp.status}: ${corpo.slice(0, 300)}`);
  }
  return resp.json();
}

async function postJson(
  path: string,
  body: Record<string, unknown>,
  params: Record<string, string>,
): Promise<unknown> {
  const url = `${API_BASE}${path}?${new URLSearchParams(params).toString()}`;
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const corpo = await resp.text().catch(() => '');
    throw new Error(`POST ${path} → ${resp.status}: ${corpo.slice(0, 300)}`);
  }
  return resp.json();
}

/* ------------------------------------------------------------------ */
/* Operações                                                           */
/* ------------------------------------------------------------------ */

export type BandeiraOpcao = { bandeira: string; valor_kwh: number };

export function calcularFatura(
  form: InvoiceFormData,
  modalidade: TariffModalidade,
  bandeirasOpcoes?: BandeiraOpcao[] | null,
): Promise<FaturaResponseApi> {
  return postJson(
    '/api/calculo/fatura',
    paraConsumidor(form, bandeirasOpcoes),
    queryParamsFatura(form, modalidade),
  ) as Promise<FaturaResponseApi>;
}

export function compararModalidades(
  form: InvoiceFormData,
  bandeirasOpcoes?: BandeiraOpcao[] | null,
): Promise<ComparacaoResponseApi> {
  return postJson(
    '/api/calculo/comparar',
    paraConsumidor(form, bandeirasOpcoes),
    queryParamsFatura(form, form.modalidadeAtual),
  ) as Promise<ComparacaoResponseApi>;
}

export function listarDistribuidoras(): Promise<DistribuidoraApi[]> {
  return getJson('/api/distribuidoras') as Promise<DistribuidoraApi[]>;
}

export function listarSubgrupos(): Promise<string[]> {
  return getJson('/api/subgrupos') as Promise<string[]>;
}

export function listarClasses(): Promise<string[]> {
  return getJson('/api/classes') as Promise<string[]>;
}

export function listarBandeiras(dataReferencia: string): Promise<BandeirasApi> {
  return getJson(`/api/bandeiras?competencia=${competenciaIso(dataReferencia)}`) as Promise<BandeirasApi>;
}

/* ------------------------------------------------------------------ */
/* E-PI — POST /api/epi/calcular                                       */
/* ------------------------------------------------------------------ */

export interface EpiResultadoApi {
  pi: number;
  modalidade: string;
  bandeira_r_mwh: number;
  e_mwh: number;
  c_te: number;
  c_e_acr: number;
  custos_acl: number;
  base_acl: number;
  aviso: string | null;
}

/** E-PI do perfil (modalidade = menor custo no ACR quando omitida). */
export async function calcularEpi(
  form: InvoiceFormData,
  modalidadeApi?: string,
): Promise<EpiResultadoApi> {
  const corpo: Record<string, unknown> = {
    distribuidora: form.distribuidora,
    subgrupo: form.subgrupo,
    data_referencia: dataReferenciaIso(form.dataReferencia),
    consumo_ponta_kwh: form.consumoPonta,
    consumo_fora_ponta_kwh: form.consumoForaPonta,
    pis: form.pis / 100,
    cofins: form.cofins / 100,
    icms: form.icms / 100,
    k: 0.03,
    opex_mensal: form.opexMensal || 0,
    capex: form.capex || 0,
    horizonte_meses: form.horizonteMeses > 0 ? form.horizonteMeses : 60,
  };
  if (modalidadeApi) corpo.modalidade = modalidadeApi;
  return (await postJson('/api/epi/calcular', corpo, {})) as EpiResultadoApi;
}

/* ------------------------------------------------------------------ */
/* Planejamento anual — POST /api/planejamento/comparar                */
/* ------------------------------------------------------------------ */

export interface MesHistorico {
  data_referencia: string; // AAAA-MM-15
  d_med_ponta: number;
  d_med_fora_ponta: number;
  e_ponta_kwh: number;
  e_fora_ponta_kwh: number;
}

/** Número em pt-BR ("12.345,6") ou en ("12345.6") → number. */
function numeroBr(txt: string): number {
  const t = txt.trim();
  if (!t) return NaN;
  if (t.includes(',')) return Number(t.replace(/\./g, '').replace(',', '.'));
  // "54.950" com 3 casas após o ponto = milhar pt-BR
  if (/^\d{1,3}(\.\d{3})+$/.test(t)) return Number(t.replace(/\./g, ''));
  return Number(t);
}

/**
 * Lê o histórico colado: uma linha por mês, no formato
 * "MM/AAAA; demanda ponta; demanda fora ponta; consumo ponta; consumo fora ponta"
 * (separador ';', tab ou espaços). Devolve os meses válidos em ordem cronológica
 * e a lista de linhas que não puderam ser lidas.
 */
export function lerHistorico(texto: string): { meses: MesHistorico[]; erros: string[] } {
  const meses: MesHistorico[] = [];
  const erros: string[] = [];
  for (const bruta of texto.split(/\r?\n/)) {
    const linha = bruta.trim();
    if (!linha) continue;
    const partes = linha.split(/[;\t]|\s{2,}|\s(?=\d)/).map((p) => p.trim()).filter(Boolean);
    const m = /^(\d{1,2})\/(\d{4})$/.exec(partes[0] ?? '');
    const nums = partes.slice(1, 5).map(numeroBr);
    if (!m || nums.length < 4 || nums.some((n) => Number.isNaN(n) || n < 0)) {
      erros.push(linha);
      continue;
    }
    const mes = m[1].padStart(2, '0');
    meses.push({
      data_referencia: `${m[2]}-${mes}-15`,
      d_med_ponta: nums[0],
      d_med_fora_ponta: nums[1],
      e_ponta_kwh: nums[2],
      e_fora_ponta_kwh: nums[3],
    });
  }
  meses.sort((a, b) => a.data_referencia.localeCompare(b.data_referencia));
  return { meses: meses.slice(-12), erros };
}

export interface PlanejamentoApi {
  melhor_contrato_atual: string;
  melhor_demanda_otimizada: string;
  ganho: { total: number; demanda: number; modalidade: number };
  modalidades: {
    modalidade: string;
    custo_contrato_atual: number;
    custo_demanda_otimizada: number;
    dc_atual: number | [number, number] | null;
    dc_otima: number | [number, number];
    pi: { anual: number | null; mensal: (number | null)[] } | null;
  }[];
  avisos: string[];
}

export async function compararPlanejamento(
  form: InvoiceFormData,
  meses: MesHistorico[],
): Promise<PlanejamentoApi> {
  const azul = form.modalidadeAtual === 'azul';
  const corpo: Record<string, unknown> = {
    distribuidora: form.distribuidora,
    subgrupo: form.subgrupo,
    classe: form.classe || 'Não se aplica',
    detalhe: form.detalhe || 'Não se aplica',
    atividade: form.atividade,
    tipo_ligacao: form.tipoLigacao,
    data_referencia: dataReferenciaIso(form.dataReferencia),
    meses,
    pis: form.pis / 100,
    cofins: form.cofins / 100,
    icms: form.icms / 100,
    tipo_icms: form.tipoIcms,
    demanda_isenta_icms: true,
    tributar_reativos: form.tributarReativos,
    modalidade_atual: azul ? 'Azul' : 'Verde',
    dc_atual_verde: azul ? null : form.demandaContratada || null,
    dc_atual_azul_ponta: azul ? form.demandaContratadaPontaKw || null : form.demandaContratada || null,
    dc_atual_azul_fora: azul ? form.demandaContratadaForaPontaKw || null : form.demandaContratada || null,
    k: 0.03,
    opex_mensal: form.opexMensal || 0,
    capex: form.capex || 0,
    horizonte_meses: form.horizonteMeses > 0 ? form.horizonteMeses : 60,
  };
  return (await postJson('/api/planejamento/comparar', corpo, {})) as PlanejamentoApi;
}
