import React, { useState } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  Printer,
  Sliders,
  Verified,
  TrendingDown,
  TrendingUp,
  Receipt,
  CheckCircle2,
  AlertTriangle,
  Info,
  BarChart3,
  Sparkles,
  Check,
  Zap,
  Layers,
  Scale,
} from 'lucide-react';
import { AuditResult, InvoiceFormData } from '../types/energy';
import { formatCurrency, formatNumber } from '../utils/calculator';

interface StepTwoReportProps {
  audit: AuditResult;
  formData: InvoiceFormData;
  onBackToEdit: () => void;
  onRequestMigration?: () => void;
  onExportPdf: () => void;
}

export const StepTwoReport: React.FC<StepTwoReportProps> = ({
  audit,
  formData,
  onBackToEdit,
  onRequestMigration: _onRequestMigration,
  onExportPdf,
}) => {
  // Bar height proportions based on Convencional as 100%:
  const maxBase = Math.max(audit.custoConvencional, 1);
  const convHeightPct = 100;
  const azulHeightPct = Math.round((audit.custoAzul / maxBase) * 100);
  const verdeHeightPct = Math.round((audit.custoVerde / maxBase) * 100);
  const aclHeightPct = Math.round((audit.custoACL / maxBase) * 100);

  const [comparativoTab, setComparativoTab] = useState<'todos' | 'te_tusd' | 'custos' | 'matriz'>('todos');

  // Escala dinâmica para o Gráfico de Custo Total
  const maxTotalCost = Math.max(
    audit.custoConvencional,
    audit.custoAzul,
    audit.custoVerde,
    audit.custoACL,
    1000
  );
  const yCostStep = Math.max(1000, Math.ceil(maxTotalCost / 4 / 500) * 500);
  const yCostMax = yCostStep * 4;
  const yCostTicks = [yCostMax, yCostStep * 3, yCostStep * 2, yCostStep, 0];

  // Escala dinâmica para o Gráfico de TE e TUSD
  const maxTeTusdVal = Math.max(
    ...audit.comparativoTeTusd.flatMap((m) => [m.teValor, m.tusdValor]),
    1000
  );
  const yTeTusdStep = Math.max(1000, Math.ceil(maxTeTusdVal / 4 / 500) * 500);
  const yTeTusdMax = yTeTusdStep * 4;
  const yTeTusdTicks = [yTeTusdMax, yTeTusdStep * 3, yTeTusdStep * 2, yTeTusdStep, 0];

  return (
    <div className="flex flex-col w-full gap-8 pb-12 print-page">
      {/* HERO CARD RESUMO EXECUTIVO */}
      <div className="relative overflow-hidden bg-white rounded-2xl p-6 sm:p-8 shadow-sm border border-slate-200/80 flex flex-col gap-6">
        <div className="absolute -right-8 -top-8 w-80 h-80 bg-gradient-to-br from-slate-100/80 to-transparent rounded-full blur-2xl pointer-events-none"></div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200/80 pb-6 relative z-10">
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold uppercase tracking-wider shadow-xs">
                <Verified className="w-3.5 h-3.5 text-emerald-600 fill-emerald-500/10" />
                Recomendação Oficial ACR × ACL
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-slate-300 hidden sm:inline-block"></span>
              <span className="font-mono-num text-xs text-slate-500 font-semibold">
                ID #{audit.simId}
              </span>
            </div>

            <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900 tracking-tight mt-1">
              Diagnóstico Concluído: Oportunidade de Redução de Custos
            </h1>

            <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
              Auditoria regulatória baseada em{' '}
              <strong className="text-slate-900 font-semibold">
                {audit.sigAgente} ({audit.distribuidoraNome}) • Subgrupo {audit.subgrupo} • Demanda Faturável{' '}
                {audit.demandaFaturavelKw} kW (Contratada: {audit.demandaContratadaKw} kW)
              </strong>{' '}
              com consumo apurado de {formatNumber(audit.consumoTotalCicloKwh)} kWh.
            </p>
          </div>

          {/* Botões Superiores */}
          <div className="flex items-center gap-3 shrink-0 relative z-10 no-print">
            <button
              onClick={onBackToEdit}
              type="button"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-800 text-xs font-semibold transition-all duration-200 border border-slate-200/80 cursor-pointer shadow-2xs"
            >
              <Sliders className="w-4 h-4 text-slate-500" />
              <span>Editar Parâmetros</span>
            </button>

            <button
              onClick={onExportPdf}
              type="button"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-400 to-yellow-400 hover:from-amber-300 hover:to-yellow-300 text-slate-950 font-black text-xs transition-all duration-200 cursor-pointer shadow-sm border border-amber-300"
            >
              <Printer className="w-4 h-4 text-slate-950 font-bold" />
              <span>Exportar Relatório PDF</span>
            </button>
          </div>
        </div>

        {/* Núcleo de Destaque Financeiro */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center pt-1 relative z-10">
          {/* Economia Mensal e Anual em Destaque */}
          <div className="lg:col-span-6 flex flex-col gap-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-900 border border-emerald-200 w-fit shadow-xs">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
              <span className="text-xs font-bold text-emerald-900">
                Modalidade Recomendada: {audit.modalidadeRecomendadaNome}
              </span>
            </div>

            <div>
              <span className="text-xs text-slate-500 uppercase font-semibold tracking-wider">
                Potencial de Economia Mensal Imediata
              </span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="font-mono-num text-3xl sm:text-4xl lg:text-5xl font-extrabold text-emerald-600 tracking-tight">
                  {formatCurrency(audit.economiaMensal)}
                </span>
                <span className="text-base text-slate-500 font-medium">/ mês</span>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3 mt-1">
              <span className="inline-flex items-center gap-1 font-mono-num text-xs font-bold text-emerald-900 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-lg">
                <TrendingDown className="w-4 h-4 text-emerald-600 inline" />-
                {formatNumber(audit.economiaPercentual, 1)}% de economia
              </span>
              <span className="text-xs sm:text-sm text-slate-600">
                Equivalente a{' '}
                <strong className="text-slate-900 font-semibold">
                  {formatCurrency(audit.economiaAnual)} / ano
                </strong>{' '}
                sem obras ou investimentos
              </span>
            </div>
          </div>

          {/* Comparador Visual Lado a Lado (Custo Atual -> Novo Custo) */}
          <div className="lg:col-span-6 flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-4 bg-slate-50 p-4 sm:p-5 rounded-2xl border border-slate-200/80">
            {/* Custo Atual */}
            <div className="flex-1 flex flex-col p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
              <div className="flex items-center justify-between text-slate-500 mb-1">
                <span className="text-xs uppercase font-semibold text-slate-500">Custo Atual</span>
                <span className="text-[11px] px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-medium capitalize">
                  {formData.modalidadeAtual}
                </span>
              </div>
              <span className="font-mono-num text-xl sm:text-2xl font-bold text-slate-800 mt-1">
                {formatCurrency(audit.custoAtual)}
              </span>
              <span className="text-xs text-slate-500 mt-1">Tarifa monômia A4</span>
            </div>

            {/* Seta Transição */}
            <div className="hidden sm:flex items-center justify-center w-9 h-9 rounded-full bg-gradient-to-r from-amber-400 to-yellow-400 text-slate-950 font-bold shrink-0 self-center shadow-xs">
              <ArrowRight className="w-5 h-5 font-bold" />
            </div>

            {/* Novo Custo Otimizado */}
            <div className="flex-1 flex flex-col p-4 rounded-xl bg-emerald-50/50 border border-emerald-300 shadow-2xs relative overflow-hidden">
              <div className="flex items-center justify-between text-emerald-950 mb-1 relative z-10">
                <span className="text-xs uppercase font-bold text-emerald-900">Novo Custo</span>
                <span className="text-[11px] px-2 py-0.5 rounded bg-emerald-600 text-white font-bold shadow-2xs">
                  Verde
                </span>
              </div>
              <span className="font-mono-num text-xl sm:text-2xl font-bold text-emerald-700 mt-1 relative z-10">
                {formatCurrency(audit.novoCusto)}
              </span>
              <span className="text-xs text-emerald-800 font-semibold mt-1 relative z-10">
                Economia Imediata
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* SEÇÃO 1: RESULTADO DOS VALORES CALCULADOS & DESCRIÇÃO DETALHADA */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 shadow-sm border border-slate-200/80 flex flex-col gap-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200/80">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-100 border border-amber-300 flex items-center justify-center text-amber-800 shrink-0">
              <Receipt className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-bold text-slate-900">
                Fatura Demonstrativa Otimizada (Tarifa Horária Verde)
              </h2>
              <p className="text-xs text-slate-500">
                Detalhamento técnico regulatório dos componentes tarifários homologados pela ANEEL
              </p>
            </div>
          </div>
          <span className="text-xs bg-amber-100 text-amber-900 border border-amber-300 px-3 py-1 rounded-full font-bold self-start sm:self-center">
            Estrutura Subgrupo {audit.subgrupo} • {audit.sigAgente}
          </span>
        </div>

        {/* Tabela Estruturada de Linhas Faturadas */}
        <div className="overflow-x-auto">
          <div className="min-w-[820px] flex flex-col divide-y divide-slate-100">
            {/* Header da Tabela */}
            <div className="grid grid-cols-12 gap-3 pb-3 text-slate-500 text-xs uppercase tracking-wider font-semibold px-3 items-center">
              <div className="col-span-4">Item Faturado &amp; Descrição Técnica</div>
              <div className="col-span-2 text-right">Base / Consumo</div>
              <div className="col-span-2 text-right">Tarifa Unit. s/ Tributo</div>
              <div className="col-span-2 text-right text-slate-800 font-bold">Tarifa Unit. c/ Tributo</div>
              <div className="col-span-2 text-right">Valor Total (R$)</div>
            </div>

            {/* Linhas */}
            {audit.breakdown.map((row, idx) => (
              <div
                key={idx}
                className="grid grid-cols-12 gap-3 py-3.5 px-3 items-center hover:bg-slate-50/80 rounded-xl transition-colors"
              >
                <div className="col-span-4 flex flex-col pr-2">
                  <div className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${row.dotColor}`}></span>
                    <span className="text-sm font-semibold text-slate-900">{row.descricao}</span>
                  </div>
                  <span className="text-xs text-slate-500 mt-0.5 pl-4.5">{row.subtitulo}</span>
                </div>
                <div className="col-span-2 text-right font-mono-num text-sm text-slate-800 font-medium">
                  {row.baseConsumo}
                </div>
                <div className="col-span-2 text-right font-mono-num text-xs sm:text-sm text-slate-600">
                  {row.tarifaSemTributo}
                </div>
                <div className="col-span-2 text-right font-mono-num text-xs sm:text-sm text-emerald-700 font-semibold">
                  {row.tarifaComTributo}
                </div>
                <div className="col-span-2 text-right font-mono-num text-sm font-bold text-slate-900">
                  {row.valorTotal}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Totalizador Final em Destaque da Tabela */}
        <div className="p-5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold shadow-2xs shrink-0">
              <Check className="w-5 h-5 stroke-[2.5]" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold text-slate-900">
                Valor Total da Fatura Otimizada
              </span>
              <span className="text-xs text-slate-500">
                Período regular de faturamento mensal apurado
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:items-end">
            <div className="flex items-baseline gap-2">
              <span className="font-mono-num text-2xl sm:text-3xl font-extrabold text-slate-900">
                {formatCurrency(audit.totalOtimizado)}
              </span>
              <span className="text-xs text-slate-500">/ mês</span>
            </div>
            <span className="text-xs text-emerald-700 font-bold mt-0.5">
              Economia apurada de {formatCurrency(audit.economiaMensal)} vs modalidade atual
            </span>
          </div>
        </div>

        {/* Barra Visual de Proporção e Composição */}
        <div className="flex flex-col gap-2 pt-2">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span className="uppercase font-semibold tracking-wider">
              Composição Regulamentada do Custo Total
            </span>
            <span className="font-mono-num font-medium text-slate-600">100% Auditado</span>
          </div>

          {/* Barra Segmentada */}
          <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden flex shadow-inner">
            <div
              className="h-full bg-blue-600 transition-all duration-500"
              style={{ width: `${audit.composicao.energiaPct}%` }}
              title={`Energia (TE): ${audit.composicao.energiaPct}%`}
            ></div>
            <div
              className="h-full bg-slate-600 transition-all duration-500"
              style={{ width: `${audit.composicao.tusdPct}%` }}
              title={`Distribuição (TUSD Rede): ${audit.composicao.tusdPct}%`}
            ></div>
            <div
              className="h-full bg-slate-400 transition-all duration-500"
              style={{ width: `${audit.composicao.tributosPct}%` }}
              title={`Tributos Regulatórios: ${audit.composicao.tributosPct}%`}
            ></div>
          </div>

          {/* Legenda da Composição */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-1.5">
            <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 border border-slate-200">
              <span className="w-3 h-3 rounded-xs bg-blue-600 shrink-0"></span>
              <span className="text-xs text-slate-700">
                Energia (TE):{' '}
                <strong className="text-slate-900 font-semibold">
                  {audit.composicao.energiaPct}%
                </strong>
              </span>
            </div>

            <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 border border-slate-200">
              <span className="w-3 h-3 rounded-xs bg-slate-600 shrink-0"></span>
              <span className="text-xs text-slate-700">
                TUSD Rede:{' '}
                <strong className="text-slate-900 font-semibold">
                  {audit.composicao.tusdPct}%
                </strong>
              </span>
            </div>

            <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 border border-slate-200">
              <span className="w-3 h-3 rounded-xs bg-slate-400 shrink-0"></span>
              <span className="text-xs text-slate-700">
                Tributos:{' '}
                <strong className="text-slate-900 font-semibold">
                  {audit.composicao.tributosPct}%
                </strong>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* SEÇÃO 2: COMPARATIVO ENTRE AS MODALIDADES TARIFÁRIAS */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 shadow-sm border border-slate-200/80 flex flex-col gap-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-200/80">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-100 border border-amber-300 flex items-center justify-center text-amber-800 shrink-0">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-bold text-slate-900">
                Comparativo de Cenários Tarifários (Regulamentação ANEEL)
              </h2>
              <p className="text-xs text-slate-500">
                Avaliação comparativa das modalidades aplicáveis ao perfil de carga da sua unidade
              </p>
            </div>
          </div>
          <span className="text-xs bg-amber-100 text-amber-900 border border-amber-300 px-3 py-1 rounded-full w-fit font-bold">
            Subgrupo {audit.subgrupo} (2,3 kV a 25 kV)
          </span>
        </div>

        {/* PAINEL COMPARATIVO AMPLIADO COM GRÁFICOS EXECUTIVOS DE GRANDE ESCALA E TE × TUSD */}
        <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200/90 shadow-xs flex flex-col gap-10">
          {/* Header Superior com Abas e Filtros */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 pb-6 border-b border-slate-200">
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-amber-400 to-yellow-400 flex items-center justify-center text-slate-950 font-black shadow-md shadow-amber-500/25 shrink-0">
                <BarChart3 className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight">
                    Auditoria Comparativa dos Cenários Tarifários ANEEL
                  </h3>
                  <span className="text-[11px] bg-amber-100 text-amber-900 px-2.5 py-0.5 rounded-full font-bold border border-amber-300">
                    Regulamentação REN 1.000/2021
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
                  Simulação detalhada das faturas mensais, partição técnica de TE (Energia) e TUSD (Rede/Demanda)
                </p>
              </div>
            </div>

            {/* Controles de Navegação entre Visões */}
            <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-xl border border-slate-200 self-start lg:self-auto flex-wrap">
              <button
                type="button"
                onClick={() => setComparativoTab('todos')}
                className={`px-3.5 py-1.5 rounded-lg text-xs transition-all cursor-pointer ${
                  comparativoTab === 'todos'
                    ? 'bg-gradient-to-r from-amber-400 to-yellow-400 text-slate-950 font-black shadow-sm border border-amber-400'
                    : 'text-slate-600 hover:text-slate-900 font-semibold'
                }`}
              >
                Visão Completa
              </button>
              <button
                type="button"
                onClick={() => setComparativoTab('te_tusd')}
                className={`px-3.5 py-1.5 rounded-lg text-xs transition-all cursor-pointer flex items-center gap-1.5 ${
                  comparativoTab === 'te_tusd'
                    ? 'bg-gradient-to-r from-amber-400 to-yellow-400 text-slate-950 font-black shadow-sm border border-amber-400'
                    : 'text-slate-600 hover:text-slate-900 font-semibold'
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>TE vs TUSD</span>
              </button>
              <button
                type="button"
                onClick={() => setComparativoTab('custos')}
                className={`px-3.5 py-1.5 rounded-lg text-xs transition-all cursor-pointer ${
                  comparativoTab === 'custos'
                    ? 'bg-gradient-to-r from-amber-400 to-yellow-400 text-slate-950 font-black shadow-sm border border-amber-400'
                    : 'text-slate-600 hover:text-slate-900 font-semibold'
                }`}
              >
                Custo Total
              </button>
              <button
                type="button"
                onClick={() => setComparativoTab('matriz')}
                className={`px-3.5 py-1.5 rounded-lg text-xs transition-all cursor-pointer ${
                  comparativoTab === 'matriz'
                    ? 'bg-gradient-to-r from-amber-400 to-yellow-400 text-slate-950 font-black shadow-sm border border-amber-400'
                    : 'text-slate-600 hover:text-slate-900 font-semibold'
                }`}
              >
                Matriz ANEEL
              </button>
            </div>
          </div>

          {/* Cards Rápidos de Indicadores Executivos */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-gradient-to-br from-amber-50 via-yellow-50/50 to-white border-2 border-amber-400 shadow-xs flex flex-col justify-between">
              <span className="text-xs uppercase font-extrabold text-amber-900 tracking-wider">
                Melhor Fatura Regulada
              </span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="font-mono-num text-2xl font-black text-amber-950">
                  {formatCurrency(audit.custoVerde)}
                </span>
                <span className="text-xs text-amber-700 font-semibold">/ mês</span>
              </div>
              <span className="text-xs text-amber-800 mt-1 font-semibold">
                Tarifa Horária Verde homologada
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-50 via-green-50/40 to-white border-2 border-emerald-400 shadow-xs flex flex-col justify-between">
              <span className="text-xs uppercase font-extrabold text-emerald-950 tracking-wider">
                Economia Mensal Imediata
              </span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="font-mono-num text-2xl font-black text-emerald-700">
                  {formatCurrency(audit.economiaMensal)}
                </span>
                <span className="text-xs bg-emerald-100 text-emerald-800 border border-emerald-300 px-2 py-0.5 rounded-full font-bold">
                  -{formatNumber(audit.economiaPercentual, 1)}%
                </span>
              </div>
              <span className="text-xs text-slate-600 mt-1 font-medium">
                Redução direta vs modalidade atual
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-amber-50/60 border border-amber-200 flex flex-col justify-between">
              <span className="text-xs uppercase font-bold text-amber-900 tracking-wider">
                Economia Anual Projetada
              </span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="font-mono-num text-2xl font-bold text-amber-950">
                  {formatCurrency(audit.economiaAnual)}
                </span>
                <span className="text-xs text-amber-700 font-medium">/ ano</span>
              </div>
              <span className="text-xs text-slate-500 mt-1 font-medium">
                Sem custos com obras ou equipamentos
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-yellow-50/60 border border-yellow-200 flex flex-col justify-between">
              <span className="text-xs uppercase font-bold text-amber-900 tracking-wider">
                Eficiência no Fio (TUSD)
              </span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="font-mono-num text-2xl font-bold text-slate-900">
                  {formatCurrency(Math.max(0, audit.custoAzul - audit.custoVerde))}
                </span>
                <span className="text-xs text-slate-500 font-medium">a menos vs Azul</span>
              </div>
              <span className="text-xs text-slate-500 mt-1 font-medium">
                Demanda única de {audit.demandaFaturavelKw} kW sem ponta
              </span>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* SEÇÃO 1: GRANDE GRÁFICO DE TE × TUSD POR MODALIDADE */}
          {/* ========================================================================= */}
          {(comparativoTab === 'todos' || comparativoTab === 'te_tusd') && (
            <div className="p-6 sm:p-8 rounded-3xl bg-slate-50/60 border border-slate-200 flex flex-col gap-8 shadow-xs">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-100 border border-amber-300 flex items-center justify-center text-amber-800 shrink-0">
                    <Layers className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-base sm:text-lg font-bold text-slate-900">
                      Gráfico Comparativo de TE (Energia) × TUSD (Rede / Distribuição)
                    </h4>
                    <p className="text-xs sm:text-sm text-slate-500">
                      Comparação simultânea dos componentes faturados de geração (TE) vs infraestrutura e demanda (TUSD)
                    </p>
                  </div>
                </div>

                {/* Legenda de TE e TUSD */}
                <div className="flex items-center gap-5 text-xs font-semibold bg-white px-4 py-2 rounded-xl border border-slate-200 shadow-2xs self-start md:self-auto">
                  <div className="flex items-center gap-2">
                    <span className="w-3.5 h-3.5 rounded-md bg-amber-400 shrink-0 shadow-2xs"></span>
                    <span className="text-slate-800 font-bold">TE (Tarifa de Energia / Geração)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-3.5 h-3.5 rounded-md bg-blue-600 shrink-0 shadow-2xs"></span>
                    <span className="text-slate-800 font-bold">TUSD (Uso da Rede / Demanda)</span>
                  </div>
                </div>
              </div>

              {/* GRANDE GRÁFICO DE BARRAS AGRUPADAS TE × TUSD COM EIXO Y E GRIDLINES */}
              <div className="flex flex-col bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs uppercase font-bold text-slate-600 tracking-wider">
                    Comparativo Lado a Lado: TE vs TUSD (em R$ mensais)
                  </span>
                  <span className="text-xs text-slate-500 font-mono-num font-semibold">
                    Escala máxima: {formatCurrency(yTeTusdMax)}
                  </span>
                </div>

                {/* Canvas do Gráfico (Altura Ampliada: h-80 sm:h-96) */}
                <div className="relative w-full h-80 sm:h-96 flex items-stretch">
                  {/* Eixo Y com Marcas e Linhas Tracejadas */}
                  <div className="w-16 sm:w-20 flex flex-col justify-between text-right pr-3 font-mono-num text-[11px] font-bold text-slate-500 border-r border-slate-300 py-1 select-none">
                    {yTeTusdTicks.map((tick, i) => (
                      <span key={i} className="leading-none">
                        R$ {(tick / 1000).toFixed(1)}k
                      </span>
                    ))}
                  </div>

                  {/* Área de Plotagem com Gridlines de Fundo */}
                  <div className="relative flex-1 flex flex-col justify-between pl-4 sm:pl-8 pr-2 sm:pr-4 py-1">
                    {/* Linhas de Grade de Fundo */}
                    <div className="absolute inset-0 flex flex-col justify-between pointer-events-none pl-4 sm:pl-8 pr-2 sm:pr-4 py-1">
                      {yTeTusdTicks.map((_, i) => (
                        <div
                          key={i}
                          className="w-full border-b border-dashed border-slate-200"
                        ></div>
                      ))}
                    </div>

                    {/* Colunas do Gráfico Agrupadas por Modalidade */}
                    <div className="relative z-10 w-full h-full flex items-end justify-around gap-3 sm:gap-6">
                      {audit.comparativoTeTusd.map((mod) => {
                        const teHeightPct = Math.max(8, Math.min(100, Math.round((mod.teValor / yTeTusdMax) * 100)));
                        const tusdHeightPct = Math.max(8, Math.min(100, Math.round((mod.tusdValor / yTeTusdMax) * 100)));

                        return (
                          <div
                            key={mod.key}
                            className="flex flex-col items-center h-full justify-end flex-1 max-w-[140px] sm:max-w-[180px]"
                          >
                            {/* Dupla de Colunas TE e TUSD */}
                            <div className="flex items-end justify-center gap-1.5 sm:gap-2.5 w-full h-full pb-2">
                              {/* Coluna TE */}
                              <div className="w-1/2 flex flex-col items-center h-full justify-end group cursor-default">
                                <div className="mb-1.5 text-center flex flex-col items-center">
                                  <span className="font-mono-num text-[10px] sm:text-xs font-bold text-amber-950 bg-amber-100 border border-amber-300 px-1 sm:px-1.5 py-0.5 rounded shadow-2xs">
                                    {formatCurrency(mod.teValor)}
                                  </span>
                                  <span className="text-[9px] sm:text-[10px] text-amber-800 font-bold mt-0.5">
                                    TE {mod.tePct}%
                                  </span>
                                </div>
                                <div
                                  className="w-full bg-gradient-to-t from-amber-500 to-yellow-400 hover:from-amber-400 hover:to-yellow-300 rounded-t-lg transition-colors shadow-2xs"
                                  style={{ height: `${teHeightPct}%` }}
                                ></div>
                              </div>

                              {/* Coluna TUSD */}
                              <div className="w-1/2 flex flex-col items-center h-full justify-end group cursor-default">
                                <div className="mb-1.5 text-center flex flex-col items-center">
                                  <span className="font-mono-num text-[10px] sm:text-xs font-bold text-blue-950 bg-blue-50 border border-blue-200 px-1 sm:px-1.5 py-0.5 rounded shadow-2xs">
                                    {formatCurrency(mod.tusdValor)}
                                  </span>
                                  <span className="text-[9px] sm:text-[10px] text-blue-700 font-semibold mt-0.5">
                                    TUSD {mod.tusdPct}%
                                  </span>
                                </div>
                                <div
                                  className="w-full bg-blue-600 hover:bg-blue-500 rounded-t-lg transition-colors shadow-2xs"
                                  style={{ height: `${tusdHeightPct}%` }}
                                ></div>
                              </div>
                            </div>

                            {/* Identificação da Modalidade no Rodapé do Eixo X */}
                            <div className="w-full pt-3 border-t-2 border-slate-300 text-center flex flex-col items-center gap-1">
                              <span className="text-xs sm:text-sm font-bold text-slate-900 leading-tight">
                                {mod.key === 'verde'
                                  ? 'Tarifa Verde'
                                  : mod.key === 'azul'
                                  ? 'Tarifa Azul'
                                  : mod.key === 'convencional'
                                  ? 'Convencional'
                                  : 'Mercado Livre'}
                              </span>
                              {mod.tag && (
                                <span
                                  className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${mod.tagColor || 'bg-slate-100 text-slate-700'}`}
                                >
                                  {mod.tag}
                                </span>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>

              {/* BARRAS HORIZONTAIS SEGMENTADAS DE GRANDE ESCALA */}
              <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs uppercase font-bold text-slate-700 tracking-wider">
                    Detalhamento de Proporção TE × TUSD no Custo Total
                  </span>
                  <span className="text-xs text-slate-500 font-medium">
                    100% da Fatura Mensal Decomposta
                  </span>
                </div>

                <div className="flex flex-col gap-4">
                  {audit.comparativoTeTusd.map((mod) => (
                    <div
                      key={mod.key}
                      className="p-5 rounded-2xl bg-white border border-slate-200/90 shadow-2xs flex flex-col gap-3.5 hover:border-slate-300 transition-colors"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div className="flex items-center gap-2.5 flex-wrap">
                          <span className="text-sm sm:text-base font-bold text-slate-900">
                            {mod.nome}
                          </span>
                          {mod.tag && (
                            <span
                              className={`text-[10px] px-2.5 py-0.5 rounded-full font-semibold ${mod.tagColor || 'bg-slate-100 text-slate-700'}`}
                            >
                              {mod.tag}
                            </span>
                          )}
                        </div>

                        <div className="flex items-baseline gap-1.5">
                          <span className="text-xs text-slate-500 font-medium">Fatura Total:</span>
                          <span className="font-mono-num text-base sm:text-lg font-bold text-slate-900">
                            {formatCurrency(mod.custoTotal)}
                          </span>
                          <span className="text-xs text-slate-500">/ mês</span>
                        </div>
                      </div>

                      {/* Barra Segmentada Grande (h-11 sm:h-12) */}
                      <div className="w-full h-11 sm:h-12 bg-slate-100 rounded-xl overflow-hidden flex shadow-inner p-1 border border-slate-200/80">
                        {/* Segmento TE */}
                        <div
                          className="h-full bg-gradient-to-r from-amber-400 via-amber-400 to-yellow-400 flex items-center justify-center text-xs sm:text-sm font-black text-slate-950 transition-all duration-500 rounded-l-lg px-3 overflow-hidden shadow-2xs"
                          style={{ width: `${mod.tePct}%` }}
                        >
                          <span className="truncate">
                            TE {mod.tePct}% · {formatCurrency(mod.teValor)}
                          </span>
                        </div>
                        {/* Segmento TUSD */}
                        <div
                          className="h-full bg-blue-600 flex items-center justify-center text-xs sm:text-sm font-bold text-white transition-all duration-500 rounded-r-lg px-3 overflow-hidden shadow-2xs"
                          style={{ width: `${mod.tusdPct}%` }}
                        >
                          <span className="truncate">
                            TUSD {mod.tusdPct}% · {formatCurrency(mod.tusdValor)}
                          </span>
                        </div>
                      </div>

                      {/* Explicação Regulatória Técnica */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-2 border-t border-slate-100 text-xs">
                        <div className="flex items-center gap-3">
                          <span className="inline-flex items-center gap-1.5 font-medium text-slate-700">
                            <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                            Energia (TE):{' '}
                            <strong className="text-slate-900 font-mono-num font-semibold">
                              {formatCurrency(mod.teValor)}
                            </strong>{' '}
                            ({mod.tePct}%)
                          </span>
                          <span className="text-slate-300">•</span>
                          <span className="inline-flex items-center gap-1.5 font-medium text-slate-700">
                            <span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
                            Rede &amp; Demanda (TUSD):{' '}
                            <strong className="text-slate-900 font-mono-num font-semibold">
                              {formatCurrency(mod.tusdValor)}
                            </strong>{' '}
                            ({mod.tusdPct}%)
                          </span>
                        </div>
                        <span className="text-xs text-slate-500 italic">{mod.descricaoRegulatoria}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* SEÇÃO 2: GRANDE GRÁFICO DE CUSTO MENSAL TOTAL */}
          {/* ========================================================================= */}
          {(comparativoTab === 'todos' || comparativoTab === 'custos') && (
            <div className="p-6 sm:p-8 rounded-3xl bg-slate-50/60 border border-slate-200 flex flex-col gap-8 shadow-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-100 border border-amber-300 flex items-center justify-center text-amber-800 shrink-0">
                    <Sparkles className="w-5 h-5 text-amber-700" />
                  </div>
                  <div>
                    <h4 className="text-base sm:text-lg font-bold text-slate-900">
                      Comparativo de Custo Total da Fatura por Modalidade
                    </h4>
                    <p className="text-xs sm:text-sm text-slate-500">
                      Simulação do valor global mensal faturado pela concessionária em cada enquadramento
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-xs font-semibold text-slate-700">
                  <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-xs bg-emerald-500 shadow-2xs"></span> Tarifa Verde (Recomendada)
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-xs bg-slate-700 shadow-2xs"></span> Tarifa Azul
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-xs bg-slate-400 shadow-2xs"></span> Convencional (Atual)
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-xs bg-slate-200 border border-dashed border-slate-400 shadow-2xs"></span>{' '}
                    Mercado Livre
                  </span>
                </div>
              </div>

              {/* GRANDE GRÁFICO VERTICAL DE CUSTO TOTAL COM EIXO Y E GRIDLINES */}
              <div className="flex flex-col bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs uppercase font-bold text-slate-600 tracking-wider">
                    Valor Faturado Mensal (R$/mês)
                  </span>
                  <span className="text-xs text-slate-500 font-mono-num font-semibold">
                    Escala máxima: {formatCurrency(yCostMax)}
                  </span>
                </div>

                {/* Canvas do Gráfico (Altura Ampliada: h-80 sm:h-96) */}
                <div className="relative w-full h-80 sm:h-96 flex items-stretch">
                  {/* Eixo Y com Marcas e Linhas Tracejadas */}
                  <div className="w-16 sm:w-20 flex flex-col justify-between text-right pr-3 font-mono-num text-[11px] font-bold text-slate-500 border-r border-slate-300 py-1 select-none">
                    {yCostTicks.map((tick, i) => (
                      <span key={i} className="leading-none">
                        R$ {(tick / 1000).toFixed(1)}k
                      </span>
                    ))}
                  </div>

                  {/* Área de Plotagem */}
                  <div className="relative flex-1 flex flex-col justify-between pl-4 sm:pl-8 pr-2 sm:pr-4 py-1">
                    {/* Linhas de Grade de Fundo */}
                    <div className="absolute inset-0 flex flex-col justify-between pointer-events-none pl-4 sm:pl-8 pr-2 sm:pr-4 py-1">
                      {yCostTicks.map((_, i) => (
                        <div
                          key={i}
                          className="w-full border-b border-dashed border-slate-200"
                        ></div>
                      ))}
                    </div>

                    {/* Linha de Benchmark da Tarifa Verde */}
                    <div
                      className="absolute left-0 right-0 border-b-2 border-dashed border-amber-400 pointer-events-none z-20 flex items-center justify-end pr-2"
                      style={{
                        bottom: `${Math.max(8, Math.min(100, Math.round((audit.custoVerde / yCostMax) * 100)))}%`,
                      }}
                    >
                      <span className="text-[10px] font-black uppercase text-amber-950 bg-amber-100 border border-amber-300 px-2 py-0.5 rounded shadow-2xs mb-1">
                        Benchmark Verde: {formatCurrency(audit.custoVerde)}
                      </span>
                    </div>

                    {/* As 4 Colunas Principais */}
                    <div className="relative z-10 w-full h-full flex items-end justify-around gap-4 sm:gap-8">
                      {/* 1. Tarifa Verde */}
                      <div className="flex flex-col items-center h-full justify-end flex-1 max-w-[150px] sm:max-w-[200px]">
                        <div className="mb-2 text-center flex flex-col items-center">
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-gradient-to-r from-amber-400 to-yellow-400 text-slate-950 font-black uppercase tracking-wider mb-1 shadow-2xs">
                            Menor Custo
                          </span>
                          <span className="font-mono-num text-sm sm:text-base font-black text-amber-950 bg-amber-100 border border-amber-300 px-2 py-0.5 rounded-lg shadow-2xs">
                            {formatCurrency(audit.custoVerde)}
                          </span>
                          <span className="text-[11px] font-bold text-emerald-700 mt-1">
                            -{formatNumber(audit.economiaPercentual, 1)}% Economia
                          </span>
                        </div>
                        <div
                          className="w-full bg-gradient-to-t from-emerald-500 to-green-400 hover:from-emerald-400 hover:to-green-300 rounded-t-xl transition-colors shadow-sm"
                          style={{
                            height: `${Math.max(8, Math.min(100, Math.round((audit.custoVerde / yCostMax) * 100)))}%`,
                          }}
                        ></div>
                        <div className="w-full pt-3 border-t-2 border-amber-400 text-center flex flex-col items-center gap-0.5">
                          <span className="text-xs sm:text-sm font-bold text-slate-900">
                            Tarifa Verde
                          </span>
                          <span className="text-[10px] text-amber-950 font-bold bg-amber-100 border border-amber-300 px-2 py-0.5 rounded-full">
                            Demanda Única
                          </span>
                        </div>
                      </div>

                      {/* 2. Tarifa Azul */}
                      <div className="flex flex-col items-center h-full justify-end flex-1 max-w-[150px] sm:max-w-[200px]">
                        <div className="mb-2 text-center flex flex-col items-center">
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-semibold mb-1 border border-slate-200">
                            + {formatCurrency(audit.diferencaAzulVsVerde)}
                          </span>
                          <span className="font-mono-num text-sm sm:text-base font-semibold text-slate-800 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded-lg">
                            {formatCurrency(audit.custoAzul)}
                          </span>
                          <span className="text-[11px] font-medium text-slate-600 mt-1">
                            +{formatNumber((audit.diferencaAzulVsVerde / audit.custoVerde) * 100, 1)}% vs Verde
                          </span>
                        </div>
                        <div
                          className="w-full bg-slate-700 hover:bg-slate-600 rounded-t-xl transition-colors shadow-sm"
                          style={{
                            height: `${Math.max(8, Math.min(100, Math.round((audit.custoAzul / yCostMax) * 100)))}%`,
                          }}
                        ></div>
                        <div className="w-full pt-3 border-t-2 border-slate-300 text-center flex flex-col items-center gap-0.5">
                          <span className="text-xs sm:text-sm font-bold text-slate-900">
                            Tarifa Azul
                          </span>
                          <span className="text-[10px] text-slate-500 font-medium">
                            Demanda Ponta/FP
                          </span>
                        </div>
                      </div>

                      {/* 3. Convencional */}
                      <div className="flex flex-col items-center h-full justify-end flex-1 max-w-[150px] sm:max-w-[200px]">
                        <div className="mb-2 text-center flex flex-col items-center">
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-semibold mb-1 border border-slate-200">
                            Situação Atual
                          </span>
                          <span className="font-mono-num text-sm sm:text-base font-semibold text-slate-800 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded-lg">
                            {formatCurrency(audit.custoConvencional)}
                          </span>
                          <span className="text-[11px] font-semibold text-rose-600 mt-1">
                            +{formatNumber(audit.sobreprecoConvencionalPct, 1)}% Sobrecusto
                          </span>
                        </div>
                        <div
                          className="w-full bg-slate-400 hover:bg-slate-300 rounded-t-xl transition-colors shadow-sm"
                          style={{
                            height: `${Math.max(8, Math.min(100, Math.round((audit.custoConvencional / yCostMax) * 100)))}%`,
                          }}
                        ></div>
                        <div className="w-full pt-3 border-t-2 border-slate-300 text-center flex flex-col items-center gap-0.5">
                          <span className="text-xs sm:text-sm font-bold text-slate-900">
                            Convencional
                          </span>
                          <span className="text-[10px] text-slate-500 font-medium">
                            Monômia Sem Horário
                          </span>
                        </div>
                      </div>

                      {/* 4. Mercado Livre (ACL) */}
                      <div className="flex flex-col items-center h-full justify-end flex-1 max-w-[150px] sm:max-w-[200px]">
                        <div className="mb-2 text-center flex flex-col items-center">
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 font-semibold mb-1 border border-indigo-200">
                            Viabilidade Futura
                          </span>
                          <span className="font-mono-num text-sm sm:text-base font-semibold text-slate-800 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded-lg">
                            {formatCurrency(audit.custoACL)}
                          </span>
                          <span className="text-[11px] font-semibold text-emerald-700 mt-1">
                            -38,1% vs Atual
                          </span>
                        </div>
                        <div
                          className="w-full bg-slate-100 border-2 border-dashed border-indigo-400 hover:bg-indigo-50/50 rounded-t-xl transition-colors shadow-2xs"
                          style={{
                            height: `${Math.max(8, Math.min(100, Math.round((audit.custoACL / yCostMax) * 100)))}%`,
                          }}
                        ></div>
                        <div className="w-full pt-3 border-t-2 border-slate-300 text-center flex flex-col items-center gap-0.5">
                          <span className="text-xs sm:text-sm font-bold text-slate-800">
                            Mercado Livre
                          </span>
                          <span className="text-[10px] text-slate-500 font-medium">
                            Ambiente Livre (ACL)
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* SEÇÃO 3: MATRIZ TÉCNICA COMPARATIVA (TABELA REGULATÓRIA ANEEL) */}
          {/* ========================================================================= */}
          {(comparativoTab === 'todos' || comparativoTab === 'matriz') && (
            <div className="flex flex-col gap-4 pt-2 border-t border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                    Matriz Técnica Regulamentar ANEEL: Demanda, TE e TUSD por Cenário
                  </h4>
                  <p className="text-xs text-slate-500">
                    Demonstrativo auditado das regras de tarifação de potência e energia homologadas
                  </p>
                </div>
                <span className="text-xs font-bold bg-amber-100 text-amber-900 px-3 py-1 rounded-full border border-amber-300">
                  Subgrupo {audit.subgrupo} • {audit.sigAgente}
                </span>
              </div>

              <div className="overflow-x-auto rounded-2xl border border-slate-200 shadow-2xs">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-100/80 text-slate-700 uppercase font-bold tracking-wider border-b border-slate-200">
                    <tr>
                      <th className="py-3.5 px-4">Modalidade</th>
                      <th className="py-3.5 px-4">Regra de Demanda de Potência</th>
                      <th className="py-3.5 px-4 text-right">Parcela TE (R$)</th>
                      <th className="py-3.5 px-4 text-right">Parcela TUSD (R$)</th>
                      <th className="py-3.5 px-4 text-right">Fatura Total (R$)</th>
                      <th className="py-3.5 px-4 text-right">Impacto Financeiro</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 bg-white">
                    <tr className="bg-amber-50/70 font-semibold border-l-4 border-l-amber-500">
                      <td className="py-4 px-4">
                        <span className="font-extrabold text-amber-950 flex items-center gap-2">
                          <Check className="w-4 h-4 text-amber-600 stroke-[2.5]" />
                          Tarifa Horária Verde (Recomendada)
                        </span>
                      </td>
                      <td className="py-4 px-4 text-slate-800">
                        Demanda única faturável ({audit.demandaFaturavelKw} kW) sem sobretaxa na ponta
                      </td>
                      <td className="py-4 px-4 text-right font-mono-num text-slate-900 font-bold">
                        {formatCurrency(audit.comparativoTeTusd[0]?.teValor || 0)}
                      </td>
                      <td className="py-4 px-4 text-right font-mono-num text-slate-900 font-bold">
                        {formatCurrency(audit.comparativoTeTusd[0]?.tusdValor || 0)}
                      </td>
                      <td className="py-4 px-4 text-right font-mono-num font-black text-amber-950 text-sm">
                        {formatCurrency(audit.custoVerde)}
                      </td>
                      <td className="py-4 px-4 text-right">
                        <span className="px-2.5 py-1 rounded-full bg-amber-100 text-amber-900 border border-amber-300 font-bold text-[11px] shadow-2xs">
                          Menor Custo Regulado
                        </span>
                      </td>
                    </tr>
                    <tr className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-bold text-slate-900">Tarifa Horária Azul</td>
                      <td className="py-3.5 px-4 text-slate-600">
                        Obriga contratação de demanda segregada (Ponta e Fora Ponta)
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono-num text-slate-700 font-semibold">
                        {formatCurrency(audit.comparativoTeTusd[1]?.teValor || 0)}
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono-num text-slate-700 font-semibold">
                        {formatCurrency(audit.comparativoTeTusd[1]?.tusdValor || 0)}
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono-num font-bold text-slate-900">
                        {formatCurrency(audit.custoAzul)}
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono-num text-rose-600 font-bold">
                        + {formatCurrency(audit.diferencaAzulVsVerde)}
                      </td>
                    </tr>
                    <tr className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-bold text-slate-900">Tarifa Convencional (Atual)</td>
                      <td className="py-3.5 px-4 text-slate-600">
                        Tarifa linear monômia sem distinção de horário de consumo
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono-num text-slate-700 font-semibold">
                        {formatCurrency(audit.comparativoTeTusd[2]?.teValor || 0)}
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono-num text-slate-700 font-semibold">
                        {formatCurrency(audit.comparativoTeTusd[2]?.tusdValor || 0)}
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono-num font-bold text-slate-900">
                        {formatCurrency(audit.custoConvencional)}
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono-num text-rose-600 font-bold">
                        + {formatCurrency(audit.economiaMensal)}
                      </td>
                    </tr>
                    <tr className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-bold text-slate-900">Mercado Livre de Energia (ACL)</td>
                      <td className="py-3.5 px-4 text-slate-600">
                        Contratação bilateral livre de TE + TUSD Fio regulado ANEEL
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono-num text-slate-800 font-semibold">
                        {formatCurrency(audit.comparativoTeTusd[3]?.teValor || 0)}
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono-num text-slate-700 font-semibold">
                        {formatCurrency(audit.comparativoTeTusd[3]?.tusdValor || 0)}
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono-num font-bold text-slate-900">
                        {formatCurrency(audit.custoACL)}
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono-num text-emerald-700 font-bold">
                        - {formatCurrency(Math.max(0, audit.custoVerde - audit.custoACL))} (ACL)
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* CARDS COMPARATIVOS COMPLEMENTARES EM GRID 4 COLUNAS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Verde (Recomendada) */}
          <div className="p-5 rounded-2xl bg-gradient-to-b from-amber-50/70 via-yellow-50/30 to-white border-2 border-amber-400 flex flex-col justify-between gap-3 shadow-md shadow-amber-400/10">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase font-extrabold text-amber-900 tracking-wider">
                  Tarifa Verde
                </span>
                <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-gradient-to-r from-amber-400 to-yellow-400 text-slate-950 font-black shadow-2xs">
                  Recomendada
                </span>
              </div>
              <span className="font-mono-num text-2xl font-black text-amber-950">
                {formatCurrency(audit.custoVerde)}
              </span>
              <p className="text-xs text-slate-600 leading-relaxed">
                Ideal para o perfil da empresa:{' '}
                {formatNumber(audit.consumoForaPontaPercentual, 1)}% do consumo ocorre fora de ponta
                e conta com demanda tarifada única sem sobretaxas.
              </p>
            </div>
            <span className="text-xs text-amber-900 font-bold flex items-center gap-1.5 mt-1 pt-2 border-t border-amber-100">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Economia imediata garantida
            </span>
          </div>

          {/* Card 2: Azul */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 flex flex-col justify-between gap-3 shadow-2xs hover:shadow-xs transition-shadow">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase font-semibold text-slate-800">Tarifa Azul</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-semibold border border-slate-200">
                  Desfavorável
                </span>
              </div>
              <span className="font-mono-num text-2xl font-bold text-slate-900">
                {formatCurrency(audit.custoAzul)}
              </span>
              <p className="text-xs text-slate-600 leading-relaxed">
                Penalizada pela contratação obrigatória de demanda diferenciada no posto de ponta
                com custo unitário elevado.
              </p>
            </div>
            <span className="text-xs text-slate-600 flex items-center gap-1.5 mt-1 pt-2 border-t border-slate-100 font-medium">
              <Info className="w-4 h-4 text-slate-400" /> + {formatCurrency(audit.diferencaAzulVsVerde)} vs Verde
            </span>
          </div>

          {/* Card 3: Convencional */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 flex flex-col justify-between gap-3 shadow-2xs hover:shadow-xs transition-shadow">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase font-semibold text-slate-700">Convencional</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-semibold border border-slate-200">
                  Atual
                </span>
              </div>
              <span className="font-mono-num text-2xl font-bold text-slate-900">
                {formatCurrency(audit.custoConvencional)}
              </span>
              <p className="text-xs text-slate-600 leading-relaxed">
                Tarifa monômia desvantajosa: o cliente paga a mesma tarifa em todas as horas, sem se
                beneficiar da folga fora de ponta.
              </p>
            </div>
            <span className="text-xs text-rose-600 font-semibold flex items-center gap-1.5 mt-1 pt-2 border-t border-slate-100">
              <AlertTriangle className="w-4 h-4 text-rose-500" /> +{formatNumber(audit.sobreprecoConvencionalPct, 1)}% de sobrepreço
            </span>
          </div>

          {/* Card 4: Mercado Livre (ACL) */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 flex flex-col justify-between gap-3 shadow-2xs hover:shadow-xs transition-shadow">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase font-semibold text-slate-800">Mercado Livre</span>
                <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold">
                  Viabilidade Futura
                </span>
              </div>
              <span className="font-mono-num text-2xl font-bold text-slate-900">
                {formatCurrency(audit.custoACL)}
              </span>
              <p className="text-xs text-slate-600 leading-relaxed">
                Elegível via Portaria Normativa nº 50/2022. Possibilidade de negociação bilateral
                livre e redução de até 38% nos custos.
              </p>
            </div>
            <span className="text-xs text-slate-700 font-semibold flex items-center gap-1.5 mt-1 pt-2 border-t border-slate-100">
              <TrendingUp className="w-4 h-4 text-slate-500" /> Migração planejada
            </span>
          </div>
        </div>
      </div>

      {/* AÇÕES DE NAVEGAÇÃO NO RODAPÉ */}
      <div className="w-full bg-white rounded-2xl p-5 shadow-sm border border-slate-200/80 flex items-center justify-between gap-4 no-print">
        <button
          onClick={onBackToEdit}
          type="button"
          className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition-all duration-200 border border-slate-200/80 cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Voltar e Ajustar Dados</span>
        </button>
      </div>
    </div>
  );
};
