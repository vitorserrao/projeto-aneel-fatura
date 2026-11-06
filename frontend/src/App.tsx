import React, { useState } from 'react';
import { Cabecalho, Etapa } from './components/Cabecalho';
import { EtapaDados } from './components/EtapaDados';
import { EtapaFatura } from './components/EtapaFatura';
import { EtapaAnalise } from './components/EtapaAnalise';
import { Aviso } from './components/ui';
import type { InvoiceFormData } from './types/energy';
import {
  BandeiraOpcao,
  listarBandeiras,
  listarClasses,
  listarDistribuidoras,
  listarSubgrupos,
  mensagemErro,
} from './lib/api';
import { Analise, calcularEpiAnalise, executarAnalise } from './lib/analise';
import { ResultadoSeries, calcularSeries } from './lib/series';
import { validarFormulario } from './lib/validacao';
import { DEFAULT_FORM, exemploCopel } from './lib/formPadrao';

export default function App() {
  const [etapa, setEtapa] = useState<Etapa>(1);
  const [form, setForm] = useState<InvoiceFormData>(DEFAULT_FORM);
  const [analise, setAnalise] = useState<Analise | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erroApi, setErroApi] = useState<string | null>(null);
  const [pendencias, setPendencias] = useState<string[]>([]);

  // Séries mensais da etapa 3 (até 72 chamadas, com progresso).
  const [series, setSeries] = useState<ResultadoSeries | null>(null);
  const [progressoSeries, setProgressoSeries] = useState<{ feitas: number; total: number } | null>(null);
  const execucao = React.useRef(0);
  /** Cache da curva de DC (por mês e DC) — sobrevive à troca de etapa. */
  const cacheCurva = React.useRef(new Map<string, number | null>());

  // Listas dinâmicas da API (null = listas estáticas de apoio).
  const [distribuidorasApi, setDistribuidorasApi] = useState<string[] | null>(null);
  const [subgruposApi, setSubgruposApi] = useState<string[] | null>(null);
  const [classesApi, setClassesApi] = useState<string[] | null>(null);
  const [bandeirasApi, setBandeirasApi] = useState<BandeiraOpcao[] | null>(null);
  const [bandeiraAtivaApi, setBandeiraAtivaApi] = useState<string | null>(null);

  React.useEffect(() => {
    void listarDistribuidoras()
      .then((d) => setDistribuidorasApi(d.map((x) => x.sig_agente)))
      .catch(() => setDistribuidorasApi(null));
    void listarSubgrupos().then(setSubgruposApi).catch(() => setSubgruposApi(null));
    void listarClasses().then(setClassesApi).catch(() => setClassesApi(null));
  }, []);

  // Bandeiras da competência informada.
  React.useEffect(() => {
    if (!/^\d{2}\/\d{2}\/\d{4}$/.test(form.dataReferencia.trim())) return;
    void listarBandeiras(form.dataReferencia)
      .then((b) => {
        setBandeirasApi(b.opcoes);
        setBandeiraAtivaApi(b.ativa);
      })
      .catch(() => setBandeirasApi(null));
  }, [form.dataReferencia]);

  const irPara = (e: Etapa) => {
    setEtapa(e);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  async function calcular() {
    const faltando = validarFormulario(form);
    setPendencias(faltando);
    if (faltando.length > 0) return;
    setCarregando(true);
    setErroApi(null);
    const id = ++execucao.current;
    try {
      const a = await executarAnalise(form, bandeirasApi);
      if (id !== execucao.current) return;
      setAnalise(a);
      setSeries(null);
      setProgressoSeries(null);
      cacheCurva.current = new Map();
      irPara(2);
      // Séries mensais em segundo plano (etapa 3).
      if (a.planejamento && a.mesesPlanejamento.length > 0) {
        void calcularSeries(a.form, a.planejamento, a.mesesPlanejamento, (feitas, total) => {
          if (id === execucao.current) setProgressoSeries({ feitas, total });
        }).then((r) => {
          if (id === execucao.current) setSeries(r);
        });
      }
    } catch (e) {
      if (id !== execucao.current) return;
      setErroApi(mensagemErro(e));
      setAnalise(null);
      setSeries(null);
    } finally {
      if (id === execucao.current) setCarregando(false);
    }
  }

  /** Etapa 3: OPEX/CAPEX/horizonte/proposta editáveis → recalcula o E-PI na API. */
  async function atualizarAcl(mudancas: Partial<InvoiceFormData>) {
    if (!analise) return;
    const novoForm = { ...analise.form, ...mudancas };
    setForm((f) => ({ ...f, ...mudancas }));
    setAnalise({ ...analise, form: novoForm });
    const epi = await calcularEpiAnalise(novoForm, analise.epi.modalidade);
    setAnalise((a) => (a ? { ...a, form: novoForm, epi } : a));
  }

  const liberadas: Etapa[] = analise ? [1, 2, 3] : [1];

  return (
    <div className="min-h-screen flex flex-col bg-fundo text-tinta">
      <Cabecalho etapa={etapa} liberadas={liberadas} aoIr={irPara} />

      <main className="flex-grow w-full max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-4">
        {erroApi ? (
          <Aviso tom="erro">
            <strong>Não foi possível calcular: a API não respondeu ou recusou o pedido.</strong> Nenhum valor é estimado
            sem o motor de cálculo. <span className="block mt-1 num text-xs break-words">{erroApi}</span>
          </Aviso>
        ) : null}

        {etapa === 1 ? (
          <EtapaDados
            form={form}
            aoMudar={setForm}
            aoCalcular={() => void calcular()}
            aoPreencherExemplo={() => {
              setForm(exemploCopel());
              setPendencias([]);
            }}
            carregando={carregando}
            pendencias={pendencias}
            distribuidorasApi={distribuidorasApi}
            subgruposApi={subgruposApi}
            classesApi={classesApi}
            bandeirasApi={bandeirasApi}
            bandeiraAtivaApi={bandeiraAtivaApi}
          />
        ) : null}

        {etapa === 2 && analise ? (
          <EtapaFatura analise={analise} aoEditar={() => irPara(1)} aoAvancar={() => irPara(3)} />
        ) : null}

        {etapa === 3 && analise ? (
          <EtapaAnalise
            analise={analise}
            series={series}
            progressoSeries={progressoSeries}
            cacheCurva={cacheCurva.current}
            aoAtualizarAcl={(m) => void atualizarAcl(m)}
            aoVoltar={() => irPara(2)}
          />
        ) : null}
      </main>

      <footer className="border-t border-borda bg-white no-print">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5 text-xs text-texto2 space-y-1">
          <p>
            Tarifas homologadas da ANEEL (base “Tarifa de Aplicação”) pela vigência de cada mês; regras da REN
            1.000/2021. Todos os valores vêm da API do simulador.
          </p>
          <p>Simulação: não é documento de cobrança.</p>
        </div>
      </footer>
    </div>
  );
}
