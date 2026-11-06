/**
 * Cliente da API FastAPI (Projeto ANEEL) — contrato documentado em
 * docs/integracao_front_back.md.
 *
 * Mapeia o formulário (InvoiceFormData) para o schema Consumidor da API
 * (snake_case) e para os query params de /api/calculo/fatura e /comparar.
 * Nenhuma regra de negócio vive aqui além do mapeamento de contrato.
 */
import { num } from './numeros';
import type { BandeiraTarifaria, InvoiceFormData, TariffModalidade } from '../types/energy';

const API_BASE: string =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? 'http://127.0.0.1:8000';

export const BASE_TARIFARIA = 'Tarifa de Aplicação';
export const NAO_SE_APLICA = 'Não se aplica';

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
    // Classe/subclasse/detalhe saem da tela: a API recebe sempre "Não se aplica"
    // (no Optante B a tarifa do Grupo B sai da atividade).
    classe: NAO_SE_APLICA,
    subclasse: NAO_SE_APLICA,
    detalhe: NAO_SE_APLICA,
    data_referencia: dataReferenciaIso(form.dataReferencia),
    consumo_ponta_kwh: num(form.consumoPonta),
    consumo_fora_ponta_kwh: num(form.consumoForaPonta),
    consumo_intermediario_kwh: num(form.consumoIntermediario),
    demanda_ponta_kw: num(form.demandaPontaKw),
    demanda_fora_ponta_kw: num(form.demandaForaPontaKw),
    demanda_contratada_ponta_kw: num(form.demandaContratadaPontaKw),
    demanda_contratada_fora_ponta_kw: num(form.demandaContratadaForaPontaKw),
    demanda_medida_unica_kw: num(form.demandaMedida),
    demanda_contratada_unica_kw: num(form.demandaContratada),
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
    potencia_transformadores_kva: num(form.potenciaTransformadoresKva),
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
    pis: String(num(form.pis) / 100),
    cofins: String(num(form.cofins) / 100),
    icms: String(num(form.icms) / 100),
    tipo_icms: form.tipoIcms,
    // buscarReativoAuto=true → a API busca VRERE/VRDRE (reativos_direto=false).
    reativos_direto: String(!form.buscarReativoAuto),
    arredondar_centavos: String(form.arredondarCentavos),
    tributar_reativos: String(form.tributarReativos),
    // Vazio = a API calcula a parcela isenta (contratada − medida).
    demanda_isenta_icms: String(form.demandaIsentaIcmsAtiva),
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

/**
 * Erro da API com o que foi enviado e o que voltou — o front mostra a
 * mensagem (`detail`) da API, nunca um texto genérico.
 */
export class ApiError extends Error {
  constructor(
    public readonly path: string,
    public readonly status: number,
    public readonly detail: string,
    public readonly corpoEnviado: unknown = null,
  ) {
    super(`${path} → ${status}: ${detail}`);
    this.name = 'ApiError';
  }
}

/** Extrai `detail` do corpo de erro do FastAPI (texto ou lista do pydantic). */
export function detalheErro(corpo: string): string {
  try {
    const j = JSON.parse(corpo) as { detail?: unknown };
    const d = j.detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) {
      return d
        .map((e: { loc?: unknown[]; msg?: string }) =>
          [Array.isArray(e.loc) ? e.loc.slice(1).join('.') : '', e.msg ?? ''].filter(Boolean).join(': '),
        )
        .join('; ');
    }
  } catch {
    /* corpo não é JSON */
  }
  return corpo.slice(0, 300) || 'sem resposta';
}

/** Mensagem legível de um erro qualquer (ApiError → detail da API). */
export function mensagemErro(e: unknown): string {
  if (e instanceof ApiError) return e.detail;
  if (e instanceof Error) return e.message;
  return String(e);
}

async function getJson(path: string): Promise<unknown> {
  const resp = await fetch(`${API_BASE}${path}`);
  if (!resp.ok) {
    const corpo = await resp.text().catch(() => '');
    throw new ApiError(`GET ${path}`, resp.status, detalheErro(corpo));
  }
  return resp.json();
}

