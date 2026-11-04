import React from 'react';
import {
  Building2,
  Gauge,
  Sparkles,
  ArrowRight,
  Lock,
  ChevronDown,
  Zap,
  Activity,
  Receipt,
  Calendar,
} from 'lucide-react';
import {
  InvoiceFormData,
  TariffModalidade,
  TipoICMS,
} from '../types/energy';
import {
  DISTRIBUTORS,
  SUBGROUPS,
  MODALIDADE_OPTIONS,
  formatNumber,
} from '../utils/calculator';
import { bandeiraApiParaForm } from '../lib/api';

interface StepOneFormProps {
  formData: InvoiceFormData;
  onChange: (data: InvoiceFormData) => void;
  onSubmit: () => void;
  onFillExample: () => void;
  carregando?: boolean;
  /** Listas dinâmicas vindas da API (null = fallback para as estáticas). */
  distribuidorasApi?: string[] | null;
  subgruposApi?: string[] | null;
  classesApi?: string[] | null;
  bandeirasApi?: { bandeira: string; valor_kwh: number }[] | null;
  bandeiraAtivaApi?: string | null;
}

export const StepOneForm: React.FC<StepOneFormProps> = ({
  formData,
  onChange,
  onSubmit,
  onFillExample,
  carregando = false,
  distribuidorasApi = null,
  subgruposApi = null,
  classesApi = null,
  bandeirasApi = null,
  bandeiraAtivaApi = null,
}) => {
  // Valores calculados dinamicamente para exibição no Passo 1
  const consumoTotalCiclo =
    formData.consumoPonta + formData.consumoForaPonta + formData.consumoIntermediario;

  // Distribuidoras e subgrupos: dados reais da API quando disponíveis.
  const opcoesDistribuidora = distribuidorasApi ?? DISTRIBUTORS.map((d) => d.sigAgente);
  const opcoesSubgrupo =
    subgruposApi && subgruposApi.length > 0
      ? subgruposApi.map((id) => ({ id, label: id }))
      : SUBGROUPS;

  // Bandeiras: opções/vigência reais da API quando disponíveis.
  const opcoesBandeira =
    bandeirasApi && bandeirasApi.length > 0
      ? bandeirasApi.map((b) => ({
          id: bandeiraApiParaForm(b.bandeira),
          label: b.bandeira.replace('Vermelha P1', 'Vermelha P1').replace('Vermelha P2', 'Vermelha P2'),
          valorKwh: b.valor_kwh,
        }))
      : ([
          { id: 'verde', label: 'Verde', valorKwh: 0 },
          { id: 'amarela', label: 'Amarela', valorKwh: 0.01874 },
          { id: 'vermelha1', label: 'Vermelha P1', valorKwh: 0.03971 },
          { id: 'vermelha2', label: 'Vermelha P2', valorKwh: 0.09492 },
        ] as const);

  const handleModalidadeClick = (mod: TariffModalidade) => {
    onChange({ ...formData, modalidadeAtual: mod });
  };

  const handleFloatChange = (field: keyof InvoiceFormData, val: string) => {
    const normalized = val.replace(',', '.');
    const num = parseFloat(normalized);
    onChange({ ...formData, [field]: isNaN(num) ? 0 : num });
  };

  const handleIntChange = (field: keyof InvoiceFormData, val: string) => {
    const num = Math.max(0, parseInt(val, 10) || 0);
    onChange({ ...formData, [field]: num });
  };

  const effectiveBandeira = formData.bandeiraAutomatica ? 'verde' : formData.bandeira;

  return (
    <section className="space-y-6 transition-all duration-300 block">
      {/* ========================================================================= */}
      {/* ÁREA DE AÇÕES SUPERIOR (SEPARADA DOS CAMPOS) */}
      {/* ========================================================================= */}
      <div className="bg-white rounded-2xl p-5 sm:p-6 border border-slate-200/90 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-md border border-amber-200/70">
              Simulação
            </span>
          </div>
          <h1 className="font-display text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight mt-1">
            Inserir Dados da Fatura
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Preencha os valores da conta de luz ou importe os parâmetros homologados da unidade.
          </p>
        </div>

        <button
          onClick={onFillExample}
          type="button"
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-amber-400 hover:bg-amber-500 text-slate-950 text-xs sm:text-sm font-bold shadow-xs hover:shadow-sm transition-all cursor-pointer ring-1 ring-amber-300/80 active:scale-95 shrink-0"
        >
          <Sparkles className="w-4 h-4 fill-slate-950/20" />
          <span>Preencher Exemplo Real</span>
        </button>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit();
        }}
        className="space-y-6"
      >
        {/* ========================================================================= */}
        {/* SEÇÃO 1: DISTRIBUIDORA E MODALIDADE */}
        {/* ========================================================================= */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-xs space-y-5">
          <div className="flex items-start gap-3 border-b border-slate-100 pb-4">
            <div className="w-9 h-9 rounded-xl bg-amber-100 text-amber-900 flex items-center justify-center font-bold shrink-0 mt-0.5">
              <Building2 className="w-5 h-5 text-amber-700" />
            </div>
            <div>
              <h2 className="font-display text-base sm:text-lg font-bold text-slate-900">
                1. Distribuidora e Modalidade
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Identificação da unidade consumidora e enquadramento tarifário
              </p>
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-4">
            {/* Distribuidora (expande para ocupar todo o espaço restante) */}
            <div className="flex-1 min-w-0 space-y-1.5">
              <label
                htmlFor="inp-distribuidora"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Distribuidora
              </label>
              <div className="relative">
                <select
                  id="inp-distribuidora"
                  value={formData.distribuidora}
                  onChange={(e) => onChange({ ...formData, distribuidora: e.target.value })}
                  className="w-full h-11 px-3.5 pr-8 bg-slate-50/60 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition-all appearance-none cursor-pointer truncate"
                >
                  {opcoesDistribuidora.map((sigla) => (
                    <option key={sigla} value={sigla}>
                      {sigla}
                    </option>
                  ))}
                </select>
                <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-3.5 pointer-events-none" />
              </div>
              <p className="text-[10px] text-slate-400">
                {distribuidorasApi ? 'Lista carregada da API (GET /api/distribuidoras).' : 'Lista de demonstração (API indisponível).'}
              </p>
            </div>

            {/* Subgrupo */}
            <div className="w-full md:w-64 lg:w-72 shrink-0 space-y-1.5">
              <label
                htmlFor="inp-subgrupo"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Subgrupo
              </label>
              <div className="relative">
                <select
                  id="inp-subgrupo"
                  value={formData.subgrupo}
                  onChange={(e) => onChange({ ...formData, subgrupo: e.target.value })}
                  className="w-full h-11 px-3.5 pr-8 bg-slate-50/60 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition-all appearance-none cursor-pointer truncate"
                >
                  {opcoesSubgrupo.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.label}
                    </option>
                  ))}
                </select>
                <Zap className="w-4 h-4 text-amber-500 absolute right-3 top-3.5 pointer-events-none" />
              </div>
              <p className="text-[10px] text-slate-400">
                {subgruposApi ? 'Lista carregada da API (GET /api/subgrupos).' : 'Lista de demonstração (API indisponível).'}
              </p>
            </div>

            {/* Data de Referência (largura mínima necessária para exibir data, ícone e rótulo sem quebras) */}
            <div className="w-full md:w-48 shrink-0 space-y-1.5">
              <label
                htmlFor="inp-data-ref"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block whitespace-nowrap"
              >
                Data de Referência
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-500 focus-within:border-amber-500 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-data-ref"
                  type="text"
                  value={formData.dataReferencia}
                  onChange={(e) => onChange({ ...formData, dataReferencia: e.target.value })}
                  placeholder="DD/MM/AAAA"
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                />
                <span className="px-3 flex items-center text-slate-400 bg-slate-100/70 border-l border-slate-200 shrink-0">
                  <Calendar className="w-4 h-4" />
                </span>
              </div>
            </div>
          </div>

          {/* Classe / Subclasse / Detalhe — filtros de tarifa do Grupo B */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
            <div className="space-y-1.5">
              <label
                htmlFor="inp-classe"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Classe
              </label>
              <input
                id="inp-classe"
                type="text"
                list="lista-classes-api"
                value={formData.classe}
                onChange={(e) => onChange({ ...formData, classe: e.target.value })}
                placeholder="Não se aplica"
                className="w-full h-11 px-3.5 bg-slate-50/60 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition-all"
              />
              {classesApi && classesApi.length > 0 ? (
                <datalist id="lista-classes-api">
                  {classesApi.map((c) => (
                    <option key={c} value={c} />
                  ))}
                </datalist>
              ) : null}
            </div>
            <div className="space-y-1.5">
              <label
                htmlFor="inp-subclasse"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Subclasse
              </label>
              <input
                id="inp-subclasse"
                type="text"
                value={formData.subclasse}
                onChange={(e) => onChange({ ...formData, subclasse: e.target.value })}
                placeholder="Não se aplica"
                className="w-full h-11 px-3.5 bg-slate-50/60 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label
                htmlFor="inp-detalhe"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Detalhe
              </label>
              <input
                id="inp-detalhe"
                type="text"
                value={formData.detalhe}
                onChange={(e) => onChange({ ...formData, detalhe: e.target.value })}
                placeholder="Não se aplica"
                className="w-full h-11 px-3.5 bg-slate-50/60 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition-all"
              />
            </div>
          </div>
          <p className="text-[11px] text-slate-400">
            Classe/subclasse filtram a tarifa do Grupo B (Optante B, Convencional e Branca). Para
            Residencial/Rural a classe é derivada automaticamente da atividade; sem classe informada e
            com tarifas ambíguas, a API recusa o cálculo (nunca soma tarifas diferentes).
          </p>

          {/* Modalidade */}
          <div className="space-y-2 pt-2 border-t border-slate-100">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700">
                Modalidade
              </label>
              <span className="text-[11px] text-slate-400">Modalidade faturada na conta</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
              {MODALIDADE_OPTIONS.map((m) => {
                const isSelected = formData.modalidadeAtual === m.id;
                return (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => handleModalidadeClick(m.id)}
                    className={`p-2.5 rounded-xl text-xs text-center transition-all cursor-pointer flex items-center justify-center ${
                      isSelected
                        ? 'border-2 border-amber-500 bg-amber-50/90 text-slate-950 shadow-xs ring-1 ring-amber-400/30 font-bold'
                        : 'border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-medium'
                    }`}
                  >
                    <span>{m.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Bandeira Tarifária com Checkbox Automática e Seleção Visual */}
          <div className="space-y-2.5 pt-2 border-t border-slate-100">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700">
                Bandeira Tarifária
              </label>

              {/* Checkbox Automática do Mês */}
              <label className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs font-bold text-slate-800 cursor-pointer select-none transition-colors">
                <input
                  type="checkbox"
                  checked={formData.bandeiraAutomatica}
                  onChange={(e) => {
                    const isAuto = e.target.checked;
                    onChange({
                      ...formData,
                      bandeiraAutomatica: isAuto,
                      bandeira: isAuto ? 'verde' : formData.bandeira,
                    });
                  }}
                  className="w-4 h-4 text-amber-500 rounded border-slate-300 focus:ring-amber-400 cursor-pointer"
                />
                <span>Automática (do mês)</span>
              </label>
            </div>

            {/* Botões de Seleção de Bandeira */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {opcoesBandeira.map((b) => {
                const isSelected = effectiveBandeira === b.id;
                const dot =
                  b.id === 'verde'
                    ? 'bg-emerald-500'
                    : b.id === 'amarela'
                      ? 'bg-amber-500'
                      : b.id === 'vermelha1'
                        ? 'bg-rose-500'
                        : 'bg-red-600';
                return (
                  <button
                    key={b.id}
                    type="button"
                    onClick={() => {
                      onChange({
                        ...formData,
                        bandeiraAutomatica: false,
                        bandeira: b.id,
                      });
                    }}
                    className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                      isSelected
                        ? 'border-2 border-amber-500 bg-amber-50 text-slate-950 shadow-xs ring-1 ring-amber-400/30'
                        : 'border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 font-medium'
                    }`}
                  >
                    <span className={`w-2.5 h-2.5 rounded-full ${dot}`}></span>
                    <span>{b.label}</span>
                  </button>
                );
              })}
            </div>
            <p className="text-[11px] text-slate-400">
              {bandeiraAtivaApi
                ? `Bandeira vigente na competência (API): ${bandeiraAtivaApi}.`
                : 'Valores de bandeira carregados da API quando disponível.'}
            </p>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* SEÇÃO 2: CONSUMO ATIVO E DEMANDA REGISTRADA */}
        {/* ========================================================================= */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-xs space-y-5">
          <div className="flex items-start gap-3 border-b border-slate-100 pb-4">
            <div className="w-9 h-9 rounded-xl bg-amber-100 text-amber-900 flex items-center justify-center font-bold shrink-0 mt-0.5">
              <Gauge className="w-5 h-5 text-amber-700" />
            </div>
            <div>
              <h2 className="font-display text-base sm:text-lg font-bold text-slate-900">
                2. Consumo Ativo e Demanda Registrada
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Valores mensais de energia e potência contratada
              </p>
            </div>
          </div>

          {/* Grid de Consumos */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Consumo Ponta */}
            <div className="space-y-1.5">
              <label
                htmlFor="inp-consumo-ponta"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Consumo Ponta
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-consumo-ponta"
                  type="number"
                  min="0"
                  step="1"
                  value={formData.consumoPonta || ''}
                  onChange={(e) => handleIntChange('consumoPonta', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="0"
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                  kWh
                </span>
              </div>
            </div>

            {/* Consumo Fora Ponta */}
            <div className="space-y-1.5">
              <label
                htmlFor="inp-consumo-fponta"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Consumo Fora Ponta
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-consumo-fponta"
                  type="number"
                  min="0"
                  step="1"
                  value={formData.consumoForaPonta || ''}
                  onChange={(e) => handleIntChange('consumoForaPonta', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="0"
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                  kWh
                </span>
              </div>
            </div>

            {/* Consumo Intermediário */}
            <div className="space-y-1.5">
              <label
                htmlFor="inp-consumo-inter"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Consumo Intermediário
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-consumo-inter"
                  type="number"
                  min="0"
                  step="1"
                  value={formData.consumoIntermediario || ''}
                  onChange={(e) => handleIntChange('consumoIntermediario', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="0"
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                  kWh
                </span>
              </div>
            </div>

            {/* Consumo Total */}
            <div className="space-y-1.5">
              <label
                htmlFor="inp-consumo-total"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Consumo Total
              </label>
              <div className="relative flex rounded-xl border border-slate-200 overflow-hidden bg-slate-50/60 transition-all">
                <input
                  id="inp-consumo-total"
                  type="text"
                  readOnly
                  value={formatNumber(consumoTotalCiclo)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none cursor-default"
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                  kWh
                </span>
              </div>
            </div>
          </div>

          {/* Grid de Demandas — Verde (demanda única) */}
          {formData.modalidadeAtual === 'verde' ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2 border-t border-slate-100">
              {/* Demanda Medida Única */}
              <div className="space-y-1.5">
                <label
                  htmlFor="inp-demanda-medida"
                  className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
                >
                  Demanda Medida Única
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-demanda-medida"
                    type="text"
                    value={formData.demandaMedida || ''}
                    onChange={(e) => handleFloatChange('demandaMedida', e.target.value)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="0,00"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                    kW
                  </span>
                </div>
              </div>

              {/* Demanda Contratada Única */}
              <div className="space-y-1.5">
                <label
                  htmlFor="inp-demanda-contratada"
                  className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
                >
                  Demanda Contratada Única
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-demanda-contratada"
                    type="text"
                    value={formData.demandaContratada || ''}
                    onChange={(e) => handleFloatChange('demandaContratada', e.target.value)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="0,00"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                    kW
                  </span>
                </div>
              </div>

              {/* Demanda Faturável */}
              <div className="space-y-1.5">
                <label
                  htmlFor="inp-demanda-faturavel"
                  className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
                >
                  Demanda Faturável
                </label>
                <div className="relative flex rounded-xl border border-slate-200 overflow-hidden bg-slate-50/60 transition-all">
                  <input
                    id="inp-demanda-faturavel"
                    type="text"
                    readOnly
                    value={formatNumber(Math.max(formData.demandaMedida, formData.demandaContratada), 2)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none cursor-default"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                    kW
                  </span>
                </div>
              </div>

              {/* Demanda Isenta ICMS */}
              <div className="space-y-1.5">
                <label className="inline-flex items-center gap-2 mb-1 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.demandaIsentaIcmsAtiva}
                    onChange={(e) => onChange({ ...formData, demandaIsentaIcmsAtiva: e.target.checked })}
                    className="w-4 h-4 text-amber-500 rounded border-slate-300 focus:ring-amber-400 cursor-pointer"
                  />
                  <span className="text-[11px] font-semibold text-slate-700">
                    Demanda Isenta de ICMS — opcional
                  </span>
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-demanda-isenta"
                    type="text"
                    value={formData.demandaIsentaIcms || ''}
                    onChange={(e) => handleFloatChange('demandaIsentaIcms', e.target.value)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="0 = sem isenção"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                    kW
                  </span>
                </div>
              </div>
            </div>
          ) : formData.modalidadeAtual === 'azul' ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-2 border-t border-slate-100">
              {/* Azul — demanda por posto (ponta/fora ponta) */}
              <div className="space-y-1.5">
                <label htmlFor="inp-demanda-ponta-medida" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                  Demanda Medida — Ponta
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-demanda-ponta-medida"
                    type="text"
                    value={formData.demandaPontaKw || ''}
                    onChange={(e) => handleFloatChange('demandaPontaKw', e.target.value)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="0,00"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">kW</span>
                </div>
              </div>
              <div className="space-y-1.5">
                <label htmlFor="inp-demanda-ponta-contratada" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                  Demanda Contratada — Ponta
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-demanda-ponta-contratada"
                    type="text"
                    value={formData.demandaContratadaPontaKw || ''}
                    onChange={(e) => handleFloatChange('demandaContratadaPontaKw', e.target.value)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="0,00"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">kW</span>
                </div>
              </div>
              <div className="space-y-1.5">
                <label htmlFor="inp-demanda-fponta-medida" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                  Demanda Medida — Fora Ponta
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-demanda-fponta-medida"
                    type="text"
                    value={formData.demandaForaPontaKw || ''}
                    onChange={(e) => handleFloatChange('demandaForaPontaKw', e.target.value)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="0,00"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">kW</span>
                </div>
              </div>
              <div className="space-y-1.5">
                <label htmlFor="inp-demanda-fponta-contratada" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                  Demanda Contratada — Fora Ponta
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-demanda-fponta-contratada"
                    type="text"
                    value={formData.demandaContratadaForaPontaKw || ''}
                    onChange={(e) => handleFloatChange('demandaContratadaForaPontaKw', e.target.value)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="0,00"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">kW</span>
                </div>
              </div>
              <div className="space-y-1.5">
                <label htmlFor="inp-demanda-faturavel-ponta" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                  Demanda Faturável — Ponta
                </label>
                <div className="relative flex rounded-xl border border-slate-200 overflow-hidden bg-slate-50/60 transition-all">
                  <input
                    id="inp-demanda-faturavel-ponta"
                    type="text"
                    readOnly
                    value={formatNumber(Math.max(formData.demandaPontaKw, formData.demandaContratadaPontaKw), 2)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none cursor-default"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">kW</span>
                </div>
              </div>
              <div className="space-y-1.5">
                <label htmlFor="inp-demanda-faturavel-fponta" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                  Demanda Faturável — Fora Ponta
                </label>
                <div className="relative flex rounded-xl border border-slate-200 overflow-hidden bg-slate-50/60 transition-all">
                  <input
                    id="inp-demanda-faturavel-fponta"
                    type="text"
                    readOnly
                    value={formatNumber(Math.max(formData.demandaForaPontaKw, formData.demandaContratadaForaPontaKw), 2)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none cursor-default"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">kW</span>
                </div>
              </div>
              {/* Isenção de ICMS (Azul) */}
              <div className="space-y-1.5">
                <label className="inline-flex items-center gap-2 mb-1 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.demandaIsentaIcmsAtiva}
                    onChange={(e) => onChange({ ...formData, demandaIsentaIcmsAtiva: e.target.checked })}
                    className="w-4 h-4 text-amber-500 rounded border-slate-300 focus:ring-amber-400 cursor-pointer"
                  />
                  <span className="text-[11px] font-semibold text-slate-700">
                    Demanda Isenta de ICMS — opcional
                  </span>
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-demanda-isenta-azul"
                    type="text"
                    value={formData.demandaIsentaIcms || ''}
                    onChange={(e) => handleFloatChange('demandaIsentaIcms', e.target.value)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="0 = sem isenção"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">kW</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="pt-2 border-t border-slate-100 text-xs text-slate-500">
              Sem faturamento de demanda nesta modalidade — Optante B, Convencional Monômia e
              Branca faturam energia (e custo de disponibilidade) sem cobrança de demanda.
            </div>
          )}

          {/* Sub-bloco: Outras Parcelas e Mercado Livre (ACL) */}
          <div className="pt-4 border-t border-slate-100 space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-800">
                Outras Parcelas e Mercado Livre (ACL)
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Outros Valores */}
              <div className="space-y-1">
                <label
                  htmlFor="inp-outros-valores"
                  className="text-xs font-semibold text-slate-600 block"
                >
                  Outros Valores
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-r border-slate-200">
                    R$
                  </span>
                  <input
                    id="inp-outros-valores"
                    type="text"
                    value={formData.outrosValores || ''}
                    onChange={(e) => handleFloatChange('outrosValores', e.target.value)}
                    className="w-full h-10 px-3 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="0,00"
                  />
                </div>
              </div>

              {/* % Consumo Mês Anterior */}
              <div className="space-y-1">
                <label
                  htmlFor="inp-rateio-mes"
                  className="text-xs font-semibold text-slate-600 block"
                >
                  % Consumo Mês Anterior
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-rateio-mes"
                    type="text"
                    value={formData.percentualConsumoMesAnterior || ''}
                    onChange={(e) =>
                      handleFloatChange('percentualConsumoMesAnterior', e.target.value)
                    }
                    className="w-full h-10 px-3 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="0"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                    frac.
                  </span>
                </div>
              </div>

              {/* Preço Médio de Energia no ACL */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <label
                    htmlFor="inp-preco-acl"
                    className="text-xs font-semibold text-slate-600 block"
                  >
                    Preço Médio de Energia no ACL
                  </label>
                  <span className="text-[10px] text-slate-400">0 = desativa ACL</span>
                </div>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-preco-acl"
                    type="text"
                    value={formData.precoMedioACL || ''}
                    onChange={(e) => handleFloatChange('precoMedioACL', e.target.value)}
                    className="w-full h-10 px-3 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="312,4"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                    R$/MWh
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* SEÇÃO 2B: OPTANTE B — GRUPO A FATURADO COMO GRUPO B (art. 292) */}
        {/* ========================================================================= */}
        {formData.modalidadeAtual === 'optante_b' ? (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-xs space-y-5">
            <div className="flex items-start gap-3 border-b border-slate-100 pb-4">
              <div className="w-9 h-9 rounded-xl bg-amber-100 text-amber-900 flex items-center justify-center font-bold shrink-0 mt-0.5">
                <Zap className="w-5 h-5 text-amber-700" />
              </div>
              <div>
                <h2 className="font-display text-base sm:text-lg font-bold text-slate-900">
                  2B. Optante B — Grupo A faturado como Grupo B (art. 292)
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Elegibilidade: transformadores ≤ 112,5 kVA (ou ≤ 1.125 kVA se cooperativa de
                  eletrificação rural); hotelaria/pousada em área de veraneio ou turismo; ou
                  refletores ≥ 2/3 da carga instalada em atividades esportivas/parques agropecuários.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-1.5">
                <label htmlFor="inp-atividade" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                  Atividade econômica
                </label>
                <select
                  id="inp-atividade"
                  value={formData.atividade}
                  onChange={(e) => onChange({ ...formData, atividade: e.target.value as InvoiceFormData['atividade'] })}
                  className="w-full h-11 px-3.5 pr-8 bg-slate-50/60 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition-all appearance-none cursor-pointer truncate"
                >
                  {(
                    [
                      'Comercial ou Industrial',
                      'Rural',
                      'Residencial',
                      'Esportivo ou Parque Agropecuário',
                    ] as const
                  ).map((a) => (
                    <option key={a} value={a}>
                      {a}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label htmlFor="inp-tipo-ligacao" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                  Tipo de ligação
                </label>
                <select
                  id="inp-tipo-ligacao"
                  value={formData.tipoLigacao}
                  onChange={(e) => onChange({ ...formData, tipoLigacao: e.target.value as InvoiceFormData['tipoLigacao'] })}
                  className="w-full h-11 px-3.5 pr-8 bg-slate-50/60 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition-all appearance-none cursor-pointer truncate"
                >
                  {(['Trifásico', 'Bifásico', 'Monofásico'] as const).map((t) => (
                    <option key={t} value={t}>
                      {t} {t === 'Trifásico' ? '(mín. 100 kWh)' : t === 'Bifásico' ? '(mín. 50 kWh)' : '(mín. 30 kWh)'}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label htmlFor="inp-potencia-trafo" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                  Potência dos transformadores
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-potencia-trafo"
                    type="text"
                    value={formData.potenciaTransformadoresKva || ''}
                    onChange={(e) => handleFloatChange('potenciaTransformadoresKva', e.target.value)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="112,5"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">kVA</span>
                </div>
              </div>

              <div className="space-y-1.5">
                <label htmlFor="inp-carga-refletores" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                  Carga dos refletores
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-carga-refletores"
                    type="text"
                    value={formData.cargaRefletoresKw || ''}
                    onChange={(e) => handleFloatChange('cargaRefletoresKw', e.target.value)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="0"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">kW</span>
                </div>
              </div>

              <div className="space-y-1.5">
                <label htmlFor="inp-carga-instalada" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                  Carga instalada total
                </label>
                <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                  <input
                    id="inp-carga-instalada"
                    type="text"
                    value={formData.cargaInstaladaTotalKw || ''}
                    onChange={(e) => handleFloatChange('cargaInstaladaTotalKw', e.target.value)}
                    className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                    placeholder="0"
                  />
                  <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">kW</span>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-3 pt-1">
              <label className="inline-flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={formData.cooperativaEletrificacaoRural}
                  onChange={(e) => onChange({ ...formData, cooperativaEletrificacaoRural: e.target.checked })}
                  className="w-4 h-4 text-amber-500 rounded border-slate-300 focus:ring-amber-400 cursor-pointer"
                />
                <span className="text-xs font-semibold text-slate-800">Cooperativa de eletrificação rural (≤ 1.125 kVA)</span>
              </label>
              <label className="inline-flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={formData.hotelariaTurismo}
                  onChange={(e) => onChange({ ...formData, hotelariaTurismo: e.target.checked })}
                  className="w-4 h-4 text-amber-500 rounded border-slate-300 focus:ring-amber-400 cursor-pointer"
                />
                <span className="text-xs font-semibold text-slate-800">Hotelaria/pousada em área de veraneio ou turismo</span>
              </label>
              <label className="inline-flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={formData.prePagamento}
                  onChange={(e) => onChange({ ...formData, prePagamento: e.target.checked })}
                  className="w-4 h-4 text-amber-500 rounded border-slate-300 focus:ring-amber-400 cursor-pointer"
                />
                <span className="text-xs font-semibold text-slate-800">Pré-pagamento (exceção do custo de disponibilidade)</span>
              </label>
            </div>

            <p className="text-[11px] text-slate-400">
              Faturamento: tarifa Convencional do subgrupo B derivado da atividade (Residencial → B1;
              Rural → B2; demais → B3). Classe/subclasse do perfil desambiguam a tarifa; monômia sem
              demanda/ultrapassagem; custo de disponibilidade (30/50/100 kWh) quando o consumo for menor.
            </p>
          </div>
        ) : null}

        {/* ========================================================================= */}
        {/* SEÇÃO 3: REATIVOS */}
        {/* ========================================================================= */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-xs space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-xl bg-amber-100 text-amber-900 flex items-center justify-center font-bold shrink-0 mt-0.5">
                <Activity className="w-5 h-5 text-amber-700" />
              </div>
              <div>
                <h2 className="font-display text-base sm:text-lg font-bold text-slate-900">
                  3. Reativos
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Excedentes de energia e potência reativas (art. 304, REN 1.000/2021)
                </p>
              </div>
            </div>

            {/* Toggle Buscar tarifa de reativo automaticamente (VRERE/VRDRE) */}
            <label className="inline-flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 cursor-pointer self-start sm:self-auto transition-colors">
              <input
                type="checkbox"
                checked={formData.buscarReativoAuto}
                onChange={(e) =>
                  onChange({ ...formData, buscarReativoAuto: e.target.checked })
                }
                className="w-4 h-4 text-amber-500 rounded border-slate-300 focus:ring-amber-400 cursor-pointer"
              />
              <span className="text-xs font-semibold text-slate-800">
                Buscar tarifa de reativo automaticamente (VRERE/VRDRE)
              </span>
            </label>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Consumo de Energia Reativa Excedente — Ponta */}
            <div className="space-y-1.5">
              <label
                htmlFor="inp-reativo-ponta"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Consumo de Energia Reativa Excedente — Ponta
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-reativo-ponta"
                  type="number"
                  min="0"
                  step="1"
                  value={formData.consumoReativoPonta || ''}
                  onChange={(e) => handleIntChange('consumoReativoPonta', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="0"
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                  kVArh
                </span>
              </div>
            </div>

            {/* Consumo de Energia Reativa Excedente — Fora de Ponta */}
            <div className="space-y-1.5">
              <label
                htmlFor="inp-reativo-fponta"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Consumo de Energia Reativa Excedente — Fora de Ponta
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-reativo-fponta"
                  type="number"
                  min="0"
                  step="1"
                  value={formData.consumoReativoForaPonta || ''}
                  onChange={(e) => handleIntChange('consumoReativoForaPonta', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="9"
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                  kVArh
                </span>
              </div>
            </div>

            {/* Demanda de Potência Reativa Excedente — Ponta */}
            <div className="space-y-1.5">
              <label
                htmlFor="inp-dem-reativa-ponta"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Demanda de Potência Reativa Excedente — Ponta
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-dem-reativa-ponta"
                  type="number"
                  min="0"
                  step="1"
                  value={formData.demandaReativaPonta || ''}
                  onChange={(e) => handleIntChange('demandaReativaPonta', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="0"
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                  kVAr
                </span>
              </div>
            </div>

            {/* Demanda de Potência Reativa Excedente — Fora de Ponta */}
            <div className="space-y-1.5">
              <label
                htmlFor="inp-dem-reativa-fponta"
                className="text-xs font-semibold uppercase tracking-wider text-slate-700 block"
              >
                Demanda de Potência Reativa Excedente — Fora de Ponta
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-dem-reativa-fponta"
                  type="number"
                  min="0"
                  step="1"
                  value={formData.demandaReativaForaPonta || ''}
                  onChange={(e) => handleIntChange('demandaReativaForaPonta', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="0"
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                  kVAr
                </span>
              </div>
            </div>
          </div>

          {/* Capacitivos (janela 0h–6h) + tarifas manuais */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
            <div className="space-y-1.5">
              <label htmlFor="inp-reativo-capacitivo" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                Energia Reativa Capacitiva (0h–6h)
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-reativo-capacitivo"
                  type="number"
                  min="0"
                  step="1"
                  value={formData.reativoEnergiaCapacitiva || ''}
                  onChange={(e) => handleIntChange('reativoEnergiaCapacitiva', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="0"
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">kVArh</span>
              </div>
            </div>
            <div className="space-y-1.5">
              <label htmlFor="inp-dem-reativa-capacitiva" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                Demanda Reativa Capacitiva (0h–6h)
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-dem-reativa-capacitiva"
                  type="number"
                  min="0"
                  step="1"
                  value={formData.reativoDemandaCapacitiva || ''}
                  onChange={(e) => handleIntChange('reativoDemandaCapacitiva', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="0"
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">kVAr</span>
              </div>
            </div>
            {!formData.buscarReativoAuto ? (
              <>
                <div className="space-y-1.5">
                  <label htmlFor="inp-tarifa-reat-e" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                    Tarifa — Energia Reativa (R$/kVArh)
                  </label>
                  <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                    <input
                      id="inp-tarifa-reat-e"
                      type="text"
                      value={formData.tarifaReativoEnergia || ''}
                      onChange={(e) => handleFloatChange('tarifaReativoEnergia', e.target.value)}
                      className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                      placeholder="0,28209"
                    />
                    <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">R$/kVArh</span>
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label htmlFor="inp-tarifa-reat-d" className="text-xs font-semibold uppercase tracking-wider text-slate-700 block">
                    Tarifa — Demanda Reativa (R$/kVAr)
                  </label>
                  <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                    <input
                      id="inp-tarifa-reat-d"
                      type="text"
                      value={formData.tarifaReativoDemanda || ''}
                      onChange={(e) => handleFloatChange('tarifaReativoDemanda', e.target.value)}
                      className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                      placeholder="14,85"
                    />
                    <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">R$/kVAr</span>
                  </div>
                </div>
              </>
            ) : null}
          </div>

          <label className="inline-flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 cursor-pointer w-fit transition-colors">
            <input
              type="checkbox"
              checked={formData.tributarReativos}
              onChange={(e) => onChange({ ...formData, tributarReativos: e.target.checked })}
              className="w-4 h-4 text-amber-500 rounded border-slate-300 focus:ring-amber-400 cursor-pointer"
            />
            <span className="text-xs font-semibold text-slate-800">
              Tributar reativos excedentes (PIS/COFINS/ICMS) — faturas CEMIG/Equatorial
            </span>
          </label>
        </div>

        {/* ========================================================================= */}
        {/* SEÇÃO 4: TRIBUTOS */}
        {/* ========================================================================= */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-xs space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-xl bg-amber-100 text-amber-900 flex items-center justify-center font-bold shrink-0 mt-0.5">
                <Receipt className="w-5 h-5 text-amber-700" />
              </div>
              <div>
                <h2 className="font-display text-base sm:text-lg font-bold text-slate-900">
                  4. Tributos
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  PIS/PASEP, COFINS, ICMS e CIP/COSIP aplicados sobre a fatura
                </p>
              </div>
            </div>

            {/* Toggle Aplicar PIS/COFINS/ICMS */}
            <label className="inline-flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 cursor-pointer self-start sm:self-auto transition-colors">
              <input
                type="checkbox"
                checked={formData.aplicarTributos}
                onChange={(e) => onChange({ ...formData, aplicarTributos: e.target.checked })}
                className="w-4 h-4 text-amber-500 rounded border-slate-300 focus:ring-amber-400 cursor-pointer"
              />
              <span className="text-xs font-semibold text-slate-800">
                Aplicar PIS/COFINS/ICMS
              </span>
            </label>

            {/* Toggle arredondar centavos */}
            <label className="inline-flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 cursor-pointer self-start sm:self-auto transition-colors">
              <input
                type="checkbox"
                checked={formData.arredondarCentavos}
                onChange={(e) => onChange({ ...formData, arredondarCentavos: e.target.checked })}
                className="w-4 h-4 text-amber-500 rounded border-slate-300 focus:ring-amber-400 cursor-pointer"
              />
              <span className="text-xs font-semibold text-slate-800">
                Arredondar linhas a centavos
              </span>
            </label>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* PIS */}
            <div className="space-y-1.5">
              <label htmlFor="inp-pis" className="text-xs font-semibold text-slate-700 block">
                PIS
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-pis"
                  type="text"
                  value={formData.pis || ''}
                  onChange={(e) => handleFloatChange('pis', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="0,95"
                  disabled={!formData.aplicarTributos}
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                  %
                </span>
              </div>
            </div>

            {/* COFINS */}
            <div className="space-y-1.5">
              <label htmlFor="inp-cofins" className="text-xs font-semibold text-slate-700 block">
                COFINS
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-cofins"
                  type="text"
                  value={formData.cofins || ''}
                  onChange={(e) => handleFloatChange('cofins', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="4,38"
                  disabled={!formData.aplicarTributos}
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                  %
                </span>
              </div>
            </div>

            {/* ICMS */}
            <div className="space-y-1.5">
              <label htmlFor="inp-icms" className="text-xs font-semibold text-slate-700 block">
                ICMS
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <input
                  id="inp-icms"
                  type="text"
                  value={formData.icms || ''}
                  onChange={(e) => handleFloatChange('icms', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="18"
                  disabled={!formData.aplicarTributos}
                />
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-l border-slate-200">
                  %
                </span>
              </div>
            </div>

            {/* Tipo de ICMS: Fora e Dentro */}
            <div className="space-y-1.5">
              <label htmlFor="inp-tipo-icms" className="text-xs font-semibold text-slate-700 block">
                Tipo de ICMS
              </label>
              <div className="grid grid-cols-2 gap-1 h-11 p-1 bg-slate-100 rounded-xl border border-slate-200">
                <button
                  type="button"
                  onClick={() => onChange({ ...formData, tipoIcms: 'fora' })}
                  disabled={!formData.aplicarTributos}
                  className={`rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                    formData.tipoIcms === 'fora'
                      ? 'bg-amber-400 text-slate-950 shadow-2xs font-bold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Fora
                </button>
                <button
                  type="button"
                  onClick={() => onChange({ ...formData, tipoIcms: 'dentro' })}
                  disabled={!formData.aplicarTributos}
                  className={`rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                    formData.tipoIcms === 'dentro'
                      ? 'bg-amber-400 text-slate-950 shadow-2xs font-bold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Dentro
                </button>
              </div>
            </div>

            {/* CIP/COSIP */}
            <div className="space-y-1.5">
              <label htmlFor="inp-cip" className="text-xs font-semibold text-slate-700 block">
                CIP/COSIP
              </label>
              <div className="relative flex rounded-xl border border-slate-200 focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-amber-400 overflow-hidden bg-slate-50/60 focus-within:bg-white transition-all">
                <span className="px-3 flex items-center text-xs font-mono-num text-slate-500 bg-slate-100/70 border-r border-slate-200">
                  R$
                </span>
                <input
                  id="inp-cip"
                  type="text"
                  value={formData.cipCosip || ''}
                  onChange={(e) => handleFloatChange('cipCosip', e.target.value)}
                  className="w-full h-11 px-3.5 bg-transparent text-sm font-semibold font-mono-num text-slate-800 focus:outline-none"
                  placeholder="0,00"
                />
              </div>
            </div>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* BOTÃO PRINCIPAL DE AÇÃO (APÓS TODAS AS SEÇÕES) */}
        {/* ========================================================================= */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={carregando}
            className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-amber-400 via-amber-500 to-yellow-400 hover:from-amber-300 hover:to-yellow-300 text-slate-950 font-black text-base shadow-lg shadow-amber-500/25 hover:shadow-amber-500/35 transition-all duration-200 flex items-center justify-center gap-2 group cursor-pointer active:scale-[0.99] disabled:opacity-60 disabled:cursor-wait"
          >
            <span>{carregando ? 'Calculando na API...' : 'Calcular e Gerar Análise'}</span>
            <ArrowRight className="w-5 h-5 font-bold group-hover:translate-x-1 transition-transform" />
          </button>
          <p className="text-center text-xs text-slate-400 mt-2.5 flex items-center justify-center gap-1.5">
            <Lock className="w-3.5 h-3.5 text-slate-400" />
            <span>Cálculo em estrita conformidade com as regras tarifárias homologadas pela ANEEL</span>
          </p>
        </div>
      </form>
    </section>
  );
};
