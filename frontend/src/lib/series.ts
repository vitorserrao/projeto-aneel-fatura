/**
 * Séries mensais da etapa 3, montadas com POST /api/calculo/fatura (B5/B6).
 *
 * Cada mês é pedido como o /api/planejamento/comparar o calcula
 * (services/planejamento_service.py): só consumo, demanda medida do mês e
 * demanda contratada; sem reativos, CIP, outros nem rateio; tributos sempre
 * aplicados; parcela isenta de ICMS calculada pela API; sem arredondamento;
 * bandeira automática da competência. Assim a soma dos meses tem de bater com
 * os totais do planejamento (±R$ 1) — se não bater, a tela mostra o aviso.
 */
import { num } from './numeros';
import { BASE_TARIFARIA, NAO_SE_APLICA, FaturaApi, MesHistorico, PlanejamentoApi, mensagemErro, postFatura } from './api';
import { Contrato, contratoDoPlanejamento } from './cenarios';
import { executarComLimite } from './pool';
import type { InvoiceFormData } from '../types/energy';

export type ModSerie = 'Verde' | 'Azul';

const MESES_CURTOS = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];

export interface MesBase {
  /** AAAA-MM-15 */
  data: string;
  /** "jan/23" */
  rotulo: string;
  ePontaKwh: number;
  eForaKwh: number;
  /** Demanda medida usada pela Verde (máx. ponta/fora ou a única). */
  dVerde: number;
  dPonta: number;
  dFora: number;
  /** true = o histórico trouxe demanda por posto (não estimada pela única). */
  pontaInformada: boolean;
}

export function rotuloMes(iso: string): string {
  const m = Number(iso.slice(5, 7));
  return `${MESES_CURTOS[m - 1]}/${iso.slice(2, 4)}`;
}

/** Mesma regra de core.planejamento.montar_demanda. */
export function mesesBase(meses: MesHistorico[]): MesBase[] {
  return meses.map((m) => {
    const porPosto = m.d_med_ponta !== undefined && m.d_med_fora_ponta !== undefined;
    const dPonta = porPosto ? (m.d_med_ponta as number) : (m.d_med_unica ?? 0);
    const dFora = porPosto ? (m.d_med_fora_ponta as number) : (m.d_med_unica ?? 0);
    return {
      data: m.data_referencia,
      rotulo: rotuloMes(m.data_referencia),
      ePontaKwh: m.e_ponta_kwh,
      eForaKwh: m.e_fora_ponta_kwh,
      dVerde: porPosto ? Math.max(dPonta, dFora) : (m.d_med_unica ?? 0),
      dPonta,
      dFora,
      pontaInformada: porPosto,
    };
  });
}

/** Pedido de /fatura de um mês, no formato do planejamento. */
export function pedidoMes(
  form: InvoiceFormData,
  mes: MesBase,
  mod: ModSerie,
  contrato: Contrato,
  aplicarTributos = true,
): { corpo: Record<string, unknown>; params: Record<string, string> } {
  const corpo: Record<string, unknown> = {
    distribuidora: form.distribuidora,
    subgrupo: form.subgrupo,
    classe: NAO_SE_APLICA,
    detalhe: NAO_SE_APLICA,
    atividade: form.atividade,
    tipo_ligacao: form.tipoLigacao,
    data_referencia: mes.data,
    consumo_ponta_kwh: mes.ePontaKwh,
    consumo_fora_ponta_kwh: mes.eForaKwh,
    consumo_intermediario_kwh: 0,
    percentual_mes_anterior: 0,
    bandeira_adicional_r_kwh: 0, // 0 = bandeira da competência (API)
  };
  if (mod === 'Verde') {
    corpo.demanda_medida_unica_kw = mes.dVerde;
    if (contrato && 'unica' in contrato) corpo.demanda_contratada_unica_kw = contrato.unica;
  } else {
    corpo.demanda_ponta_kw = mes.dPonta;
    corpo.demanda_fora_ponta_kw = mes.dFora;
    if (contrato && 'ponta' in contrato) {
      corpo.demanda_contratada_ponta_kw = contrato.ponta;
      corpo.demanda_contratada_fora_ponta_kw = contrato.fora;
    }
  }
  const params: Record<string, string> = {
    modalidade: mod,
    base_tarifaria: BASE_TARIFARIA,
    aplicar_tributos: String(aplicarTributos),
    pis: String(num(form.pis) / 100),
    cofins: String(num(form.cofins) / 100),
    icms: String(num(form.icms) / 100),
    tipo_icms: form.tipoIcms,
    reativos_direto: 'false',
    arredondar_centavos: 'false',
    tributar_reativos: String(form.tributarReativos),
    demanda_isenta_icms: String(form.demandaIsentaIcmsAtiva),
  };
  return { corpo, params };
}

