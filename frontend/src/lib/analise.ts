/**
 * Orquestra as chamadas da análise (etapas 2 e 3). Toda cifra vem da API;
 * aqui só se decide o que pedir e como agrupar as respostas.
 */
import {
  BandeiraOpcao,
  EpiResultadoApi,
  MesHistorico,
  NotaApi,
  PlanejamentoApi,
  calcularEpi,
  compararModalidades,
  compararPlanejamento,
  corpoEpi,
  mensagemErro,
} from './api';
import {
  Contrato,
  FaturaModalidade,
  ModApi,
  calcularFaturaModalidade,
  contratoAtualForm,
  contratoDoPlanejamento,
  ehHipotetica,
  seloHipotetico,
  modalidadeAtualApi,
  modalidadesCandidatas,
  motivoNaoAvaliada,
} from './cenarios';
import { montarMesesPlanejamento, optanteBInformado, premissasDeEntrada } from './validacao';
import type { InvoiceFormData } from '../types/energy';

export type EstadoModalidade = 'ok' | 'indisponivel' | 'nao_avaliado';

export interface ModalidadeAnalise {
  modalidade: ModApi;
  estado: EstadoModalidade;
  motivo: string | null;
  hipotetica: boolean;
  /** Texto do selo "hipotético" (B2/B11); null = modalidade da unidade. */
  selo: string | null;
  contratoAtual: Contrato;
  contratoOtimo: Contrato;
  atual: FaturaModalidade | null;
  /** Fatura com a DC ótima do /planejamento (null sem planejamento). */
  otima: FaturaModalidade | null;
}

export interface EpiAnalise {
  modalidade: string | null;
  simplificado: EpiResultadoApi | null;
  comCustos: EpiResultadoApi | null;
  /** Mensagem da API quando o E-PI não pôde ser calculado. */
  erro: string | null;
  /** Corpo enviado (para diagnóstico quando a API recusa). */
  corpo: Record<string, unknown> | null;
}

/**
 * Conferência com a conta (B13). Retenções/créditos só entram aqui:
 * líquido = recalculado − retenções; Δ = líquido − total impresso.
 * O custo da unidade continua sendo o recalculado.
 */
export interface Conferencia {
  totalFatura: number;
  totalCalculado: number;
  retencoes: number | null;
  liquido: number;
  diferenca: number;
  /** Reativo informado, mas a API não gerou linha de excedente (art. 304). */
  reativoNaoCobrado: boolean;
}

export function conferir(form: InvoiceFormData, fatura: FaturaModalidade): Conferencia | null {
  const total = form.totalFatura;
  if (total === null || !(total > 0)) return null;
  const ret = form.retencoesCreditos !== null && form.retencoesCreditos > 0 ? form.retencoesCreditos : null;
  const liquido = fatura.total - (ret ?? 0);
  const reativoInformado =
    form.consumoReativoPonta + form.consumoReativoForaPonta + form.demandaReativaPonta + form.demandaReativaForaPonta +
      form.reativoEnergiaCapacitiva + form.reativoDemandaCapacitiva > 0;
  return {
    totalFatura: total,
    totalCalculado: fatura.total,
    retencoes: ret,
    liquido,
    diferenca: Number((liquido - total).toFixed(2)),
    reativoNaoCobrado: reativoInformado && !fatura.com.linhas.some((l) => l.categoria === 'REATIVOS' && l.custo > 0.005),
  };
}

/**
 * B10: a recomendação do mês nunca custa mais do que a modalidade atual.
 * Devolve a modalidade mais barata e a economia, ou null se a atual já é a
 * mais barata (ou empata).
 */
export function recomendacaoMes(a: Pick<Analise, 'modalidades' | 'modalidadeAtual' | 'faturaAtual'>): { modalidade: ModApi; economia: number } | null {
  const custoAtual = a.faturaAtual.total;
  const melhor = a.modalidades
    .filter((m) => m.estado === 'ok' && m.atual && m.modalidade !== a.modalidadeAtual)
    .sort((x, y) => x.atual!.total - y.atual!.total)[0];
  if (!melhor || melhor.atual!.total >= custoAtual - 0.005) return null;
  return { modalidade: melhor.modalidade, economia: custoAtual - melhor.atual!.total };
}

export interface Analise {
  form: InvoiceFormData;
  modalidadeAtual: ModApi;
  modalidades: ModalidadeAnalise[];
  notas: NotaApi[];
  faturaAtual: FaturaModalidade;
  conferencia: Conferencia | null;
  /** B7: E-PI da modalidade recomendada, quando diferente da atual. */
  epiRecomendada: EpiAnalise | null;
  planejamento: PlanejamentoApi | null;
  planejamentoErro: string | null;
  mesesPlanejamento: MesHistorico[];
  avisosPlanejamento: string[];
  periodo: string;
  epi: EpiAnalise;
  premissas: string[];
  optanteBAvaliado: boolean;
}

const EPI_SUPORTADAS = new Set(['Verde', 'Azul', 'Optante B']);

/** Escolhe a modalidade de referência do E-PI: a melhor opção no cativo. */
export function modalidadeDoEpi(
  modalidades: ModalidadeAnalise[],
  plano: PlanejamentoApi | null,
  atual: ModApi,
): string | null {
  if (plano && EPI_SUPORTADAS.has(plano.melhor_demanda_otimizada)) return plano.melhor_demanda_otimizada;
  const ok = modalidades
    .filter((m) => m.estado === 'ok' && m.atual && EPI_SUPORTADAS.has(m.modalidade))
    .sort((a, b) => a.atual!.total - b.atual!.total);
  const custoAtual = modalidades.find((m) => m.modalidade === atual)?.atual?.total;
  // B10: só troca de referência se for mais barata que a atual.
  if (ok.length && custoAtual !== undefined && ok[0].atual!.total < custoAtual - 0.005) return ok[0].modalidade;
  return EPI_SUPORTADAS.has(atual) ? atual : null;
}

