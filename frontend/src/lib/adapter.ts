/**
 * Adapters: resposta da API (schemas/fatura.py) → tipos de exibição do front.
 *
 * As categorias do motor (TARIFA/ULTRAPASSAGEM/REATIVOS/BANDEIRA/ENCARGO/
 * OUTROS) são traduzidas para as categorias visuais do relatório; os campos
 * do mercado livre usam o E-PI calculado pela API (POST /api/epi/calcular);
 * o front não estima nenhum valor tarifário por conta própria.
 */
import type {
  AuditResult,
  EpiResumo,
  InvoiceFormData,
  PlanejamentoResumo,
  ModalidadeTeTusd,
  TableItemBreakdown,
  TariffModalidade,
} from '../types/energy';
import type {
  ComparacaoResponseApi,
  EpiResultadoApi,
  FaturaApi,
  PlanejamentoApi,
  FaturaResponseApi,
  LinhaFaturaApi,
} from './api';
import { formatCurrency, formatNumber } from '../utils/calculator';

export type CategoriaExibicao = 'TE' | 'TUSD' | 'Demanda' | 'Tributos' | 'Bandeira' | 'Outros';

/** Traduz a categoria do motor para a categoria visual do relatório. */
export function categoriaExibicao(linha: LinhaFaturaApi): CategoriaExibicao {
  const d = linha.descricao.toUpperCase();
  if (linha.categoria === 'ULTRAPASSAGEM') return 'Demanda';
  if (linha.categoria === 'REATIVOS') return 'Outros';
  if (linha.categoria === 'BANDEIRA') return 'Bandeira';
  if (linha.categoria === 'ENCARGO' || linha.categoria === 'OUTROS') return 'Outros';
  if (linha.categoria === 'TARIFA') {
    if (d.includes('DEMANDA')) return 'Demanda';
    if (d.includes('TE ')) return 'TE';
    return 'TUSD';
  }
  return 'Outros';
}

const MODALIDADE_API_PARA_FORM: Record<string, TariffModalidade> = {
  Azul: 'azul',
  Verde: 'verde',
  'Optante B': 'optante_b',
  Branca: 'branca',
  'Convencional Monômia': 'convencional',
};

export function modalidadeApiParaForm(nome: string): TariffModalidade {
  return MODALIDADE_API_PARA_FORM[nome] ?? 'verde';
}

function breakdownDeFatura(fatura: FaturaApi): TableItemBreakdown[] {
  return fatura.linhas.map((l) => ({
    descricao: l.descricao,
    subtitulo: l.categoria,
    baseConsumo: `${formatNumber(l.quantidade, 2)}`,
    tarifaSemTributo: formatCurrency(l.tarifa),
    tarifaComTributo: formatCurrency(l.tarifa),
    valorTotal: formatCurrency(l.custo),
    valorNum: l.custo,
    dotColor: 'bg-slate-400',
  }));
}

function somaPorCategoria(fatura: FaturaApi, cats: CategoriaExibicao[]): number {
  return fatura.linhas
    .filter((l) => cats.includes(categoriaExibicao(l)))
    .reduce((a, l) => a + l.custo, 0);
}

function comparativoDeFaturas(faturas: FaturaApi[]): ModalidadeTeTusd[] {
  return faturas.map((f) => {
    const te = somaPorCategoria(f, ['TE']);
    const total = f.custo_total || 1;
    return {
      key: modalidadeApiParaForm(f.modalidade),
      nome: f.modalidade,
      custoTotal: f.custo_total,
      teValor: Math.round(te * 100) / 100,
      tusdValor: Math.round((f.custo_total - te) * 100) / 100,
      tePct: Math.round((te / total) * 100),
      tusdPct: Math.round(((f.custo_total - te) / total) * 100),
      descricaoRegulatoria: f.base_tarifaria,
    };
  });
}

/** E-PI da API → resumo de exibição. */
export function adaptarEpi(epi: EpiResultadoApi, form: InvoiceFormData): EpiResumo {
  return {
    pi: epi.pi,
    modalidade: epi.modalidade,
    eMwh: epi.e_mwh,
    baseAclMwh: epi.base_acl,
    comCustosMigracao: (form.opexMensal || 0) > 0 || (form.capex || 0) > 0,
    aviso: epi.aviso,
  };
}

/**
 * Custo mensal estimado no ACL para a proposta informada, a partir do E-PI:
 * custo ACR (melhor modalidade) − (E-PI − preço) × base ACL.
 * Sem proposta (preço 0) → 0 (o relatório mostra só o E-PI).
 */
export function custoAclPorEpi(custoMelhorAcr: number, epi: EpiResumo | null, precoMwh: number): number {
  if (!epi || precoMwh <= 0) return 0;
  return Math.max(0, custoMelhorAcr - (epi.pi - precoMwh) * epi.baseAclMwh);
}

