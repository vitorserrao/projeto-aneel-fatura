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

/** Campo numérico: null = não informado (nunca vira 0 escondido). */
export type NumOpc = number | null;

export interface InvoiceFormData {
  // Seção 1: Distribuidora e Modalidade
  distribuidora: string; // sig_agente (ex: COPEL-DIS, ENEL-SP, CEMIG-D, etc.)
  subgrupo: string; // A1..AS (Grupo A) ou B1..B4 (Grupo B)
  dataReferencia: string; // exibido DD/MM/AAAA; API recebe AAAA-MM-DD
  modalidadeAtual: TariffModalidade;
  bandeiraAutomatica: boolean;
  bandeira: BandeiraTarifaria;
  /** Bandeira manual em R$/kWh (B12: ex. proporcional aos dias). null = usa a bandeira escolhida. */
  bandeiraManualRkwh: number | null;

  // Seção 2: Consumo Ativo e Demanda Registrada
  consumoPonta: number | null; // kWh
  consumoForaPonta: number | null; // kWh
  consumoIntermediario: number | null; // kWh (Branca)
  demandaMedida: number | null; // kW — Verde (demanda única)
  demandaContratada: number | null; // kW — Verde (demanda única)
  demandaPontaKw: number | null; // kW — Azul
  demandaForaPontaKw: number | null; // kW — Azul
  demandaContratadaPontaKw: number | null; // kW — Azul
  demandaContratadaForaPontaKw: number | null; // kW — Azul
  demandaIsentaIcmsAtiva: boolean; // envia demanda_isenta_icms=true
  demandaIsentaIcms: number; // kW (opcional)

  // Outras Parcelas e Mercado Livre (ACL)
  outrosValores: number; // R$
  percentualConsumoMesAnterior: number; // fração 0..1
  precoMedioACL: number; // R$/MWh (0 = sem proposta: só calcula o E-PI)
  opexMensal: number; // R$/mês — E-PI com custos de migração (0 = simplificado)
  capex: number; // R$ — E-PI com custos de migração
  horizonteMeses: number; // meses de amortização do CAPEX
  encargosAcl: number | null; // R$/MWh (ESS/EER, CCEE) — vazio = 0, declarado no relatório
  totalFatura: number | null; // R$ impresso na fatura — conferência (opcional)
  /** B13: retenções/créditos impressos na fatura (R$, positivo). Só para a conferência: nunca vai à API. */
  retencoesCreditos: number | null;

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
  pis: number | null; // % (ex: 0.95)
  cofins: number | null; // % (ex: 4.38)
  icms: number | null; // % (ex: 18)
  tipoIcms: TipoICMS; // 'fora' | 'dentro'
  cipCosip: number; // R$
  arredondarCentavos: boolean; // arredondar_centavos da API

  // Optante B — Grupo A faturado como Grupo B (art. 292)
  atividade: AtividadeEconomica;
  tipoLigacao: TipoLigacao;
  prePagamento: boolean;
  potenciaTransformadoresKva: number | null; // ≤ 112,5 kVA (ou ≤ 1.125 cooperativa)
  cooperativaEletrificacaoRural: boolean;
  hotelariaTurismo: boolean;
  cargaRefletoresKw: number; // ≥ 2/3 da carga instalada (esportivo/parques)
  cargaInstaladaTotalKw: number;

}