async function postJson(
  path: string,
  body: Record<string, unknown>,
  params: Record<string, string>,
): Promise<unknown> {
  const qs = new URLSearchParams(params).toString();
  const url = `${API_BASE}${path}${qs ? `?${qs}` : ''}`;
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const corpo = await resp.text().catch(() => '');
    throw new ApiError(`POST ${path}`, resp.status, detalheErro(corpo), body);
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

/** POST /api/calculo/fatura com corpo e parâmetros já montados. */
export function postFatura(
  corpo: Record<string, unknown>,
  params: Record<string, string>,
): Promise<FaturaResponseApi> {
  return postJson('/api/calculo/fatura', corpo, params) as Promise<FaturaResponseApi>;
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

export interface OpcoesEpi {
  /** Modalidade ACR (Verde/Azul/Optante B). Sempre enviada: sem ela a API
   * escolhe a de menor custo com um perfil só de energia (sem demanda) e
   * pode falhar ao calcular as outras modalidades. */
  modalidade: string;
  /** false = E-PI simplificado (OPEX/CAPEX zerados). */
  comCustos: boolean;
  /** Sobrescreve o consumo/data (ex.: um mês do histórico). */
  consumoPontaKwh?: number;
  consumoForaPontaKwh?: number;
  dataReferenciaIso?: string;
}

/** Corpo de POST /api/epi/calcular (exportado para registro no PR/testes). */
export function corpoEpi(form: InvoiceFormData, o: OpcoesEpi): Record<string, unknown> {
  return {
    distribuidora: form.distribuidora,
    subgrupo: form.subgrupo,
    data_referencia: o.dataReferenciaIso ?? dataReferenciaIso(form.dataReferencia),
    modalidade: o.modalidade,
    consumo_ponta_kwh: o.consumoPontaKwh ?? num(form.consumoPonta),
    consumo_fora_ponta_kwh: o.consumoForaPontaKwh ?? num(form.consumoForaPonta),
    pis: num(form.pis) / 100,
    cofins: num(form.cofins) / 100,
    icms: num(form.icms) / 100,
    k: 0.03,
    encargos: num(form.encargosAcl),
    opex_mensal: o.comCustos ? form.opexMensal || 0 : 0,
    capex: o.comCustos ? form.capex || 0 : 0,
    horizonte_meses: form.horizonteMeses > 0 ? form.horizonteMeses : 60,
  };
}

export async function calcularEpi(form: InvoiceFormData, o: OpcoesEpi): Promise<EpiResultadoApi> {
  return (await postJson('/api/epi/calcular', corpoEpi(form, o), {})) as EpiResultadoApi;
}

/* ------------------------------------------------------------------ */
/* Planejamento anual — POST /api/planejamento/comparar                */
/* ------------------------------------------------------------------ */

export interface MesHistorico {
  data_referencia: string; // AAAA-MM-15
  /** Azul / histórico por posto. */
  d_med_ponta?: number;
  d_med_fora_ponta?: number;
  /** Fatura Verde: demanda medida única (vale para os dois postos na simulação Azul). */
  d_med_unica?: number;
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
 * Lê o histórico colado: uma linha por mês, em um dos formatos
 *   "MM/AAAA; demanda ponta; demanda fora ponta; consumo ponta; consumo fora ponta"
 *   "MM/AAAA; demanda única; consumo ponta; consumo fora ponta"   (fatura Verde)
 * (separador ';', tab ou espaços). Linha incompleta ou mês repetido vira erro
 * — nunca é completada com zero. Devolve os meses em ordem cronológica.
 */
export function lerHistorico(texto: string): { meses: MesHistorico[]; erros: string[] } {
  const meses: MesHistorico[] = [];
  const erros: string[] = [];
  const vistos = new Set<string>();
  let n = 0;
  for (const bruta of texto.split(/\r?\n/)) {
    const linha = bruta.trim();
    n += 1;
    if (!linha || linha.startsWith('#')) continue;
    const partes = linha.split(/[;\t]|\s{2,}|\s(?=\d)/).map((p) => p.trim()).filter(Boolean);
    const m = /^(\d{1,2})\/(\d{4})$/.exec(partes[0] ?? '');
    const nums = partes.slice(1).map(numeroBr);
    const mesNum = m ? Number(m[1]) : 0;
    if (!m || mesNum < 1 || mesNum > 12) {
      erros.push(`linha ${n}: mês inválido (use MM/AAAA) — "${linha}"`);
      continue;
    }
    if (nums.length !== 3 && nums.length !== 4) {
      erros.push(`linha ${n}: esperado 3 valores (demanda única; consumo ponta; consumo fora ponta) ou 4 (demanda ponta; demanda fora ponta; consumo ponta; consumo fora ponta) — "${linha}"`);
      continue;
    }
    if (nums.some((x) => Number.isNaN(x) || x < 0)) {
      erros.push(`linha ${n}: valor vazio, negativo ou ilegível — "${linha}"`);
      continue;
    }
    const chave = `${m[2]}-${m[1].padStart(2, '0')}`;
    if (vistos.has(chave)) {
      erros.push(`linha ${n}: mês ${m[1].padStart(2, '0')}/${m[2]} repetido`);
      continue;
    }
    vistos.add(chave);
    const base = { data_referencia: `${chave}-15` };
    meses.push(
      nums.length === 4
        ? { ...base, d_med_ponta: nums[0], d_med_fora_ponta: nums[1], e_ponta_kwh: nums[2], e_fora_ponta_kwh: nums[3] }
        : { ...base, d_med_unica: nums[0], e_ponta_kwh: nums[1], e_fora_ponta_kwh: nums[2] },
    );
  }
  meses.sort((a, b) => a.data_referencia.localeCompare(b.data_referencia));
  return { meses, erros };
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
  equilibrio: { dp_eq: number; mensagem: string } | null;
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
    classe: NAO_SE_APLICA,
    detalhe: NAO_SE_APLICA,
    atividade: form.atividade,
    tipo_ligacao: form.tipoLigacao,
    data_referencia: dataReferenciaIso(form.dataReferencia),
    meses,
    pis: num(form.pis) / 100,
    cofins: num(form.cofins) / 100,
    icms: num(form.icms) / 100,
    tipo_icms: form.tipoIcms,
    demanda_isenta_icms: form.demandaIsentaIcmsAtiva,
    tributar_reativos: form.tributarReativos,
    modalidade_atual: azul ? 'Azul' : 'Verde',
    dc_atual_verde: azul ? null : (num(form.demandaContratada) || null),
    dc_atual_azul_ponta: azul ? (num(form.demandaContratadaPontaKw) || null) : (num(form.demandaContratada) || null),
    dc_atual_azul_fora: azul ? (num(form.demandaContratadaForaPontaKw) || null) : (num(form.demandaContratada) || null),
    k: 0.03,
    encargos: num(form.encargosAcl),
    opex_mensal: form.opexMensal || 0,
    capex: form.capex || 0,
    horizonte_meses: form.horizonteMeses > 0 ? form.horizonteMeses : 60,
  };
  return (await postJson('/api/planejamento/comparar', corpo, {})) as PlanejamentoApi;
}