export interface SerieModalidade {
  modalidade: ModSerie;
  contratoAtual: Contrato;
  contratoOtimo: Contrato;
  /** Custo mensal (R$) com o contrato atual; null = a API falhou no mês. */
  atual: (number | null)[];
  /** Custo mensal (R$) com a DC ótima do planejamento. */
  otima: (number | null)[];
  /** Faturas da DC ótima, com e sem tributos (composição, ultrapassagem). */
  otimaFaturas: (FaturaApi | null)[];
  otimaSem: (FaturaApi | null)[];
}

export interface ConferenciaSerie {
  modalidade: ModSerie;
  cenario: 'atual' | 'otima';
  soma: number;
  planejamento: number;
  diferenca: number;
  /** |diferença| ≤ R$ 1 e nenhum mês faltando. */
  ok: boolean;
  mesesFaltando: number;
}

export interface ResultadoSeries {
  base: MesBase[];
  series: SerieModalidade[];
  conferencias: ConferenciaSerie[];
  erros: string[];
}

export const TOLERANCIA_SOMA = 1.0;

const soma = (v: (number | null)[]) => v.reduce<number>((a, x) => a + (x ?? 0), 0);

/** Confere a soma dos meses com o total do /planejamento. */
export function conferirSoma(
  modalidade: ModSerie,
  cenario: 'atual' | 'otima',
  valores: (number | null)[],
  planejamento: number,
): ConferenciaSerie {
  const s = soma(valores);
  const faltando = valores.filter((v) => v === null).length;
  const diferenca = s - planejamento;
  return {
    modalidade,
    cenario,
    soma: s,
    planejamento,
    diferenca,
    ok: faltando === 0 && Math.abs(diferenca) <= TOLERANCIA_SOMA,
    mesesFaltando: faltando,
  };
}

/**
 * Séries Verde × Azul mês a mês: até 12 meses × 2 modalidades × 2 cenários
 * (+ a DC ótima sem tributos, para a composição). Limite de 6 chamadas
 * simultâneas, com progresso.
 */
