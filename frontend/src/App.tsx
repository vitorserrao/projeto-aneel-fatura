import React, { useState } from 'react';
import { Header } from './components/Header';
import { Stepper } from './components/Stepper';
import { StepOneForm } from './components/StepOneForm';
import { StepTwoReport } from './components/StepTwoReport';
import { MigrationModal } from './components/MigrationModal';
import { Footer } from './components/Footer';
import { AuditResult, InvoiceFormData } from './types/energy';
import { calculateAudit } from './utils/calculator';
import {
  BandeiraOpcao,
  calcularFatura,
  compararModalidades,
  listarBandeiras,
  listarClasses,
  listarDistribuidoras,
  listarSubgrupos,
} from './lib/api';
import { adaptarComparacao } from './lib/adapter';

const DEFAULT_FORM: InvoiceFormData = {
  // Seção 1: Distribuidora e Modalidade
  distribuidora: 'COPEL-DIS',
  subgrupo: 'A4',
  classe: 'Não se aplica',
  subclasse: 'Não se aplica',
  detalhe: 'Não se aplica',
  dataReferencia: '15/03/2023',
  modalidadeAtual: 'convencional',
  bandeiraAutomatica: true,
  bandeira: 'verde',

  // Seção 2: Consumo Ativo e Demanda Registrada
  consumoPonta: 55,
  consumoForaPonta: 9094,
  consumoIntermediario: 0,
  demandaMedida: 150.65,
  demandaContratada: 260,
  demandaPontaKw: 0,
  demandaForaPontaKw: 0,
  demandaContratadaPontaKw: 0,
  demandaContratadaForaPontaKw: 0,
  demandaIsentaIcmsAtiva: false,
  demandaIsentaIcms: 109.35,

  // Outras Parcelas e Mercado Livre (ACL)
  outrosValores: 115.01,
  percentualConsumoMesAnterior: 0,
  precoMedioACL: 312.4,

  // Seção 3: Reativos
  buscarReativoAuto: true,
  tarifaReativoEnergia: 0,
  tarifaReativoDemanda: 0,
  consumoReativoPonta: 0,
  consumoReativoForaPonta: 9,
  demandaReativaPonta: 0,
  demandaReativaForaPonta: 0,
  reativoEnergiaCapacitiva: 0,
  reativoDemandaCapacitiva: 0,
  tributarReativos: false,

  // Seção 4: Tributos
  aplicarTributos: true,
  pis: 0.95,
  cofins: 4.38,
  icms: 18,
  tipoIcms: 'fora',
  cipCosip: 0,
  arredondarCentavos: true,

  // Optante B (art. 292)
  atividade: 'Comercial ou Industrial',
  tipoLigacao: 'Trifásico',
  prePagamento: false,
  potenciaTransformadoresKva: 0,
  cooperativaEletrificacaoRural: false,
  hotelariaTurismo: false,
  cargaRefletoresKw: 0,
  cargaInstaladaTotalKw: 0,

  // Metadados
  ucCode: '1049283-0',
  unidadeNome: 'Matriz',
};

export default function App() {
  const [currentStep, setCurrentStep] = useState<1 | 2>(1);
  const [formData, setFormData] = useState<InvoiceFormData>(DEFAULT_FORM);
  const [isMigrationOpen, setIsMigrationOpen] = useState(false);
  const [auditResult, setAuditResult] = useState<AuditResult>(() => calculateAudit(DEFAULT_FORM));
  const [carregando, setCarregando] = useState(false);
  const [erroApi, setErroApi] = useState<string | null>(null);

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

  /** Executa o cálculo: API real como fonte primária; demo como fallback. */
  async function executarAnalise(): Promise<void> {
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
      setAuditResult(adaptarComparacao(base, formData, respFatura.value.fatura));
    } catch (e) {
      const mensagem = e instanceof Error ? e.message : String(e);
      setErroApi(mensagem);
      // Fallback: motor de demonstração local (mesma experiência, sem a API).
      setAuditResult(calculateAudit(formData));
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
      modalidadeAtual: 'convencional',
      bandeiraAutomatica: true,
      bandeira: 'verde',
      consumoPonta: 55,
      consumoForaPonta: 9094,
      consumoIntermediario: 0,
      demandaMedida: 150.65,
      demandaContratada: 260,
      demandaIsentaIcms: 109.35,
      outrosValores: 115.01,
      percentualConsumoMesAnterior: 0,
      precoMedioACL: 312.4,
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
    setAuditResult(calculateAudit(exemplo));
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
              <strong>API indisponível — usando motor de demonstração.</strong>{' '}
              <span className="text-amber-800">{erroApi}</span>
            </div>
          ) : null}

          {/* Progress Stepper */}
          <Stepper currentStep={currentStep} onGoToStep={handleGoToStep} />

          {/* Step 1 View */}
          {currentStep === 1 && (
            <StepOneForm
              formData={formData}
              onChange={setFormData}
              onSubmit={() => {
                void executarAnalise().then(() => handleGoToStep(2));
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
          {currentStep === 2 && (
            <StepTwoReport
              audit={auditResult}
              formData={formData}
              onBackToEdit={() => handleGoToStep(1)}
              onRequestMigration={() => setIsMigrationOpen(true)}
              onExportPdf={handleExportPdf}
            />
          )}
        </div>
      </main>

      {/* Institutional Footer */}
      <Footer />

      {/* Modal de Requerimento de Migração */}
      <MigrationModal
        isOpen={isMigrationOpen}
        onClose={() => setIsMigrationOpen(false)}
        audit={auditResult}
        formData={formData}
      />
    </div>
  );
}
