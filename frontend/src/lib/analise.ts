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

export interface Analise {
  form: InvoiceFormData;
  modalidadeAtual: ModApi;
  modalidades: ModalidadeAnalise[];
  notas: NotaApi[];
  faturaAtual: FaturaModalidade;
  conferencia: { totalFatura: number; totalCalculado: number; diferenca: number } | null;
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
  if (ok.length) return ok[0].modalidade;
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

  const epi = await calcularEpiAnalise(form, modalidadeDoEpi(modalidades, plano, atual));

  const totalFatura = form.totalFatura;
  return {
    form,
    modalidadeAtual: atual,
    modalidades,
    notas: [...faturaAtual.notas, ...(comparar?.notas ?? [])],
    faturaAtual,
    conferencia:
      totalFatura !== null && totalFatura > 0
        ? {
            totalFatura,
            totalCalculado: faturaAtual.total,
            diferenca: Number((faturaAtual.total - totalFatura).toFixed(2)),
          }
        : null,
    planejamento: plano,
    planejamentoErro,
    mesesPlanejamento: meses,
    avisosPlanejamento: avisos,
    periodo,
    epi,
    premissas: premissasDeEntrada(form),
    optanteBAvaliado: optanteBInformado(form) || form.modalidadeAtual === 'optante_b',
  };
}
