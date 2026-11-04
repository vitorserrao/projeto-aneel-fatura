import { Distributor, InvoiceFormData, AuditResult, TariffModalidade, ModalidadeTeTusd } from '../types/energy';

export const DISTRIBUTORS: Distributor[] = [
  {
    id: 'COPEL-DIS',
    sigAgente: 'COPEL-DIS',
    name: 'Copel Distribuição (Paraná)',
    state: 'PR',
    region: 'Sul',
    subgroups: ['A4', 'A3a', 'A2', 'Optante B', 'B3'],
    baseTusdDemanda: 23.90,
    baseTePonta: 0.795,
    baseTeForaPonta: 0.078,
    baseTusdPonta: 0.498,
    baseTusdForaPonta: 0.026,
    baseConvencionalKwh: 0.492,
  },
  {
    id: 'ENEL-SP',
    sigAgente: 'ENEL-SP',
    name: 'Enel Distribuição São Paulo',
    state: 'SP',
    region: 'Sudeste',
    subgroups: ['A4', 'A3a', 'A2', 'Optante B', 'B3'],
    baseTusdDemanda: 25.44,
    baseTePonta: 0.812,
    baseTeForaPonta: 0.082,
    baseTusdPonta: 0.5164,
    baseTusdForaPonta: 0.0282,
    baseConvencionalKwh: 0.518,
  },
  {
    id: 'CEMIG-D',
    sigAgente: 'CEMIG-D',
    name: 'Cemig Distribuição (Minas Gerais)',
    state: 'MG',
    region: 'Sudeste',
    subgroups: ['A4', 'A3a', 'A2', 'Optante B', 'B3'],
    baseTusdDemanda: 28.12,
    baseTePonta: 0.845,
    baseTeForaPonta: 0.089,
    baseTusdPonta: 0.542,
    baseTusdForaPonta: 0.031,
    baseConvencionalKwh: 0.548,
  },
  {
    id: 'CPFL-PAULISTA',
    sigAgente: 'CPFL-PAULISTA',
    name: 'CPFL Paulista',
    state: 'SP',
    region: 'Sudeste',
    subgroups: ['A4', 'A3a', 'A2', 'Optante B'],
    baseTusdDemanda: 26.85,
    baseTePonta: 0.822,
    baseTeForaPonta: 0.085,
    baseTusdPonta: 0.528,
    baseTusdForaPonta: 0.029,
    baseConvencionalKwh: 0.532,
  },
  {
    id: 'LIGHT',
    sigAgente: 'LIGHT',
    name: 'Light Serviços de Eletricidade (Rio de Janeiro)',
    state: 'RJ',
    region: 'Sudeste',
    subgroups: ['A4', 'A3a', 'A2', 'Optante B'],
    baseTusdDemanda: 29.80,
    baseTePonta: 0.865,
    baseTeForaPonta: 0.092,
    baseTusdPonta: 0.565,
    baseTusdForaPonta: 0.033,
    baseConvencionalKwh: 0.568,
  },
];

export const SUBGROUPS = [
  { id: 'A1', label: 'A1 (≥ 230 kV)' },
  { id: 'A2', label: 'A2 (88 kV a 138 kV)' },
  { id: 'A3', label: 'A3 (69 kV)' },
  { id: 'A3a', label: 'A3a (30 kV a 44 kV)' },
  { id: 'A4', label: 'A4 (2,3 kV a 25 kV)' },
  { id: 'AS', label: 'AS (Subterrâneo)' },
  { id: 'B1', label: 'B1 (Residencial)' },
  { id: 'B2', label: 'B2 (Rural)' },
  { id: 'B3', label: 'B3 (Demais classes)' },
  { id: 'B4', label: 'B4 (Iluminação Pública)' },
];

export const MODALIDADE_OPTIONS: { id: TariffModalidade; label: string }[] = [
  { id: 'verde', label: 'Verde' },
  { id: 'azul', label: 'Azul' },
  { id: 'optante_b', label: 'Optante B' },
  { id: 'branca', label: 'Branca' },
  { id: 'convencional', label: 'Convencional Monômia' },
];

export const BANDEIRA_ADICIONAIS = {
  verde: 0.0,
  amarela: 0.01874,
  vermelha1: 0.03971,
  vermelha2: 0.09492,
};

