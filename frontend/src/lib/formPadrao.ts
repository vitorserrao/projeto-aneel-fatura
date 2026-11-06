/**
 * Formulário vazio e exemplo real (fatura Copel A4 Verde 03/2023, total
 * impresso R$ 9.854,93 — docs/validacao_conta_real_copel_verde_2023.md).
 */
import type { InvoiceFormData } from '../types/energy';

export const HISTORICO_EXEMPLO_COPEL = [
  // Mês de consumo; demanda ponta; demanda fora ponta; consumo ponta; consumo fora ponta
  // (quadro "Histórico de Consumo" da fatura Copel 04/2023 — grandezas faturadas)
  '04/2022; 1,37; 206,44; 12; 6914',
  '05/2022; 7,97; 208,11; 25; 10600',
  '06/2022; 0,78; 207,13; 15; 2258',
  '07/2022; 0,39; 210,47; 14; 7463',
  '08/2022; 0,59; 206,44; 16; 10289',
  '09/2022; 0,88; 203,39; 16; 12832',
  '10/2022; 1,08; 193,25; 14; 9336',
  '11/2022; 0,78; 191,68; 16; 6903',
  '12/2022; 6,69; 168,16; 27; 6616',
  '01/2023; 4,82; 156,55; 49; 6846',
  '02/2023; 6,78; 139,82; 34; 7518',
  '03/2023; 6,88; 150,65; 55; 9094',
].join('\n');

export const DEFAULT_FORM: InvoiceFormData = {
  // Seção 1: Distribuidora e Modalidade
  distribuidora: '',
  subgrupo: '',
  classe: 'Não se aplica',
  subclasse: 'Não se aplica',
  detalhe: 'Não se aplica',
  dataReferencia: '',
  modalidadeAtual: 'verde',
  bandeiraAutomatica: true,
  bandeira: 'verde',

  // Seção 2: Consumo Ativo e Demanda Registrada
  consumoPonta: null,
  consumoForaPonta: null,
  consumoIntermediario: null,
  demandaMedida: null,
  demandaContratada: null,
  demandaPontaKw: null,
  demandaForaPontaKw: null,
  demandaContratadaPontaKw: null,
  demandaContratadaForaPontaKw: null,
  demandaIsentaIcmsAtiva: true,
  demandaIsentaIcms: 0,

  // Outras Parcelas e Mercado Livre (ACL)
  outrosValores: 0,
  percentualConsumoMesAnterior: 0,
  precoMedioACL: 0,
  opexMensal: 0,
  capex: 0,
  horizonteMeses: 60,
  encargosAcl: null,
  totalFatura: null,
  historico12: '',

  // Seção 3: Reativos
  buscarReativoAuto: true,
  tarifaReativoEnergia: 0,
  tarifaReativoDemanda: 0,
  consumoReativoPonta: 0,
  consumoReativoForaPonta: 0,
  demandaReativaPonta: 0,
  demandaReativaForaPonta: 0,
  reativoEnergiaCapacitiva: 0,
  reativoDemandaCapacitiva: 0,
  tributarReativos: false,

  // Seção 4: Tributos
  aplicarTributos: true,
  pis: null,
  cofins: null,
  icms: null,
  tipoIcms: 'fora',
  cipCosip: 0,
  arredondarCentavos: true,

  // Optante B (art. 292)
  atividade: 'Comercial ou Industrial',
  tipoLigacao: 'Trifásico',
  prePagamento: false,
  potenciaTransformadoresKva: null,
  cooperativaEletrificacaoRural: false,
  hotelariaTurismo: false,
  cargaRefletoresKw: 0,
  cargaInstaladaTotalKw: 0,

  // Metadados
  ucCode: '',
  unidadeNome: '',
};

export function exemploCopel(): InvoiceFormData {
  return {
    ...DEFAULT_FORM,
    distribuidora: 'COPEL-DIS',
    subgrupo: 'A4',
    dataReferencia: '15/03/2023',
    modalidadeAtual: 'verde',
    bandeiraAutomatica: true,
    bandeira: 'verde',
    consumoPonta: 55,
    consumoForaPonta: 9094,
    consumoIntermediario: 0,
    demandaMedida: 150.65,
    demandaContratada: 260,
    demandaIsentaIcmsAtiva: true,
    demandaIsentaIcms: 109.35,
    outrosValores: 115.01,
    percentualConsumoMesAnterior: 0,
    precoMedioACL: 0,
    opexMensal: 0,
    capex: 0,
    horizonteMeses: 60,
    historico12: HISTORICO_EXEMPLO_COPEL,
    // Fatura Copel 04/2023 (consumo de 03/2023): total impresso R$ 9.854,93
    totalFatura: 9854.93,
    encargosAcl: null,
    potenciaTransformadoresKva: null,
    ucCode: 'UC COPEL-1',
    unidadeNome: 'Exemplo Copel A4 Verde',
    buscarReativoAuto: true,
    consumoReativoPonta: 0,
    consumoReativoForaPonta: 9,
    demandaReativaPonta: 0,
    demandaReativaForaPonta: 0,
    aplicarTributos: true,
    pis: 0.95,
    cofins: 4.38,
    icms: 18,
    tipoIcms: 'fora',
    cipCosip: 0,
  };
}

