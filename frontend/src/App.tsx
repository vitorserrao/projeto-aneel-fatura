import React, { useState } from 'react';
import { Header } from './components/Header';
import { Stepper } from './components/Stepper';
import { StepOneForm } from './components/StepOneForm';
import { StepTwoReport } from './components/StepTwoReport';
import { Footer } from './components/Footer';
import { AuditResult, InvoiceFormData } from './types/energy';
import {
  BandeiraOpcao,
  calcularEpi,
  calcularFatura,
  compararModalidades,
  compararPlanejamento,
  listarBandeiras,
  listarClasses,
  listarDistribuidoras,
  listarSubgrupos,
} from './lib/api';
import { adaptarComparacao, adaptarEpi, adaptarPlanejamento } from './lib/adapter';
import { montarMesesPlanejamento, validarFormulario } from './lib/validacao';

const HISTORICO_EXEMPLO_COPEL = [
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

const DEFAULT_FORM: InvoiceFormData = {
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

export default function App() {
  const [currentStep, setCurrentStep] = useState<1 | 2>(1);
  const [formData, setFormData] = useState<InvoiceFormData>(DEFAULT_FORM);
  const [auditResult, setAuditResult] = useState<AuditResult | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erroApi, setErroApi] = useState<string | null>(null);
  const [pendencias, setPendencias] = useState<string[]>([]);

  // Dados dinâmicos vindos da API (null = fallback para as listas estáticas).
  const [distribuidorasApi, setDistribuidorasApi] = useState<string[] | null>(null);
  const [subgruposApi, setSubgruposApi] = useState<string[] | null>(null);
  const [classesApi, setClassesApi] = useState<string[] | null>(null);
  const [bandeirasApi, setBandeirasApi] = useState<BandeiraOpcao[] | null>(null);
  const [bandeiraAtivaApi, setBandeiraAtivaApi] = useState<string | null>(null);

  // Carrega as listas da API uma vez (erro → mantém fallback estático).
  React.useEffect(() => {
    void listarDistribuidoras()
      .then((d) => setDistribuidorasApi(d.map((x) => x.sig_agente)))
      .catch(() => setDistribuidorasApi(null));
    void listarSubgrupos()
      .then((s) => setSubgruposApi(s))
      .catch(() => setSubgruposApi(null));
    void listarClasses()
      .then((c) => setClassesApi(c))
      .catch(() => setClassesApi(null));
    void listarBandeiras(formData.dataReferencia)
      .then((b) => {
        setBandeirasApi(b.opcoes);
        setBandeiraAtivaApi(b.ativa);
      })
      .catch(() => setBandeirasApi(null));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleGoToStep = (step: 1 | 2) => {
    setCurrentStep(step);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  /**
   * Executa a análise na API (fonte única dos números):
   * fatura da modalidade atual + comparação (obrigatórias), E-PI e
   * planejamento anual (opcionais — o relatório indica quando faltam).
   * Sem API não há relatório: o front não inventa valores.
   */
  async function executarAnalise(): Promise<boolean> {
    // Campos obrigatórios: nada vazio vira zero.
    const faltando = validarFormulario(formData);
    setPendencias(faltando);
    if (faltando.length > 0) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return false;
    }
    setCarregando(true);
    setErroApi(null);
    try {
      const [respFatura, respComparacao] = await Promise.allSettled([
        calcularFatura(formData, formData.modalidadeAtual, bandeirasApi),
        compararModalidades(formData, bandeirasApi),
      ]);
      if (respFatura.status === 'rejected') {
        throw respFatura.reason;
      }
      const base =
        respComparacao.status === 'fulfilled' ? respComparacao.value : respFatura.value;

      // Planejamento: histórico informado + mês da fatura (sem histórico = só o mês).
      const { meses, avisos, periodo } = montarMesesPlanejamento(formData);
      const grupoA = formData.modalidadeAtual === 'verde' || formData.modalidadeAtual === 'azul';
      const [respEpi, respPlan] = await Promise.allSettled([
        calcularEpi(formData),
        grupoA && meses.length > 0 ? compararPlanejamento(formData, meses) : Promise.resolve(null),
      ]);
      const epi = respEpi.status === 'fulfilled' ? adaptarEpi(respEpi.value, formData) : null;
      const planejamento =
        respPlan.status === 'fulfilled' && respPlan.value
          ? adaptarPlanejamento(respPlan.value, meses.length, periodo, avisos)
          : null;

      setAuditResult(adaptarComparacao(base, formData, respFatura.value.fatura, epi, planejamento));
      return true;
    } catch (e) {
      const mensagem = e instanceof Error ? e.message : String(e);
      setErroApi(mensagem);
      setAuditResult(null);
      return false;
    } finally {
      setCarregando(false);
    }
  }

  const handleFillExample = () => {
    const exemplo: InvoiceFormData = {
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
    setFormData(exemplo);
    setAuditResult(null);
    setPendencias([]);
  };

  const handleExportPdf = () => {
    window.print();
  };

  return (
    <div className="bg-[#f8fafc] font-sans text-slate-900 antialiased min-h-screen flex flex-col justify-between selection:bg-amber-300 selection:text-slate-950">
      {/* Top Navigation Bar */}
      <Header />

      {/* Main Content Area */}
      <main className="w-full flex-grow py-8 px-4 sm:px-6">
        <div className={`mx-auto ${currentStep === 1 ? 'max-w-4xl' : 'max-w-6xl'}`}>
          {/* Status da API */}
          {erroApi ? (
            <div className="mb-4 rounded-xl bg-amber-50 border border-amber-300 px-4 py-3 text-xs text-amber-900">
              <strong>Não foi possível calcular: a API não respondeu.</strong>{' '}
              Nenhum valor é estimado sem o motor de cálculo. Verifique se a API está no ar e tente de novo.{' '}
              <span className="text-amber-800">{erroApi}</span>
            </div>
          ) : null}

          {pendencias.length > 0 ? (
            <div className="mb-4 rounded-xl bg-red-50 border border-red-300 px-4 py-3 text-xs text-red-900" role="alert">
              <strong>Preencha antes de calcular ({pendencias.length}):</strong>
              <ul className="list-disc pl-5 mt-1 space-y-0.5">
                {pendencias.map((p) => (
                  <li key={p}>{p}</li>
                ))}
              </ul>
              <p className="mt-1 text-red-800">Campos vazios não são tratados como zero. Para zero, digite 0.</p>
            </div>
          ) : null}

          {/* Progress Stepper */}
          <Stepper
            currentStep={currentStep}
            onGoToStep={(step) => {
              // O relatório só existe depois do cálculo na API.
              if (step === 2 && !auditResult) return;
              handleGoToStep(step);
            }}
          />

          {/* Step 1 View */}
          {currentStep === 1 && (
            <StepOneForm
              formData={formData}
              onChange={setFormData}
              onSubmit={() => {
                void executarAnalise().then((ok) => {
                  if (ok) handleGoToStep(2);
                });
              }}
              onFillExample={handleFillExample}
              carregando={carregando}
              distribuidorasApi={distribuidorasApi}
              subgruposApi={subgruposApi}
              classesApi={classesApi}
              bandeirasApi={bandeirasApi}
              bandeiraAtivaApi={bandeiraAtivaApi}
            />
          )}

          {/* Step 2 View */}
          {currentStep === 2 && auditResult && (
            <StepTwoReport
              audit={auditResult}
              formData={formData}
              onBackToEdit={() => handleGoToStep(1)}
              onExportPdf={handleExportPdf}
            />
          )}
        </div>
      </main>

      {/* Institutional Footer */}
      <Footer />

    </div>
  );
}