export async function calcularEpiAnalise(form: InvoiceFormData, modalidade: string | null): Promise<EpiAnalise> {
  if (!modalidade) {
    return {
      modalidade: null,
      simplificado: null,
      comCustos: null,
      erro: 'O E-PI é calculado para as modalidades do Grupo A (Verde, Azul ou Optante B).',
      corpo: null,
    };
  }
  const comCustos = (form.opexMensal || 0) > 0 || (form.capex || 0) > 0;
  const corpo = corpoEpi(form, { modalidade, comCustos: false });
  const [s, c] = await Promise.allSettled([
    calcularEpi(form, { modalidade, comCustos: false }),
    comCustos ? calcularEpi(form, { modalidade, comCustos: true }) : Promise.resolve(null),
  ]);
  return {
    modalidade,
    simplificado: s.status === 'fulfilled' ? s.value : null,
    comCustos: c.status === 'fulfilled' ? c.value : null,
    erro: s.status === 'rejected' ? mensagemErro(s.reason) : c.status === 'rejected' ? mensagemErro(c.reason) : null,
    corpo,
  };
}

/**
 * Executa a análise. Lança erro (com a mensagem da API) se a fatura da
 * modalidade atual não puder ser calculada — sem ela não há relatório.
 */
export async function executarAnalise(
  form: InvoiceFormData,
  bandeiras: BandeiraOpcao[] | null,
): Promise<Analise> {
  const atual = modalidadeAtualApi(form);
  const candidatas = modalidadesCandidatas(form);
  const { meses, avisos, periodo } = montarMesesPlanejamento(form);
  const grupoAContrato = form.modalidadeAtual === 'verde' || form.modalidadeAtual === 'azul';

  const naoAvaliada = new Map(candidatas.map((m) => [m, motivoNaoAvaliada(form, m)]));
  const [respComparar, respPlano, ...respFaturas] = await Promise.allSettled([
    candidatas.length > 1 ? compararModalidades(form, bandeiras) : Promise.resolve(null),
    grupoAContrato && meses.length > 0 ? compararPlanejamento(form, meses) : Promise.resolve(null),
    ...candidatas.map((m) =>
      naoAvaliada.get(m) ? Promise.resolve(null) : calcularFaturaModalidade(form, m, 'atual', null, bandeiras),
    ),
  ]);

  const iAtual = candidatas.indexOf(atual);
  const rAtual = respFaturas[iAtual];
  if (rAtual.status === 'rejected') throw rAtual.reason;
  const faturaAtual = rAtual.value as FaturaModalidade;

  const comparar = respComparar.status === 'fulfilled' ? respComparar.value : null;
  const plano = respPlano.status === 'fulfilled' ? respPlano.value : null;
  const planejamentoErro = respPlano.status === 'rejected' ? mensagemErro(respPlano.reason) : null;

  const modalidades: ModalidadeAnalise[] = candidatas.map((m, i) => {
    const r = respFaturas[i];
    const indisp = comparar?.comparacao.indisponiveis.find((x) => x.modalidade === m);
    const base = {
      modalidade: m,
      hipotetica: ehHipotetica(form, m),
      selo: seloHipotetico(form, m),
      contratoAtual: contratoAtualForm(form, m),
      contratoOtimo: contratoDoPlanejamento(plano?.modalidades.find((x) => x.modalidade === m)?.dc_otima),
      otima: null,
    };
    const motivoNA = naoAvaliada.get(m);
    if (motivoNA) return { ...base, estado: 'nao_avaliado', motivo: motivoNA, atual: null };
    if (m !== atual && indisp) return { ...base, estado: 'indisponivel', motivo: indisp.motivo, atual: null };
    if (r.status === 'rejected') {
      return { ...base, estado: 'indisponivel', motivo: mensagemErro(r.reason), atual: null };
    }
    return { ...base, estado: 'ok', motivo: null, atual: r.value as FaturaModalidade };
  });

  // Faturas com a DC ótima do planejamento (Verde/Azul); Optante B não tem DC.
  if (plano) {
    await Promise.all(
      modalidades.map(async (m) => {
        if (m.estado !== 'ok') return;
        if (m.modalidade === 'Optante B') {
          m.otima = m.atual;
          return;
        }
        if (!m.contratoOtimo) return;
        try {
          m.otima = await calcularFaturaModalidade(form, m.modalidade, 'otima', m.contratoOtimo, bandeiras);
        } catch {
          m.otima = null;
        }
      }),
    );
  }

  // B7: E-PI sempre com a modalidade explícita — a atual; e a recomendada, se for outra.
  const recomendada = modalidadeDoEpi(modalidades, plano, atual);
  const [epi, epiRecomendada] = await Promise.all([
    calcularEpiAnalise(form, EPI_SUPORTADAS.has(atual) ? atual : null),
    recomendada && recomendada !== atual ? calcularEpiAnalise(form, recomendada) : Promise.resolve(null),
  ]);

  return {
    form,
    modalidadeAtual: atual,
    modalidades,
    notas: [...faturaAtual.notas, ...(comparar?.notas ?? [])],
    faturaAtual,
    conferencia: conferir(form, faturaAtual),
    planejamento: plano,
    planejamentoErro,
    mesesPlanejamento: meses,
    avisosPlanejamento: avisos,
    periodo,
    epi,
    epiRecomendada,
    premissas: premissasDeEntrada(form),
    optanteBAvaliado: optanteBInformado(form) || form.modalidadeAtual === 'optante_b',
  };
}
