export type TariffModalidade =
  | 'verde'
  | 'azul'
  | 'optante_b'
  | 'branca'
  | 'convencional';

export type BandeiraTarifaria = 'verde' | 'amarela' | 'vermelha1' | 'vermelha2';

export type TipoICMS = 'fora' | 'dentro';

/** Atividades reconhecidas no bloco Optante B (art. 292). */
export type AtividadeEconomica =
  | 'Comercial ou Industrial'
  | 'Rural'
  | 'Residencial'
  | 'Esportivo ou Parque Agropecuário';

/** Tipo de ligação — custo de disponibilidade do Grupo B (art. 291). */
export type TipoLigacao = 'Trifásico' | 'Bifásico' | 'Monofásico';

export interface Distributor {
  id: string;
  sigAgente: string;
  name: string;
  state: string;
  region: string;
  subgroups: string[];
  baseTusdDemanda: number; // R$/kW
  baseTePonta: number; // R$/kWh
  baseTeForaPonta: number; // R$/kWh
  baseTusdPonta: number;
  baseTusdForaPonta: number;
  baseConvencionalKwh: number;
}

export interface InvoiceFormData {
  // Seção 1: Distribuidora e Modalidade
  distribuidora: string; // sig_agente (ex: COPEL-DIS, ENEL-SP, CEMIG-D, etc.)
  subgrupo: string; // A1..AS (Grupo A) ou B1..B4 (Grupo B)
  classe: string; // filtra a tarifa do Grupo B (ex.: Residencial, Comercial)
  subclasse: string; // filtra a tarifa do Grupo B (ex.: Residencial Baixa Renda)
  detalhe: string; // detalhe tarifário do dataset (padrão "Não se aplica")
  dataReferencia: string; // exibido DD/MM/AAAA; API recebe AAAA-MM-DD
  modalidadeAtual: TariffModalidade;
  bandeiraAutomatica: boolean;
  bandeira: BandeiraTarifaria;

  // Seção 2: Consumo Ativo e Demanda Registrada
  consumoPonta: number; // kWh
  consumoForaPonta: number; // kWh
  consumoIntermediario: number; // kWh (Branca)
  demandaMedida: number; // kW — Verde (demanda única)
  demandaContratada: number; // kW — Verde (demanda única)
  demandaPontaKw: number; // kW — Azul
  demandaForaPontaKw: number; // kW — Azul
  demandaContratadaPontaKw: number; // kW — Azul
  demandaContratadaForaPontaKw: number; // kW — Azul
  demandaIsentaIcmsAtiva: boolean; // envia demanda_isenta_icms=true
  demandaIsentaIcms: number; // kW (opcional)

  // Outras Parcelas e Mercado Livre (ACL)
  outrosValores: number; // R$
  percentualConsumoMesAnterior: number; // fração 0..1
  precoMedioACL: number; // R$/MWh (0 = sem proposta: só calcula o E-PI)
  opexMensal: number; // R$/mês — E-PI com custos de migração (0 = simplificado)
  capex: number; // R$ — E-PI com custos de migração
  horizonteMeses: number; // meses de amortização do CAPEX

  // Histórico de 12 meses para o planejamento anual (texto colado):
  // "MM/AAAA; demanda ponta; demanda fora ponta; consumo ponta; consumo fora ponta"
  historico12: string;

  // Seção 3: Reativos (art. 304)
  buscarReativoAuto: boolean; // true = VRERE/VRDRE do banco (reativos_direto=false)
  tarifaReativoEnergia: number; // R$/kVArh (modo manual)
  tarifaReativoDemanda: number; // R$/kVAr (modo manual)
  consumoReativoPonta: number; // kVArh (indutivo)
  consumoReativoForaPonta: number; // kVArh (indutivo)
  demandaReativaPonta: number; // kVAr (indutivo)
  demandaReativaForaPonta: number; // kVAr (indutivo)
  reativoEnergiaCapacitiva: number; // kVArh (janela 0h–6h)
  reativoDemandaCapacitiva: number; // kVAr (janela 0h–6h)
  tributarReativos: boolean; // tributar_reativos (faturas CEMIG/Equatorial)

  // Seção 4: Tributos
  aplicarTributos: boolean;
  pis: number; // % (ex: 0.95)
  cofins: number; // % (ex: 4.38)
  icms: number; // % (ex: 18)
  tipoIcms: TipoICMS; // 'fora' | 'dentro'
  cipCosip: number; // R$
  arredondarCentavos: boolean; // arredondar_centavos da API