export const VRERE_FIXO = 0.28209; // R$/kVArh (art. 304 REN 1.000/2021)
export const VRDRE_FIXO = 14.85; // R$/kVAr

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatNumber(value: number, decimals: number = 0): string {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

export function calculateAudit(form: InvoiceFormData): AuditResult {
  const dist =
    DISTRIBUTORS.find((d) => d.sigAgente === form.distribuidora || d.id === form.distribuidora) ||
    DISTRIBUTORS[0];

  // 1. Consumo Total do Ciclo
  const consumoTotal = form.consumoPonta + form.consumoForaPonta + form.consumoIntermediario;
  const pctPonta = consumoTotal > 0 ? (form.consumoPonta / consumoTotal) * 100 : 0.6;
  const pctForaPonta = consumoTotal > 0 ? (form.consumoForaPonta / consumoTotal) * 100 : 99.4;

  // 2. Demanda Faturável = máx(medida, contratada) — Verde (única) e Azul (por posto)
  const demandaFaturavel = Math.max(form.demandaMedida, form.demandaContratada);
  const demandaPontaFaturavel = Math.max(
    form.demandaPontaKw || form.demandaMedida,
    form.demandaContratadaPontaKw || form.demandaContratada,
  );
  const demandaForaFaturavel = Math.max(
    form.demandaForaPontaKw || form.demandaMedida,
    form.demandaContratadaForaPontaKw || form.demandaContratada,
  );

  // 3. Isenção de ICMS na demanda (apenas quando o toggle está ativo)
  const isentaAtiva = form.demandaIsentaIcmsAtiva && form.demandaIsentaIcms > 0;
  const demandaIsenta = isentaAtiva ? form.demandaIsentaIcms : 0;

  // 4. Bandeira Adicional (valores oficiais REN 479/2012)
  const effectiveBandeira = form.bandeiraAutomatica ? 'verde' : form.bandeira;
  const bandeiraAdicional = BANDEIRA_ADICIONAIS[effectiveBandeira] ?? 0;

  // 5. Reativos Excedentes (Art. 304 REN 1.000/2021)
  const vrere = form.buscarReativoAuto ? VRERE_FIXO : form.tarifaReativoEnergia || VRERE_FIXO;
  const vrdre = form.buscarReativoAuto ? VRDRE_FIXO : form.tarifaReativoDemanda || VRDRE_FIXO;
  const custoReativoEnergia =
    (form.consumoReativoPonta + form.consumoReativoForaPonta + form.reativoEnergiaCapacitiva) * vrere;
  const custoReativoPotencia =
    (form.demandaReativaPonta + form.demandaReativaForaPonta + form.reativoDemandaCapacitiva) * vrdre;
  const reativosTotal = custoReativoEnergia + custoReativoPotencia;

  // Fator de ajuste por distribuidora
  const baseMult = dist.baseTusdDemanda / 23.90;

  // Tarifas Homologadas COPEL / Padrão ANEEL (demonstração):
  const tarifaPontaVerde = 1.3284 + bandeiraAdicional;
  const tarifaForaPontaVerde = 0.1102 + bandeiraAdicional;
  const tarifaDemandaVerde = dist.baseTusdDemanda;

  const valorPontaVerde = form.consumoPonta * tarifaPontaVerde;
  const valorForaPontaVerde = form.consumoForaPonta * tarifaForaPontaVerde;
  const valorDemandaVerde = demandaFaturavel * tarifaDemandaVerde;

  // Base Líquida Verde
  const subtotalVerde =
    valorPontaVerde + valorForaPontaVerde + valorDemandaVerde + reativosTotal + form.outrosValores;

  // Tarifa Azul — demanda por posto (ponta/fora ponta)
  const demandaPontaAzul = demandaPontaFaturavel * 48.2 * baseMult;
  const demandaForaPontaAzul = demandaForaFaturavel * 18.4 * baseMult;
  const consumoPontaAzul = form.consumoPonta * (0.852 + bandeiraAdicional) * baseMult;
  const consumoForaPontaAzul = form.consumoForaPonta * (0.112 + bandeiraAdicional) * baseMult;
  const subtotalAzul =
    demandaPontaAzul +
    demandaForaPontaAzul +
    consumoPontaAzul +
    consumoForaPontaAzul +
    reativosTotal +
    form.outrosValores;

  // Tarifa Convencional Monômia — sem faturamento de demanda (Grupo B)
  const convRate = (dist.baseConvencionalKwh + bandeiraAdicional) * baseMult;
  const subtotalConvencional = consumoTotal * convRate + reativosTotal + form.outrosValores;

  // Optante B (art. 292): faturado como Grupo B (mesma base da Convencional) +
  // custo de disponibilidade (30/50/100 kWh) quando o consumo for menor.
  const minimoKwh =
    form.tipoLigacao === 'Monofásico' ? 30 : form.tipoLigacao === 'Bifásico' ? 50 : 100;
  const consumoFaturadoB = Math.max(consumoTotal, minimoKwh);
  const subtotalOptanteB = consumoFaturadoB * convRate + reativosTotal + form.outrosValores;

  // Tarifa Branca — aproximação de demonstração por posto (ponta/intermediário/fora)
  const subtotalBranca =
    form.consumoPonta * convRate * 2.2 +
    form.consumoIntermediario * convRate * 1.2 +
    form.consumoForaPonta * convRate * 0.8 +
    reativosTotal +
    form.outrosValores;

  // Aplicação de Tributos (PIS, COFINS, ICMS)
  const pisAliq = form.aplicarTributos ? form.pis / 100 : 0;
  const cofinsAliq = form.aplicarTributos ? form.cofins / 100 : 0;
  const icmsAliq = form.aplicarTributos ? form.icms / 100 : 0;
  const somaAliquotas = pisAliq + cofinsAliq + icmsAliq;

  const aplicarTributo = (base: number) => {
    if (!form.aplicarTributos || somaAliquotas <= 0) return base + form.cipCosip;
    if (form.tipoIcms === 'dentro') {
      // Gross-up por dentro: Base / (1 - somaAliquotas)
      const divisor = Math.max(0.01, 1 - somaAliquotas);
      return base / divisor + form.cipCosip;
    }
    // Por fora: somado diretamente sobre a base
    return base * (1 + somaAliquotas) + form.cipCosip;
  };

  // Fatores de gross-up e tributação unitária
  let fatorTributo = 1;
  let fatorDemanda = 1;
  if (form.aplicarTributos && somaAliquotas > 0) {
    if (form.tipoIcms === 'dentro') {
      const divisor = Math.max(0.01, 1 - somaAliquotas);
      fatorTributo = 1 / divisor;

      if (demandaIsenta > 0 && demandaFaturavel > 0) {
        const divisorSemIcms = Math.max(0.01, 1 - (pisAliq + cofinsAliq));
        const fatorSemIcms = 1 / divisorSemIcms;
        const fracIsenta = Math.min(1, demandaIsenta / demandaFaturavel);
        const fracTrib = 1 - fracIsenta;
        fatorDemanda = fracIsenta * fatorSemIcms + fracTrib * fatorTributo;
      } else {
        fatorDemanda = fatorTributo;
      }
    } else {
      fatorTributo = 1 + somaAliquotas;
      if (demandaIsenta > 0 && demandaFaturavel > 0) {
        const fatorSemIcms = 1 + (pisAliq + cofinsAliq);
        const fracIsenta = Math.min(1, demandaIsenta / demandaFaturavel);
        const fracTrib = 1 - fracIsenta;
        fatorDemanda = fracIsenta * fatorSemIcms + fracTrib * fatorTributo;
      } else {
        fatorDemanda = fatorTributo;
      }
    }
  }

  // Valores unitários e totais com tributos
  const tarifaPontaVerdeComTrib = tarifaPontaVerde * fatorTributo;
  const valorPontaVerdeComTrib = form.consumoPonta * tarifaPontaVerdeComTrib;

  const tarifaForaPontaVerdeComTrib = tarifaForaPontaVerde * fatorTributo;
  const valorForaPontaVerdeComTrib = form.consumoForaPonta * tarifaForaPontaVerdeComTrib;

  const tarifaDemandaVerdeComTrib = tarifaDemandaVerde * fatorDemanda;
  const valorDemandaVerdeComTrib = demandaFaturavel * tarifaDemandaVerdeComTrib;

  const tarifaReativoComTrib = vrere * fatorTributo;
  const valorReativoComTrib = reativosTotal * fatorTributo;

  const valorOutrosComTrib = form.outrosValores * fatorTributo;
  const valorCipCosip = form.cipCosip;

  const totalOtimizado =
    valorPontaVerdeComTrib +
    valorForaPontaVerdeComTrib +
    valorDemandaVerdeComTrib +
    valorReativoComTrib +
    valorOutrosComTrib +
    valorCipCosip;

  const custoVerde = Math.round(totalOtimizado);
  const custoAzul = Math.round(aplicarTributo(subtotalAzul));
  const custoConvencional = Math.round(aplicarTributo(subtotalConvencional));
  const custoOptanteB = Math.round(aplicarTributo(subtotalOptanteB));
  const custoBranca = Math.round(aplicarTributo(subtotalBranca));

  // Comparação com Mercado Livre (ACL)
  let custoACL = 0;
  if (form.precoMedioACL > 0) {
    const precoEnergiaKwh = form.precoMedioACL / 1000;
    const custoEnergiaACL = consumoTotal * precoEnergiaKwh;
    const tusdFioACL = demandaFaturavel * (dist.baseTusdDemanda * 0.75);
    const subtotalACL = custoEnergiaACL + tusdFioACL + form.outrosValores;
    custoACL = Math.round(aplicarTributo(subtotalACL));
  } else {
    custoACL = Math.round(custoVerde * 0.774);
  }

  // Custo da modalidade faturada atualmente:
  let custoAtual = custoConvencional;
  if (form.modalidadeAtual === 'verde') custoAtual = custoVerde;
  else if (form.modalidadeAtual === 'azul') custoAtual = custoAzul;
  else if (form.modalidadeAtual === 'branca') custoAtual = custoBranca;
  else if (form.modalidadeAtual === 'optante_b') {
    custoAtual = custoOptanteB;
  }

  // Recomendação inteligente:
  // Se mais de 75% for fora de ponta, Verde é a melhor.
  const recomendadaKey: TariffModalidade = pctForaPonta >= 75 ? 'verde' : 'azul';
  const recomendadaNome =
    recomendadaKey === 'verde' ? 'Tarifa Horária Verde' : 'Tarifa Horária Azul';
  const novoCusto = recomendadaKey === 'verde' ? custoVerde : custoAzul;

  const economiaMensal = Math.max(0, custoAtual - novoCusto);
  const economiaPercentual = custoAtual > 0 ? (economiaMensal / custoAtual) * 100 : 0;
  const economiaAnual = economiaMensal * 12;

  const diferencaAzulVsVerde = custoAzul - custoVerde;
  const diferencaConvencionalVsVerde = custoConvencional - custoVerde;
  const sobreprecoConvencionalPct =
    custoVerde > 0 ? (diferencaConvencionalVsVerde / custoVerde) * 100 : 0;

  const breakdown: AuditResult['breakdown'] = [
    {
      descricao: 'Consumo Ponta (P)',
      subtitulo: 'Energia consumida no horário de maior pico do sistema elétrico (18h às 21h, dias úteis).',
      baseConsumo: `${formatNumber(form.consumoPonta)} kWh`,
      tarifaHomologada: `R$ ${tarifaPontaVerde.toFixed(4).replace('.', ',')} / kWh`,
      tarifaSemTributo: `R$ ${tarifaPontaVerde.toFixed(4).replace('.', ',')} / kWh`,
      tarifaComTributo: `R$ ${tarifaPontaVerdeComTrib.toFixed(4).replace('.', ',')} / kWh`,
      valorTotal: formatCurrency(valorPontaVerdeComTrib),
      valorNum: valorPontaVerdeComTrib,
      dotColor: 'bg-emerald-600',
    },
    {
      descricao: 'Consumo Fora Ponta (FP)',
      subtitulo: 'Energia consumida no período diurno e noturno com menor demanda na rede e tarifa reduzida.',
      baseConsumo: `${formatNumber(form.consumoForaPonta)} kWh`,
      tarifaHomologada: `R$ ${tarifaForaPontaVerde.toFixed(4).replace('.', ',')} / kWh`,
      tarifaSemTributo: `R$ ${tarifaForaPontaVerde.toFixed(4).replace('.', ',')} / kWh`,
      tarifaComTributo: `R$ ${tarifaForaPontaVerdeComTrib.toFixed(4).replace('.', ',')} / kWh`,
      valorTotal: formatCurrency(valorForaPontaVerdeComTrib),
      valorNum: valorForaPontaVerdeComTrib,
      dotColor: 'bg-emerald-400',
    },
    {
      descricao: 'Demanda Faturável Única (Contratada)',
      subtitulo: `Potência contratada (${formatNumber(form.demandaContratada)} kW vs medida ${formatNumber(form.demandaMedida, 2)} kW). Na Tarifa Verde, aplica-se tarifa única.`,
      baseConsumo: `${formatNumber(demandaFaturavel)} kW`,
      tarifaHomologada: `R$ ${tarifaDemandaVerde.toFixed(2).replace('.', ',')} / kW`,
      tarifaSemTributo: `R$ ${tarifaDemandaVerde.toFixed(2).replace('.', ',')} / kW`,
      tarifaComTributo: `R$ ${tarifaDemandaVerdeComTrib.toFixed(2).replace('.', ',')} / kW`,
      valorTotal: formatCurrency(valorDemandaVerdeComTrib),
      valorNum: valorDemandaVerdeComTrib,
      dotColor: 'bg-blue-600',
    },
  ];

  if (reativosTotal > 0) {
    breakdown.push({
      descricao: 'Excedente Reativo (Art. 304 REN 1.000/2021)',
      subtitulo: `Cobrança de energia/potência reativa excedente apurada fora dos limites de fator de potência.`,
      baseConsumo: `${formatNumber(form.consumoReativoForaPonta + form.consumoReativoPonta)} kVArh`,
      tarifaHomologada: `R$ ${vrere.toFixed(5).replace('.', ',')} / kVArh`,
      tarifaSemTributo: `R$ ${vrere.toFixed(5).replace('.', ',')} / kVArh`,
      tarifaComTributo: `R$ ${tarifaReativoComTrib.toFixed(5).replace('.', ',')} / kVArh`,
      valorTotal: formatCurrency(valorReativoComTrib),
      valorNum: valorReativoComTrib,
      dotColor: 'bg-rose-500',
    });
  }

  // Especificação de Parcelas e Encargos (CIP/COSIP e Outros)
  if (form.cipCosip > 0) {
    breakdown.push({
      descricao: 'Parcelas / Encargos — CIP/COSIP',
      subtitulo: 'Contribuição de Iluminação Pública municipal (custeio do serviço - Art. 149-A da CF).',
      baseConsumo: 'Fixo / Mensal',
      tarifaHomologada: '-',
      tarifaSemTributo: '-',
      tarifaComTributo: '-',
      valorTotal: formatCurrency(form.cipCosip),
      valorNum: form.cipCosip,
      dotColor: 'bg-slate-600',
    });
  }

  if (form.outrosValores > 0) {
    breakdown.push({
      descricao: 'Parcelas / Encargos — Outros Valores',
      subtitulo: 'Valores e encargos adicionais faturados na conta da concessionária.',
      baseConsumo: 'Fixo / Mensal',
      tarifaHomologada: '-',
      tarifaSemTributo: '-',
      tarifaComTributo: '-',
      valorTotal: formatCurrency(valorOutrosComTrib),
      valorNum: valorOutrosComTrib,
      dotColor: 'bg-slate-500',
    });
  }

  // Desdobramento de TE e TUSD por modalidade
  const teVerde = Math.round(valorPontaVerdeComTrib + valorForaPontaVerdeComTrib);
  const tusdVerde = Math.max(0, Math.round(custoVerde - teVerde));
  const teVerdePct = custoVerde > 0 ? Math.round((teVerde / custoVerde) * 100) : 50;
  const tusdVerdePct = 100 - teVerdePct;

  const teAzul = Math.round((consumoPontaAzul + consumoForaPontaAzul) * fatorTributo);
  const tusdAzul = Math.max(0, Math.round(custoAzul - teAzul));
  const teAzulPct = custoAzul > 0 ? Math.round((teAzul / custoAzul) * 100) : 40;
  const tusdAzulPct = 100 - teAzulPct;

  const teConv = Math.round((consumoTotal * convRate) * fatorTributo);
  const tusdConv = Math.max(0, Math.round(custoConvencional - teConv));
  const teConvPct = custoConvencional > 0 ? Math.round((teConv / custoConvencional) * 100) : 55;
  const tusdConvPct = 100 - teConvPct;

  const teACL = Math.round(custoACL * 0.42);
  const tusdACL = Math.max(0, Math.round(custoACL - teACL));
  const teACLPct = custoACL > 0 ? Math.round((teACL / custoACL) * 100) : 42;
  const tusdACLPct = 100 - teACLPct;

  const comparativoTeTusd: ModalidadeTeTusd[] = [
    {
      key: 'verde',
      nome: 'Tarifa Horária Verde',
      custoTotal: custoVerde,
      teValor: teVerde,
      tusdValor: tusdVerde,
      tePct: teVerdePct,
      tusdPct: tusdVerdePct,
      descricaoRegulatoria: 'Demanda única sem sobretaxa no horário de ponta. Fatura de rede (TUSD) otimizada.',
      tag: 'Recomendada',
      tagColor: 'bg-amber-100 text-amber-900 border border-amber-300 font-bold',
    },
    {
      key: 'azul',
      nome: 'Tarifa Horária Azul',
      custoTotal: custoAzul,
      teValor: teAzul,
      tusdValor: tusdAzul,
      tePct: teAzulPct,
      tusdPct: tusdAzulPct,
      descricaoRegulatoria: 'Demanda contratada segregada (Ponta e Fora Ponta). Custo de TUSD fio expressivamente mais alto.',
      tag: `+ ${formatCurrency(diferencaAzulVsVerde)} vs Verde`,
      tagColor: 'bg-slate-100 text-slate-700 border border-slate-200 font-semibold',
    },
    {
      key: 'convencional',
      nome: 'Tarifa Convencional',
      custoTotal: custoConvencional,
      teValor: teConv,
      tusdValor: tusdConv,
      tePct: teConvPct,
      tusdPct: tusdConvPct,
      descricaoRegulatoria: 'Modalidade monômia linear sem diferenciação de ponta. Não aproveita o baixo custo fora de ponta.',
      tag: 'Situação Atual',
      tagColor: 'bg-slate-100 text-slate-700 border border-slate-200 font-medium',
    },
    {
      key: 'acl',
      nome: 'Mercado Livre (ACL)',
      custoTotal: custoACL,
      teValor: teACL,
      tusdValor: tusdACL,
      tePct: teACLPct,
      tusdPct: tusdACLPct,
      descricaoRegulatoria: 'Energia (TE) livremente contratada com gerador/comercializador. TUSD fio regulado ANEEL.',
      tag: 'Oportunidade Futura',
      tagColor: 'bg-indigo-50 text-indigo-800 border border-indigo-200 font-semibold',
    },
  ];

  const tributosTotais = Math.round(novoCusto * (somaAliquotas / (1 + somaAliquotas)));

  // Elegibilidade do Optante B (art. 292) — mesma regra do core/motor_calculo.py.
  const atividadeEsportiva = /esportiv|parque|agropecu/i.test(form.atividade);
  const elegivelOptanteB =
    form.hotelariaTurismo ||
    (atividadeEsportiva &&
      form.cargaRefletoresKw > 0 &&
      form.cargaInstaladaTotalKw > 0 &&
      form.cargaRefletoresKw >= (2 / 3) * form.cargaInstaladaTotalKw) ||
    (form.potenciaTransformadoresKva > 0 &&
      form.potenciaTransformadoresKva <=
        (form.cooperativaEletrificacaoRural ? 1125 : 112.5));

  return {
    simId: 'SIM-2025-9482',
    distribuidoraNome: dist.name,
    sigAgente: dist.sigAgente,
    subgrupo: form.subgrupo,
    demandaFaturavelKw: demandaFaturavel,
    demandaContratadaKw: form.demandaContratada,
    consumoTotalCicloKwh: consumoTotal,
    modalidadeRecomendadaNome: recomendadaNome,
    modalidadeRecomendadaKey: recomendadaKey,
    custoAtual,
    novoCusto,
    economiaMensal,
    economiaPercentual,
    economiaAnual,
    custoAzul,
    custoConvencional,
    custoVerde,
    custoOptanteB,
    custoACL,
    custoBranca,
    diferencaAzulVsVerde,
    sobreprecoConvencionalPct,
    consumoPontaPercentual: pctPonta,
    consumoForaPontaPercentual: pctForaPonta,
    breakdown,
    totalOtimizado: novoCusto,
    composicao: {
      energiaPct: 48,
      tusdPct: 26,
      tributosPct: 26,
    },
    comparativoTeTusd,
    reativosTotal,
    tributosTotaisEstimados: tributosTotais,
    tributosPercentual: Number((form.pis + form.cofins + form.icms).toFixed(2)),
    notas: [
      {
        tipo: 'info',
        mensagem:
          'Motor de demonstração (fallback). Conecte a API real para o cálculo regulatório (POST /api/calculo/fatura).',
      },
    ],
    indisponiveis: elegivelOptanteB
      ? []
      : [
          {
            modalidade: 'Optante B',
            motivo:
              'Optante B (art. 292): exige transformadores ≤ 112,5 kVA (ou ≤ 1.125 kVA se cooperativa de eletrificação rural), hotelaria/turismo ou iluminação esportiva ≥ 2/3 da carga.',
          },
        ],
    fonte: 'demo',
  };
}
