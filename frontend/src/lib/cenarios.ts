/**
 * Faturas por modalidade e cenário, sempre via POST /api/calculo/fatura.
 *
 * B1 — /api/calculo/comparar não recebe demanda isenta de ICMS, tributar
 *      reativos nem arredondamento; por isso os TOTAIS de cada modalidade vêm
 *      de /fatura (mesmos flags da fatura da etapa 2). /comparar só informa
 *      as modalidades indisponíveis e o motivo.
 * B2 — Azul para unidade Verde: demanda medida única nos dois postos e a
 *      contratada única nas duas contratadas (premissa D6) → "hipotético".
 * B3 — Coluna "Tarifa ANEEL (sem tributos)": segunda chamada com
 *      aplicar_tributos=false; as linhas são casadas pela descrição.
 *
 * O front não calcula tarifa: só monta o pedido, casa linhas e soma.
 */
import { num } from './numeros';
import {
  BandeiraOpcao,
  FaturaApi,
  FaturaResponseApi,
  NotaApi,
  paraConsumidor,
  postFatura,
  queryParamsFatura,
} from './api';
import { ComponenteCusto, chaveLinha, rotuloLinha } from './rotulos';
import type { InvoiceFormData, TariffModalidade } from '../types/energy';

export type ModApi = 'Verde' | 'Azul' | 'Optante B' | 'Branca' | 'Convencional Monômia';
export type Cenario = 'atual' | 'otima';

export const MOD_API: Record<TariffModalidade, ModApi> = {
  verde: 'Verde',
  azul: 'Azul',
  optante_b: 'Optante B',
  branca: 'Branca',
  convencional: 'Convencional Monômia',
};

/** Demanda contratada de um cenário (Verde: única; Azul: ponta/fora). */
export type Contrato = { unica: number } | { ponta: number; fora: number } | null;

export const modalidadeAtualApi = (form: InvoiceFormData): ModApi => MOD_API[form.modalidadeAtual];

const grupoAForm = (form: InvoiceFormData) => form.subgrupo.trim().toUpperCase().startsWith('A');

/** Modalidades a mostrar: Grupo A → Verde, Azul e Optante B; Grupo B → só a atual. */
export function modalidadesCandidatas(form: InvoiceFormData): ModApi[] {
  if (!grupoAForm(form)) return [modalidadeAtualApi(form)];
  return ['Verde', 'Azul', 'Optante B'];
}

/** A modalidade é simulada sem contrato real (ex.: Azul para unidade Verde)? */
export function ehHipotetica(form: InvoiceFormData, mod: ModApi): boolean {
  if (mod === 'Azul') return form.modalidadeAtual === 'verde';
  if (mod === 'Verde') return form.modalidadeAtual === 'azul';
  return false;
}

export const SELO_HIPOTETICO: Partial<Record<ModApi, string>> = {
  Azul: 'hipotético: a unidade não tem contrato Azul',
  Verde: 'hipotético: a unidade não tem contrato Verde',
};

/**
 * A modalidade pode ser calculada com o que o usuário informou?
 * Devolve o motivo quando não pode (ex.: Optante B sem kVA = "não avaliado").
 */
export function motivoNaoAvaliada(form: InvoiceFormData, mod: ModApi): string | null {
  const atual = modalidadeAtualApi(form);
  if (mod === atual) return null;
  if (mod === 'Optante B') {
    const informou =
      form.potenciaTransformadoresKva !== null ||
      form.hotelariaTurismo ||
      (form.cargaRefletoresKw > 0 && form.cargaInstaladaTotalKw > 0);
    return informou ? null : 'não avaliado: informe a potência dos transformadores (kVA) na etapa 1';
  }
  if ((mod === 'Verde' || mod === 'Azul') && atual === 'Optante B') {
    return 'não avaliado: a unidade Optante B não informou demanda medida/contratada';
  }
  return null;
}