  // Optante B — Grupo A faturado como Grupo B (art. 292)
  atividade: AtividadeEconomica;
  tipoLigacao: TipoLigacao;
  prePagamento: boolean;
  potenciaTransformadoresKva: number; // ≤ 112,5 kVA (ou ≤ 1.125 cooperativa)
  cooperativaEletrificacaoRural: boolean;
  hotelariaTurismo: boolean;
  cargaRefletoresKw: number; // ≥ 2/3 da carga instalada (esportivo/parques)
  cargaInstaladaTotalKw: number;

  // Metadados
  ucCode: string;
  unidadeNome: string;
}

export interface TableItemBreakdown {
  descricao: string;
  subtitulo: string;
  baseConsumo: string;
  tarifaHomologada?: string;
  tarifaSemTributo: string;
  tarifaComTributo: string;
  valorTotal: string;
  valorNum: number;
  dotColor: string;
}

export interface ModalidadeTeTusd {
  key: string;
  nome: string;
  custoTotal: number;
  teValor: number;
  tusdValor: number;
  tePct: number;
  tusdPct: number;
  descricaoRegulatoria: string;
  tag?: string;
  tagColor?: string;
}

/** Nota devolvida pela API (limitações/avisos) — exibida no relatório. */
export interface NotaCalculo {
  tipo: string; // ex.: 'info' | 'warning' | 'tarifa_ambigua' | 'reativos_*'
  mensagem: string;
}

/** Modalidade indisponível para o perfil e o motivo (regra de elegibilidade). */
export interface ModalidadeIndisponivel {
  modalidade: string;
  motivo: string;
}

/** Fonte do cálculo: API real ou motor de demonstração (fallback). */
export type FonteCalculo = 'api';

/** E-PI (preço de indiferença estimado) devolvido por POST /api/epi/calcular. */
export interface EpiResumo {
  pi: number; // R$/MWh
  modalidade: string;
  eMwh: number;
  baseAclMwh: number;
  comCustosMigracao: boolean;
  aviso: string | null;
}

/** Resultado de POST /api/planejamento/comparar (12 meses). */
export interface PlanejamentoModalidade {
  modalidade: string;
  custoContratoAtual: number;
  custoDemandaOtimizada: number;
  dcAtual: number | [number, number] | null;
  dcOtima: number | [number, number];
  epiAnual: number | null;
}

export interface PlanejamentoResumo {
  meses: number;
  melhorContratoAtual: string;
  melhorDemandaOtimizada: string;
  ganhoTotal: number;
  ganhoDemanda: number;
  ganhoModalidade: number;
  modalidades: PlanejamentoModalidade[];
  avisos: string[];
}

export interface AuditResult {
  simId: string;
  distribuidoraNome: string;
  sigAgente: string;
  subgrupo: string;
  demandaFaturavelKw: number;
  demandaContratadaKw: number;
  consumoTotalCicloKwh: number;
  modalidadeRecomendadaNome: string;
  modalidadeRecomendadaKey: TariffModalidade;
  custoAtual: number;
  novoCusto: number;
  economiaMensal: number;
  economiaPercentual: number;
  economiaAnual: number;
  custoAzul: number;
  custoConvencional: number;
  custoVerde: number;
  custoOptanteB: number;
  custoACL: number;
  custoBranca: number;
  diferencaAzulVsVerde: number;
  sobreprecoConvencionalPct: number;
  consumoPontaPercentual: number;
  consumoForaPontaPercentual: number;
  breakdown: TableItemBreakdown[];
  totalOtimizado: number;
  composicao: {
    energiaPct: number;
    tusdPct: number;
    tributosPct: number;
  };
  comparativoTeTusd: ModalidadeTeTusd[];
  reativosTotal: number;
  tributosTotaisEstimados: number;
  tributosPercentual: number;
  /** Notas de escopo/limitação devolvidas pela API (ex.: tarifa ambígua). */
  notas: NotaCalculo[];
  /** Modalidades fora da elegibilidade (ex.: Optante B sem art. 292). */
  indisponiveis: ModalidadeIndisponivel[];
  /** Onde o cálculo foi executado. */
  fonte: FonteCalculo;
  /** E-PI do mês informado (null se a API não respondeu). */
  epi: EpiResumo | null;
  /** Planejamento anual (null sem histórico de 12 meses). */
  planejamento: PlanejamentoResumo | null;
}