export async function calcularSeries(
  form: InvoiceFormData,
  plano: PlanejamentoApi,
  meses: MesHistorico[],
  aoProgredir?: (feitas: number, total: number) => void,
): Promise<ResultadoSeries> {
  const base = mesesBase(meses);
  const mods = plano.modalidades.filter(
    (m): m is typeof m & { modalidade: ModSerie } => m.modalidade === 'Verde' || m.modalidade === 'Azul',
  );
  const series: SerieModalidade[] = mods.map((m) => ({
    modalidade: m.modalidade,
    contratoAtual: contratoDoPlanejamento(m.dc_atual),
    contratoOtimo: contratoDoPlanejamento(m.dc_otima),
    atual: base.map(() => null),
    otima: base.map(() => null),
    otimaFaturas: base.map(() => null),
    otimaSem: base.map(() => null),
  }));

  type Alvo = { s: SerieModalidade; i: number; tipo: 'atual' | 'otima' | 'sem' };
  const alvos: Alvo[] = [];
  for (const s of series) {
    base.forEach((_, i) => {
      alvos.push({ s, i, tipo: 'atual' }, { s, i, tipo: 'otima' }, { s, i, tipo: 'sem' });
    });
  }
  const resultados = await executarComLimite(
    alvos.map(({ s, i, tipo }) => () => {
      const contrato = tipo === 'atual' ? s.contratoAtual : s.contratoOtimo;
      const p = pedidoMes(form, base[i], s.modalidade, contrato, tipo !== 'sem');
      return postFatura(p.corpo, p.params);
    }),
    6,
    aoProgredir,
  );

  const erros: string[] = [];
  resultados.forEach((r, k) => {
    const { s, i, tipo } = alvos[k];
    if (!r.ok) {
      const msg = `${s.modalidade} ${base[i].rotulo}: ${mensagemErro(r.erro)}`;
      if (!erros.includes(msg)) erros.push(msg);
      return;
    }
    const f = r.valor.fatura;
    if (tipo === 'atual') s.atual[i] = f.custo_total;
    else if (tipo === 'otima') {
      s.otima[i] = f.custo_total;
      s.otimaFaturas[i] = f;
    } else s.otimaSem[i] = f;
  });

  const conferencias: ConferenciaSerie[] = [];
  for (const s of series) {
    const p = mods.find((m) => m.modalidade === s.modalidade)!;
    conferencias.push(conferirSoma(s.modalidade, 'atual', s.atual, p.custo_contrato_atual));
    conferencias.push(conferirSoma(s.modalidade, 'otima', s.otima, p.custo_demanda_otimizada));
  }
  return { base, series, conferencias, erros };
}

/** Meses com ultrapassagem cobrada na fatura da DC ótima (linhas da API). */
export function mesesComUltrapassagem(faturas: (FaturaApi | null)[]): boolean[] {
  return faturas.map(
    (f) => !!f && f.linhas.some((l) => l.categoria === 'ULTRAPASSAGEM' && l.custo > 0.005),
  );
}

/* ------------------------------------------------------------------ */
/* Curva "Qual demanda contratar?" (B6)                                */
/* ------------------------------------------------------------------ */

/**
 * 12 a 15 valores de DC entre 30 kW e 1,3 × a maior demanda medida,
 * sempre incluindo a DC ótima (e a atual, se couber no intervalo).
 */
export function pontosCurva(dMax: number, dcOtima: number, dcAtual: number | null = null, n = 13): number[] {
  const min = 30;
  const max = Math.max(min + 12, Math.ceil(1.3 * dMax));
  const passo = (max - min) / (n - 1);
  const set = new Set<number>();
  for (let k = 0; k < n; k += 1) set.add(Math.round(min + k * passo));
  set.add(Math.round(dcOtima));
  if (dcAtual !== null && dcAtual >= min && dcAtual <= max) set.add(Math.round(dcAtual));
  let pts = [...set].sort((a, b) => a - b);
  // Limite de 15: retira pontos intermediários longe da ótima/atual.
  while (pts.length > 15) {
    const fixos = new Set([Math.round(dcOtima), dcAtual === null ? -1 : Math.round(dcAtual), pts[0], pts[pts.length - 1]]);
    const i = pts.findIndex((p, j) => j > 0 && !fixos.has(p));
    pts = pts.filter((_, j) => j !== i);
  }
  return pts;
}

export interface PontoCurva {
  dc: number;
  /** Soma das faturas mensais da API; null = algum mês falhou. */
  custo: number | null;
}

/**
 * Custo do período para cada DC (modalidade atual). Na Azul varia a DC fora
 * de ponta com a ponta fixa na ótima. `cache` evita repetir chamadas.
 */