/** Corpo + parâmetros de /fatura para a modalidade e o contrato do cenário. */
export function pedidoFatura(
  form: InvoiceFormData,
  mod: ModApi,
  contrato: Contrato,
  aplicarTributos: boolean,
  bandeiras?: BandeiraOpcao[] | null,
): { corpo: Record<string, unknown>; params: Record<string, string> } {
  const corpo = paraConsumidor(form, bandeiras);
  const params = queryParamsFatura(form, form.modalidadeAtual);
  params.modalidade = mod;
  params.aplicar_tributos = String(aplicarTributos);
  const atual = modalidadeAtualApi(form);

  if (mod === 'Azul' && atual === 'Verde') {
    // B2 / premissa D6: medida única nos dois postos; contratada única nas duas.
    corpo.demanda_ponta_kw = num(form.demandaMedida);
    corpo.demanda_fora_ponta_kw = num(form.demandaMedida);
    corpo.demanda_contratada_ponta_kw = num(form.demandaContratada);
    corpo.demanda_contratada_fora_ponta_kw = num(form.demandaContratada);
  }
  if (mod === 'Verde' && atual === 'Azul') {
    // Verde para unidade Azul: medida = maior entre os postos; contratada = maior contratada.
    corpo.demanda_medida_unica_kw = Math.max(num(form.demandaPontaKw), num(form.demandaForaPontaKw));
    corpo.demanda_contratada_unica_kw = Math.max(
      num(form.demandaContratadaPontaKw),
      num(form.demandaContratadaForaPontaKw),
    );
  }
  if (contrato) {
    if ('unica' in contrato) corpo.demanda_contratada_unica_kw = contrato.unica;
    else {
      corpo.demanda_contratada_ponta_kw = contrato.ponta;
      corpo.demanda_contratada_fora_ponta_kw = contrato.fora;
    }
  }
  // A quantidade isenta digitada vale só para a fatura real (modalidade e
  // contrato atuais); nos demais cenários a API calcula contratada − medida.
  if (mod !== atual || contrato) delete params.demanda_isenta_icms_kw;
  return { corpo, params };
}

/* ------------------------------------------------------------------ */
/* Linhas detalhadas (B3/B4)                                           */
/* ------------------------------------------------------------------ */

export interface LinhaDetalhada {
  descricao: string;
  rotulo: string;
  unidade: string;
  componente: ComponenteCusto;
  quantidade: number;
  /** Tarifa ANEEL sem tributos (da chamada aplicar_tributos=false); null = sem par. */
  tarifaSem: number | null;
  /** Preço com tributos (tarifa da linha com tributos). */
  tarifaCom: number;
  pisCofins: number;
  icms: number;
  /** Valor da linha (R$), como a API devolveu. */
  valor: number;
  /** Valor sem tributos (R$); null = sem par. */
  valorSem: number | null;
  isentaIcms: boolean;
}

/**
 * Casa as linhas com e sem tributos pela descrição (sem o sufixo
 * " (com tributos)"), respeitando a ordem de linhas repetidas.
 * Tributo da linha = valor com − valor sem (ambos da API); o ICMS é a
 * alíquota sobre o valor com tributos (0 na parcela isenta) e PIS/COFINS
 * o restante.
 */
export function detalharLinhas(
  com: FaturaApi,
  sem: FaturaApi | null,
  form: InvoiceFormData,
): LinhaDetalhada[] {
  const fila = new Map<string, FaturaApi['linhas']>();
  for (const l of sem?.linhas ?? []) {
    const k = chaveLinha(l.descricao);
    fila.set(k, [...(fila.get(k) ?? []), l]);
  }
  const icmsFrac = num(form.icms) / 100;
  return com.linhas.map((l) => {
    const r = rotuloLinha(l.descricao, com.modalidade, l.categoria);
    const par = fila.get(r.chave)?.shift() ?? null;
    const valorSem = com.aplicar_tributos ? (par ? par.custo : null) : l.custo;
    const tributo = valorSem === null ? 0 : Math.max(0, l.custo - valorSem);
    const icms = r.isentaIcms || tributo <= 0.005 ? 0 : Math.min(tributo, l.custo * icmsFrac);
    return {
      descricao: l.descricao,
      rotulo: r.rotulo,
      unidade: r.unidade,
      componente: r.componente,
      quantidade: l.quantidade,
      tarifaSem: com.aplicar_tributos ? (par ? par.tarifa : null) : l.tarifa,
      tarifaCom: l.tarifa,
      pisCofins: tributo - icms,
      icms,
      valor: l.custo,
      valorSem,
      isentaIcms: r.isentaIcms,
    };
  });
}

export interface ResumoTributos {
  base: number;
  icms: number;
  pis: number;
  cofins: number;
}