/** Planejamento anual da API → resumo de exibição. */
export function adaptarPlanejamento(p: PlanejamentoApi, meses: number): PlanejamentoResumo {
  return {
    meses,
    melhorContratoAtual: p.melhor_contrato_atual,
    melhorDemandaOtimizada: p.melhor_demanda_otimizada,
    ganhoTotal: p.ganho.total,
    ganhoDemanda: p.ganho.demanda,
    ganhoModalidade: p.ganho.modalidade,
    modalidades: p.modalidades.map((m) => ({
      modalidade: m.modalidade,
      custoContratoAtual: m.custo_contrato_atual,
      custoDemandaOtimizada: m.custo_demanda_otimizada,
      dcAtual: m.dc_atual,
      dcOtima: m.dc_otima,
      epiAnual: m.pi?.anual ?? null,
    })),
    avisos: p.avisos,
  };
}

export function adaptarFatura(fatura: FaturaApi, _form: InvoiceFormData): Partial<AuditResult> {
  const te = somaPorCategoria(fatura, ['TE']);
  const tusd = somaPorCategoria(fatura, ['TUSD']);
  const demanda = somaPorCategoria(fatura, ['Demanda']);
  const total = fatura.custo_total || 1;
  return {
    breakdown: breakdownDeFatura(fatura),
    composicao: {
      energiaPct: Math.round((te / total) * 100),
      tusdPct: Math.round(((tusd + demanda) / total) * 100),
      tributosPct: Math.round((somaPorCategoria(fatura, ['Tributos', 'Bandeira', 'Outros']) / total) * 100),
    },
    reativosTotal: somaPorCategoria(fatura, ['Outros']),
    comparativoTeTusd: comparativoDeFaturas([fatura]),
  };
}

/** Comparação da API → AuditResult completo para o relatório. */
export function adaptarComparacao(
  resp: ComparacaoResponseApi | FaturaResponseApi,
  form: InvoiceFormData,
  faturaAtual: FaturaApi,
  epi: EpiResumo | null = null,
  planejamento: PlanejamentoResumo | null = null,
): AuditResult {
  const respComparacao = 'comparacao' in resp ? resp.comparacao : null;
  const respFatura: FaturaApi = 'fatura' in resp ? resp.fatura : faturaAtual;
  const disponiveis = respComparacao ? respComparacao.disponiveis : [respFatura];
  const melhorApi = respComparacao?.melhor ?? respFatura.modalidade;

  const porNome = (nome: string) => disponiveis.find((f) => f.modalidade === nome)?.custo_total ?? 0;
  const custoAzul = porNome('Azul');
  const custoVerde = porNome('Verde');
  const custoOptanteB = porNome('Optante B');
  const custoConvencional = porNome('Convencional Monômia');
  const custoBranca = porNome('Branca');

  const melhorKey = modalidadeApiParaForm(melhorApi);
  const novoCusto = disponiveis.find((f) => f.modalidade === melhorApi)?.custo_total ?? faturaAtual.custo_total;
  const custoAtual = faturaAtual.custo_total;
  const economiaMensal = Math.max(0, custoAtual - novoCusto);
  const consumoTotalKwh = form.consumoPonta + form.consumoForaPonta + form.consumoIntermediario;

  const extras = adaptarFatura(faturaAtual, form);
  const notasApi = 'notas' in resp ? resp.notas : [];
  const indisponiveisApi = respComparacao ? respComparacao.indisponiveis : [];

  return {
    simId: `api-${Date.now()}`,
    distribuidoraNome: form.distribuidora,
    sigAgente: form.distribuidora,
    subgrupo: form.subgrupo,
    demandaFaturavelKw: Math.max(form.demandaMedida, form.demandaContratada),
    demandaContratadaKw: form.demandaContratada,
    consumoTotalCicloKwh: consumoTotalKwh,
    modalidadeRecomendadaNome: melhorApi,
    modalidadeRecomendadaKey: melhorKey,
    custoAtual,
    novoCusto,
    economiaMensal,
    economiaPercentual: custoAtual > 0 ? (economiaMensal / custoAtual) * 100 : 0,
    economiaAnual: economiaMensal * 12,
    custoAzul,
    custoConvencional,
    custoVerde,
    custoOptanteB,
    custoACL: custoAclPorEpi(novoCusto, epi, form.precoMedioACL),
    custoBranca,
    diferencaAzulVsVerde: custoAzul - custoVerde,
    sobreprecoConvencionalPct: custoVerde > 0 ? ((custoConvencional - custoVerde) / custoVerde) * 100 : 0,
    consumoPontaPercentual: consumoTotalKwh > 0 ? (form.consumoPonta / consumoTotalKwh) * 100 : 0,
    consumoForaPontaPercentual: consumoTotalKwh > 0 ? (form.consumoForaPonta / consumoTotalKwh) * 100 : 0,
    breakdown: extras.breakdown ?? [],
    totalOtimizado: novoCusto,
    composicao: extras.composicao ?? { energiaPct: 0, tusdPct: 0, tributosPct: 0 },
    comparativoTeTusd: comparativoDeFaturas(disponiveis),
    reativosTotal: extras.reativosTotal ?? 0,
    tributosTotaisEstimados: somaPorCategoria(faturaAtual, ['Tributos', 'Bandeira']),
    tributosPercentual: Number((form.pis + form.cofins + form.icms).toFixed(2)),
    notas: notasApi.map((n) => ({ tipo: n.tipo, mensagem: n.mensagem })),
    indisponiveis: indisponiveisApi.map((i) => ({ modalidade: i.modalidade, motivo: i.motivo })),
    fonte: 'api',
    epi,
    planejamento,
  };
}