export async function calcularCurva(
  form: InvoiceFormData,
  base: MesBase[],
  mod: ModSerie,
  pontos: number[],
  pontaFixa: number | null,
  cache: Map<string, number | null>,
  aoProgredir?: (feitas: number, total: number) => void,
): Promise<PontoCurva[]> {
  const chave = (dc: number, i: number) => `${mod}|${pontaFixa ?? '-'}|${dc}|${base[i].data}`;
  const faltam: { dc: number; i: number }[] = [];
  for (const dc of pontos) base.forEach((_, i) => {
    if (!cache.has(chave(dc, i))) faltam.push({ dc, i });
  });
  const rs = await executarComLimite(
    faltam.map(({ dc, i }) => () => {
      const contrato: Contrato = mod === 'Verde' ? { unica: dc } : { ponta: pontaFixa ?? dc, fora: dc };
      const p = pedidoMes(form, base[i], mod, contrato, true);
      return postFatura(p.corpo, p.params);
    }),
    6,
    aoProgredir,
  );
  rs.forEach((r, k) => cache.set(chave(faltam[k].dc, faltam[k].i), r.ok ? r.valor.fatura.custo_total : null));
  return pontos.map((dc) => {
    const vs = base.map((_, i) => cache.get(chave(dc, i)) ?? null);
    return { dc, custo: vs.some((v) => v === null) ? null : soma(vs) };
  });
}

/**
 * Faixa de DC cujo custo fica até +0,5% do mínimo amostrado. As bordas são
 * interpoladas linearmente entre os pontos vizinhos (aproximação visual).
 */
export function faixaBoa(pontos: PontoCurva[], tolerancia = 0.005): [number, number] | null {
  const v = pontos.filter((p): p is { dc: number; custo: number } => p.custo !== null).sort((a, b) => a.dc - b.dc);
  if (v.length === 0) return null;
  const min = Math.min(...v.map((p) => p.custo));
  const lim = min * (1 + tolerancia);
  const bons = v.map((p, i) => ({ ...p, i })).filter((p) => p.custo <= lim);
  const iIni = bons[0].i;
  const iFim = bons[bons.length - 1].i;
  const cruza = (a: { dc: number; custo: number }, b: { dc: number; custo: number }) =>
    a.custo === b.custo ? a.dc : a.dc + ((lim - a.custo) / (b.custo - a.custo)) * (b.dc - a.dc);
  const de = iIni > 0 ? cruza(v[iIni], v[iIni - 1]) : v[iIni].dc;
  const ate = iFim < v.length - 1 ? cruza(v[iFim], v[iFim + 1]) : v[iFim].dc;
  return [Math.round(Math.min(de, ate)), Math.round(Math.max(de, ate))];
}

/* ------------------------------------------------------------------ */
/* Indicadores (B8) — não são tarifa                                   */
/* ------------------------------------------------------------------ */

export function horasDoMes(iso: string): number {
  const ano = Number(iso.slice(0, 4));
  const mes = Number(iso.slice(5, 7));
  return new Date(ano, mes, 0).getDate() * 24;
}

/** Uso da ponta (h/mês) = energia ponta ÷ demanda ponta; null sem demanda de ponta medida. */
export function usoPontaHoras(m: MesBase): number | null {
  if (!m.pontaInformada || m.dPonta <= 0) return null;
  return m.ePontaKwh / m.dPonta;
}

/** Fator de carga = energia ÷ (demanda máxima × horas do mês). */
export function fatorCarga(m: MesBase): number | null {
  const dMax = Math.max(m.dVerde, m.dPonta, m.dFora);
  if (dMax <= 0) return null;
  return (m.ePontaKwh + m.eForaKwh) / (dMax * horasDoMes(m.data));
}

export function media(v: (number | null)[]): number | null {
  const ok = v.filter((x): x is number => x !== null && Number.isFinite(x));
  return ok.length ? ok.reduce((a, x) => a + x, 0) / ok.length : null;
}