export function resumoTributos(linhas: LinhaDetalhada[], form: InvoiceFormData): ResumoTributos {
  const tributadas = linhas.filter((l) => l.pisCofins + l.icms > 0.005);
  const pc = tributadas.reduce((a, l) => a + l.pisCofins, 0);
  const pis = num(form.pis);
  const cofins = num(form.cofins);
  const fPis = pis + cofins > 0 ? pis / (pis + cofins) : 0;
  return {
    base: tributadas.reduce((a, l) => a + l.valor, 0),
    icms: tributadas.reduce((a, l) => a + l.icms, 0),
    pis: pc * fPis,
    cofins: pc * (1 - fPis),
  };
}

export interface Composicao {
  TE: number;
  Demanda: number;
  Fio: number;
  Tributos: number;
  Outros: number;
}

export const composicaoVazia = (): Composicao => ({ TE: 0, Demanda: 0, Fio: 0, Tributos: 0, Outros: 0 });

/** Composição do custo: componentes sem tributos + tributos (soma = total da API). */
export function composicaoDe(linhas: LinhaDetalhada[], acc: Composicao = composicaoVazia()): Composicao {
  for (const l of linhas) {
    const liquido = l.valorSem ?? l.valor;
    acc[l.componente] += liquido;
    acc.Tributos += l.valor - liquido;
  }
  return acc;
}

/* ------------------------------------------------------------------ */
/* Fatura de uma modalidade (com e sem tributos)                       */
/* ------------------------------------------------------------------ */

export interface FaturaModalidade {
  modalidade: ModApi;
  cenario: Cenario;
  contrato: Contrato;
  com: FaturaApi;
  sem: FaturaApi | null;
  notas: NotaApi[];
  linhas: LinhaDetalhada[];
  total: number;
  hipotetica: boolean;
}

export async function calcularFaturaModalidade(
  form: InvoiceFormData,
  mod: ModApi,
  cenario: Cenario,
  contrato: Contrato,
  bandeiras?: BandeiraOpcao[] | null,
): Promise<FaturaModalidade> {
  const pCom = pedidoFatura(form, mod, contrato, form.aplicarTributos, bandeiras);
  const chamadas: Promise<FaturaResponseApi>[] = [postFatura(pCom.corpo, pCom.params)];
  if (form.aplicarTributos) {
    const pSem = pedidoFatura(form, mod, contrato, false, bandeiras);
    chamadas.push(postFatura(pSem.corpo, pSem.params));
  }
  const [respCom, respSem] = await Promise.all(chamadas);
  return {
    modalidade: mod,
    cenario,
    contrato,
    com: respCom.fatura,
    sem: respSem ? respSem.fatura : null,
    notas: respCom.notas,
    linhas: detalharLinhas(respCom.fatura, respSem ? respSem.fatura : null, form),
    total: respCom.fatura.custo_total,
    hipotetica: ehHipotetica(form, mod),
  };
}

/** Contrato ótimo de uma modalidade a partir do `dc_otima` do /planejamento. */
export function contratoDoPlanejamento(dc: number | [number, number] | null | undefined): Contrato {
  if (dc === null || dc === undefined) return null;
  if (Array.isArray(dc)) return { ponta: dc[0], fora: dc[1] };
  return dc > 0 ? { unica: dc } : null;
}

/** Texto curto do contrato ("201 kW" / "194 / 204 kW"). */
export function textoContrato(c: Contrato, fmt: (n: number) => string): string {
  if (!c) return '—';
  if ('unica' in c) return `${fmt(c.unica)} kW`;
  return `${fmt(c.ponta)} / ${fmt(c.fora)} kW`;
}

/** Contrato atual informado no formulário (para a modalidade pedida). */
export function contratoAtualForm(form: InvoiceFormData, mod: ModApi): Contrato {
  const atual = modalidadeAtualApi(form);
  if (mod === 'Verde') {
    if (atual === 'Azul')
      return { unica: Math.max(num(form.demandaContratadaPontaKw), num(form.demandaContratadaForaPontaKw)) };
    return { unica: num(form.demandaContratada) };
  }
  if (mod === 'Azul') {
    if (atual === 'Verde') return { ponta: num(form.demandaContratada), fora: num(form.demandaContratada) };
    return { ponta: num(form.demandaContratadaPontaKw), fora: num(form.demandaContratadaForaPontaKw) };
  }
  return null;
}
