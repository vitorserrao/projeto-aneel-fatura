/**
 * Etapa 1 — Dados (Main.dc.html). Mesmos campos de InvoiceFormData e mesmo
 * mapeamento para a API; obrigatórios e pendências seguem validarFormulario.
 * Campo vazio fica vazio (null) — nunca vira zero escondido.
 */
import React from 'react';
import type { InvoiceFormData, TariffModalidade } from '../types/energy';
import { BandeiraOpcao, bandeiraApiParaForm, dataReferenciaIso, lerHistorico } from '../lib/api';
import { ehGrupoA, montarMesesPlanejamento, num, validarFormulario } from '../lib/validacao';
import { DISTRIBUIDORAS_APOIO, SUBGROUPS } from '../lib/listas';
import {
  LinhaTabela,
  linhasDeMeses,
  mesesForaDoPadrao,
  modeloCsv,
  textoDeCsv,
  textoDeLinhas,
} from '../lib/historico';
import { numero, pct } from '../lib/formato';
import { rotuloMes } from '../lib/series';
import {
  Aviso,
  Botao,
  Calculado,
  CampoNumero,
  CampoSelecao,
  CampoTexto,
  Cartao,
  Dica,
  Marcador,
  Rotulo,
  Sanfona,
  Segmentos,
  TituloSecao,
} from './ui';

interface Props {
  form: InvoiceFormData;
  aoMudar: (f: InvoiceFormData) => void;
  aoCalcular: () => void;
  aoPreencherExemplo: () => void;
  carregando: boolean;
  pendencias: string[];
  distribuidorasApi: string[] | null;
  subgruposApi: string[] | null;
  classesApi: string[] | null;
  bandeirasApi: BandeiraOpcao[] | null;
  bandeiraAtivaApi: string | null;
}

const MODALIDADES_PRINCIPAIS: { id: TariffModalidade; titulo: string; desc: string }[] = [
  { id: 'verde', titulo: 'Horária Verde', desc: 'Uma demanda contratada; energia na ponta mais cara' },
  { id: 'azul', titulo: 'Horária Azul', desc: 'Demanda contratada na ponta e fora de ponta' },
];
const OUTRAS_MODALIDADES: { id: TariffModalidade; titulo: string; desc: string }[] = [
  { id: 'optante_b', titulo: 'Optante B', desc: 'Grupo A faturado como B (art. 292)' },
  { id: 'branca', titulo: 'Branca', desc: 'Grupo B, três postos' },
  { id: 'convencional', titulo: 'Convencional', desc: 'Grupo B, monômia' },
];

const DICAS = [
  {
    t: 'Onde encontro isso?',
    d: (
      <>
        Na primeira página da fatura, perto do nome do cliente: <strong>código da UC</strong>,{' '}
        <strong>subgrupo</strong> (ex.: A4), <strong>modalidade tarifária</strong> e{' '}
        <strong>demanda contratada</strong>.
      </>
    ),
  },
  {
    t: 'Um mês ou 12 meses?',
    d: (
      <>
        Com uma fatura você confere o cálculo. Com o <strong>histórico de 12 meses</strong> o sistema também acha a
        demanda contratada ideal e compara o ano inteiro.
      </>
    ),
  },
  {
    t: 'Só o essencial está aberto',
    d: (
      <>
        Tributos são obrigatórios. Bandeira é automática. Reativos, outros valores e mercado livre são opcionais: abra
        só se a sua fatura tiver.
      </>
    ),
  },
];

export const EtapaDados: React.FC<Props> = ({
  form,
  aoMudar,
  aoCalcular,
  aoPreencherExemplo,
  carregando,
  pendencias,
  distribuidorasApi,
  subgruposApi,
  classesApi,
  bandeirasApi,
  bandeiraAtivaApi,
}) => {
  const set = <K extends keyof InvoiceFormData>(campo: K, v: InvoiceFormData[K]) => aoMudar({ ...form, [campo]: v });
  /** Campos numéricos não opcionais (padrão 0 declarado): vazio = 0. */
  const set0 = (campo: keyof InvoiceFormData) => (v: number | null) => aoMudar({ ...form, [campo]: v ?? 0 });

  const mod = form.modalidadeAtual;
  const grupoA = ehGrupoA(form);
  const verde = mod === 'verde';
  const azul = mod === 'azul';
  const optante = mod === 'optante_b';
  const pend = validarFormulario(form);
  const falta = (trecho: string) => pend.some((p) => p.startsWith(trecho));

  const [aba, setAba] = React.useState<'mes' | 'historico'>(form.historico12.trim() ? 'historico' : 'mes');
  const [classeAberta, setClasseAberta] = React.useState(false);
  const [optanteAberto, setOptanteAberto] = React.useState(optante);

  // Sanfonas: abrem só se a fatura tiver o item (ou se houver pendência nelas).
  const temReativo =
    form.consumoReativoPonta + form.consumoReativoForaPonta + form.demandaReativaPonta + form.demandaReativaForaPonta +
      form.reativoEnergiaCapacitiva + form.reativoDemandaCapacitiva > 0;
  const [abertas, setAbertas] = React.useState<Record<string, boolean>>({});
  const aberta = (k: string, padrao: boolean) => abertas[k] ?? padrao;
  const alternar = (k: string, padrao: boolean) => setAbertas({ ...abertas, [k]: !aberta(k, padrao) });

  // Exemplo preenchido: reabre as seções com dados.
  const exemploRef = React.useRef(form.ucCode);
  React.useEffect(() => {
    if (form.ucCode !== exemploRef.current) {
      exemploRef.current = form.ucCode;
      setAbertas({});
      setAba(form.historico12.trim() ? 'historico' : 'mes');
    }
  }, [form.ucCode, form.historico12]);

  const opcoesDistribuidora = (distribuidorasApi ?? DISTRIBUIDORAS_APOIO).map((s) => ({
    valor: s,
    rotulo: s,
  }));
  const opcoesSubgrupo =
    subgruposApi && subgruposApi.length > 0
      ? subgruposApi.map((s) => ({ valor: s, rotulo: SUBGROUPS.find((x) => x.id === s)?.label ?? s }))
      : SUBGROUPS.map((s) => ({ valor: s.id, rotulo: s.label }));
  const opcoesClasse = (classesApi ?? []).map((c) => ({ valor: c, rotulo: c }));
  const opcoesBandeira =
    bandeirasApi && bandeirasApi.length > 0
      ? bandeirasApi.map((b) => ({ id: bandeiraApiParaForm(b.bandeira), rotulo: b.bandeira, kwh: b.valor_kwh }))
      : [
          { id: 'verde' as const, rotulo: 'Verde', kwh: 0 },
          { id: 'amarela' as const, rotulo: 'Amarela', kwh: 0.01874 },
          { id: 'vermelha1' as const, rotulo: 'Vermelha P1', kwh: 0.03971 },
          { id: 'vermelha2' as const, rotulo: 'Vermelha P2', kwh: 0.09492 },
        ];

  // Histórico
  const hist = lerHistorico(form.historico12);
  const plano = verde || azul ? montarMesesPlanejamento(form) : { meses: [], avisos: [], periodo: '' };
  // Tabela editável com estado próprio: uma célula apagada para redigitar
  // não some da tabela (o texto só é relido quando muda por fora).
  const [linhas, setLinhasLocal] = React.useState<LinhaTabela[]>(() => linhasDeMeses(hist.meses));
  const textoTabela = React.useRef(form.historico12);
  React.useEffect(() => {
    if (form.historico12 !== textoTabela.current) {
      textoTabela.current = form.historico12;
      setLinhasLocal(linhasDeMeses(lerHistorico(form.historico12).meses));
    }
  }, [form.historico12]);
  const setLinhas = (ls: LinhaTabela[]) => {
    const texto = textoDeLinhas(ls);
    textoTabela.current = texto;
    setLinhasLocal(ls);
    set('historico12', texto);
  };
  const adicionarMes = () => {
    const ultimo = linhas[linhas.length - 1]?.mes;
    const [mm, aaaa] = ultimo ? ultimo.split('/').map(Number) : [0, 0];
    const d = ultimo ? new Date(aaaa, mm, 1) : new Date();
    const mes = `${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
    setLinhas([...linhas, { mes, dPonta: '', dFora: '', ePonta: '', eFora: '' }]);
  };
  const foraPadrao = mesesForaDoPadrao(hist.meses);
  const consumoPeriodo = hist.meses.reduce((a, m) => a + m.e_ponta_kwh + m.e_fora_ponta_kwh, 0);
  const maiorDemanda = hist.meses.reduce(
    (a, m) => Math.max(a, m.d_med_unica ?? 0, m.d_med_ponta ?? 0, m.d_med_fora_ponta ?? 0),
    0,
  );
  const contratadaRef = azul
    ? Math.max(num(form.demandaContratadaPontaKw), num(form.demandaContratadaForaPontaKw))
    : num(form.demandaContratada);

  const consumoTotal = num(form.consumoPonta) + num(form.consumoForaPonta) + num(form.consumoIntermediario);

  const baixarModelo = () => {
    const blob = new Blob([modeloCsv(dataReferenciaIso(form.dataReferencia))], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'historico_12_meses_modelo.csv';
    a.click();
    URL.revokeObjectURL(url);
  };
  const lerCsv = async (arquivo: File | undefined) => {
    if (!arquivo) return;
    set('historico12', textoDeCsv(await arquivo.text()));
  };

  const irPara = (id: string) => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });

  const cartaoModalidade = (m: { id: TariffModalidade; titulo: string; desc: string }, grande: boolean) => {
    const ativo = mod === m.id;
    return (
      <button
        key={m.id}
        type="button"
        aria-pressed={ativo}
        onClick={() => {
          set('modalidadeAtual', m.id);
          if (m.id === 'optante_b') setOptanteAberto(true);
        }}
        className={`text-left rounded-xl border px-4 cursor-pointer transition min-w-0 ${grande ? 'py-3.5' : 'py-2.5'} ${
          ativo ? 'border-tinta ring-2 ring-tinta bg-white' : 'border-borda bg-white hover:border-texto2'
        }`}
      >
        <span className="flex items-center gap-2 font-bold">
          {m.id === 'verde' || m.id === 'azul' ? (
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: m.id === 'verde' ? '#1F8A4C' : '#2B59C3' }} />
          ) : null}
          {m.titulo}
        </span>
        <span className="block text-xs text-texto2 mt-0.5">{m.desc}</span>
      </button>
    );
  };

  const blocoDemandaMes = verde ? (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div>
        <Rotulo htmlFor="inp-demandaMedida" obrigatorio>
          Demanda medida única
        </Rotulo>
        <CampoNumero id="inp-demandaMedida" valor={form.demandaMedida} aoMudar={(v) => set('demandaMedida', v)} unidade="kW" invalido={falta('Demanda medida única')} />
      </div>
      <Calculado
        rotulo="Demanda contratada única"
        valor={form.demandaContratada === null ? '—' : `${numero(form.demandaContratada, 2)} kW`}
        dica="Vem de “Sua unidade”."
      />
      <Calculado
        rotulo="Demanda faturável"
        valor={`${numero(Math.max(num(form.demandaMedida), num(form.demandaContratada)), 2)} kW`}
        dica="maior entre medida e contratada"
      />
    </div>
  ) : azul ? (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div>
        <Rotulo htmlFor="inp-demandaPontaKw" obrigatorio>
          Demanda medida ponta
        </Rotulo>
        <CampoNumero id="inp-demandaPontaKw" valor={form.demandaPontaKw} aoMudar={(v) => set('demandaPontaKw', v)} unidade="kW" invalido={falta('Demanda medida ponta')} />
      </div>
      <div>
        <Rotulo htmlFor="inp-demandaForaPontaKw" obrigatorio>
          Demanda medida fora ponta
        </Rotulo>
        <CampoNumero id="inp-demandaForaPontaKw" valor={form.demandaForaPontaKw} aoMudar={(v) => set('demandaForaPontaKw', v)} unidade="kW" invalido={falta('Demanda medida fora')} />
      </div>
      <Calculado rotulo="Faturável ponta" valor={`${numero(Math.max(num(form.demandaPontaKw), num(form.demandaContratadaPontaKw)), 2)} kW`} />
      <Calculado
        rotulo="Faturável fora ponta"
        valor={`${numero(Math.max(num(form.demandaForaPontaKw), num(form.demandaContratadaForaPontaKw)), 2)} kW`}
      />
    </div>
  ) : (
    <Aviso tom="info">
      Sem faturamento de demanda nesta modalidade — Optante B, Convencional Monômia e Branca faturam energia (e custo
      de disponibilidade) sem cobrança de demanda.
    </Aviso>
  );

  const blocoIsenta =
    verde || azul ? (
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-start">
        <div>
          <Marcador
            id="inp-demandaIsentaIcmsAtiva"
            marcado={form.demandaIsentaIcmsAtiva}
            aoMudar={(v) => set('demandaIsentaIcmsAtiva', v)}
            rotulo="Demanda contratada e não utilizada sem ICMS"
            dica="A fatura separa “Demanda isenta de ICMS”. Ligado: a API divide a demanda."
          />
        </div>
        {form.demandaIsentaIcmsAtiva ? (
          <div>
            <Rotulo htmlFor="inp-demandaIsentaIcms">Demanda isenta de ICMS</Rotulo>
            <CampoNumero
              id="inp-demandaIsentaIcms"
              valor={form.demandaIsentaIcms > 0 ? form.demandaIsentaIcms : null}
              aoMudar={set0('demandaIsentaIcms')}
              unidade="kW"
              placeholder="vazio = contratada − medida"
            />
            <Dica>Opcional. Parte da demanda que a fatura cobra sem ICMS; vazio, a API calcula contratada − medida.</Dica>
          </div>
        ) : null}
      </div>
    ) : null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[240px_minmax(0,1fr)] gap-6">
      {/* Dicas laterais */}
      <aside className="hidden lg:block space-y-4 no-print">
        <div className="sticky top-28 space-y-4">
          {DICAS.map((d) => (
            <div key={d.t} className="bg-white border border-borda rounded-2xl p-4">
              <div className="flex gap-2 font-bold text-sm">
                <span aria-hidden className="text-acento">●</span>
                {d.t}
              </div>
              <p className="text-sm text-texto2 mt-2 leading-relaxed">{d.d}</p>
            </div>
          ))}
        </div>
      </aside>

      <form
        className="space-y-6 min-w-0"
        onSubmit={(e) => {
          e.preventDefault();
          aoCalcular();
        }}
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Dados da fatura</h1>
            <p className="text-sm text-texto2 mt-1">
              Campos com <span className="text-alerta">*</span> são obrigatórios. Campo vazio nunca é tratado como zero:
              para zero, digite 0.
            </p>
          </div>
          <Botao className="bg-acento/15 border border-acento/60 text-tinta" onClick={aoPreencherExemplo}>
            Preencher com exemplo real
          </Botao>
        </div>

        {/* 1. Sua unidade */}
        <Cartao id="sec-unidade">
          <TituloSecao
            titulo="Sua unidade consumidora"
            sub="Identificação e enquadramento tarifário. Com isso o sistema busca as tarifas certas na base da ANEEL."
          />
          <div className="space-y-5">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Rotulo htmlFor="inp-ucCode">Código da UC</Rotulo>
                <CampoTexto id="inp-ucCode" valor={form.ucCode} aoMudar={(v) => set('ucCode', v)} mono placeholder="opcional" />
              </div>
              <div>
                <Rotulo htmlFor="inp-unidadeNome">Nome da unidade</Rotulo>
                <CampoTexto id="inp-unidadeNome" valor={form.unidadeNome} aoMudar={(v) => set('unidadeNome', v)} placeholder="opcional" />
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <Rotulo htmlFor="inp-distribuidora" obrigatorio>
                  Distribuidora
                </Rotulo>
                <CampoSelecao id="inp-distribuidora" valor={form.distribuidora} aoMudar={(v) => set('distribuidora', v)} opcoes={opcoesDistribuidora} vazio="Selecione…" />
              </div>
              <div>
                <Rotulo htmlFor="inp-subgrupo" obrigatorio>
                  Subgrupo
                </Rotulo>
                <CampoSelecao id="inp-subgrupo" valor={form.subgrupo} aoMudar={(v) => set('subgrupo', v)} opcoes={opcoesSubgrupo} vazio="Selecione…" />
              </div>
              <div>
                <Rotulo htmlFor="inp-dataReferencia" obrigatorio>
                  Data de referência
                </Rotulo>
                <CampoTexto id="inp-dataReferencia" valor={form.dataReferencia} aoMudar={(v) => set('dataReferencia', v)} mono placeholder="DD/MM/AAAA" />
                <Dica>Define a vigência das tarifas.</Dica>
              </div>
            </div>

            <div>
              <button
                type="button"
                className="text-sm font-semibold underline underline-offset-2 cursor-pointer"
                aria-expanded={classeAberta}
                onClick={() => setClasseAberta(!classeAberta)}
              >
                Classe, subclasse e detalhe tarifário
              </button>
              {classeAberta ? (
                <div className="mt-3 space-y-2">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                      <Rotulo htmlFor="inp-classe">Classe</Rotulo>
                      {opcoesClasse.length ? (
                        <CampoSelecao id="inp-classe" valor={form.classe} aoMudar={(v) => set('classe', v)} opcoes={[{ valor: 'Não se aplica', rotulo: 'Não se aplica' }, ...opcoesClasse.filter((o) => o.valor !== 'Não se aplica')]} />
                      ) : (
                        <CampoTexto id="inp-classe" valor={form.classe} aoMudar={(v) => set('classe', v)} />
                      )}
                    </div>
                    <div>
                      <Rotulo htmlFor="inp-subclasse">Subclasse</Rotulo>
                      <CampoTexto id="inp-subclasse" valor={form.subclasse} aoMudar={(v) => set('subclasse', v)} />
                    </div>
                    <div>
                      <Rotulo htmlFor="inp-detalhe">Detalhe</Rotulo>
                      <CampoTexto id="inp-detalhe" valor={form.detalhe} aoMudar={(v) => set('detalhe', v)} />
                    </div>
                  </div>
                  <Dica>
                    Classe/subclasse filtram a tarifa do Grupo B (Optante B, Convencional e Branca). Para Residencial/Rural
                    a classe é derivada automaticamente da atividade; sem classe informada e com tarifas ambíguas, a API
                    recusa o cálculo (nunca soma tarifas diferentes).
                  </Dica>
                </div>
              ) : null}
            </div>

            <div>
              <Rotulo>
                Modalidade faturada na conta
                <span className="text-alerta ml-0.5">*</span>
              </Rotulo>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">{MODALIDADES_PRINCIPAIS.map((m) => cartaoModalidade(m, true))}</div>
              <div className="text-sm text-texto2 mt-4 mb-2">Outras modalidades</div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">{OUTRAS_MODALIDADES.map((m) => cartaoModalidade(m, false))}</div>
              {pend.some((p) => p.includes('exige subgrupo') || p.includes('exigem subgrupo')) ? (
                <p className="text-sm text-alerta mt-2">
                  {pend.find((p) => p.includes('exige subgrupo') || p.includes('exigem subgrupo'))}
                </p>
              ) : null}
            </div>

            {verde ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Rotulo htmlFor="inp-demandaContratada" obrigatorio>
                    Demanda contratada única
                  </Rotulo>
                  <CampoNumero id="inp-demandaContratada" valor={form.demandaContratada} aoMudar={(v) => set('demandaContratada', v)} unidade="kW" invalido={falta('Demanda contratada')} />
                </div>
                <CampoKva form={form} set={set} />
              </div>
            ) : azul ? (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <Rotulo htmlFor="inp-demandaContratadaPontaKw" obrigatorio>
                    Demanda contratada ponta
                  </Rotulo>
                  <CampoNumero id="inp-demandaContratadaPontaKw" valor={form.demandaContratadaPontaKw} aoMudar={(v) => set('demandaContratadaPontaKw', v)} unidade="kW" invalido={falta('Demanda contratada ponta')} />
                </div>
                <div>
                  <Rotulo htmlFor="inp-demandaContratadaForaPontaKw" obrigatorio>
                    Demanda contratada fora ponta
                  </Rotulo>
                  <CampoNumero id="inp-demandaContratadaForaPontaKw" valor={form.demandaContratadaForaPontaKw} aoMudar={(v) => set('demandaContratadaForaPontaKw', v)} unidade="kW" invalido={falta('Demanda contratada fora')} />
                </div>
                <CampoKva form={form} set={set} />
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Aviso tom="info">Esta modalidade não tem demanda contratada: a fatura é só pela energia.</Aviso>
                {grupoA || optante ? <CampoKva form={form} set={set} obrigatorio={optante} /> : null}
              </div>
            )}

            {grupoA || optante ? (
              <div className="border-t border-borda2 pt-4">
                <button
                  type="button"
                  className="text-sm font-semibold underline underline-offset-2 cursor-pointer"
                  aria-expanded={optanteAberto}
                  onClick={() => setOptanteAberto(!optanteAberto)}
                >
                  Optante B — Grupo A faturado como Grupo B (art. 292){' '}
                  <span className={`font-normal ${optante ? 'text-alerta' : 'text-texto2'}`}>
                    {optante ? '· obrigatório' : '· opcional, avaliar como alternativa'}
                  </span>
                </button>
                {optanteAberto ? (
                  <div className="mt-3 space-y-4">
                    <Dica>
                      Elegibilidade: transformadores ≤ 112,5 kVA (ou ≤ 1.125 kVA se cooperativa de eletrificação rural);
                      hotelaria/pousada em área de veraneio ou turismo; ou refletores ≥ 2/3 da carga instalada em
                      atividades esportivas/parques agropecuários.
                      {!optante ? ' Sem a potência dos transformadores, o Optante B aparece como “não avaliado” (não como inelegível).' : ''}
                    </Dica>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div>
                        <Rotulo htmlFor="inp-atividade">Atividade econômica</Rotulo>
                        <CampoSelecao
                          id="inp-atividade"
                          valor={form.atividade}
                          aoMudar={(v) => set('atividade', v as InvoiceFormData['atividade'])}
                          opcoes={['Comercial ou Industrial', 'Rural', 'Residencial', 'Esportivo ou Parque Agropecuário'].map((x) => ({ valor: x, rotulo: x }))}
                        />
                      </div>
                      <div>
                        <Rotulo htmlFor="inp-tipoLigacao">Tipo de ligação</Rotulo>
                        <CampoSelecao
                          id="inp-tipoLigacao"
                          valor={form.tipoLigacao}
                          aoMudar={(v) => set('tipoLigacao', v as InvoiceFormData['tipoLigacao'])}
                          opcoes={['Trifásico', 'Bifásico', 'Monofásico'].map((x) => ({ valor: x, rotulo: x }))}
                        />
                      </div>
                      <div>
                        <Rotulo htmlFor="inp-cargaRefletoresKw">Carga dos refletores</Rotulo>
                        <CampoNumero id="inp-cargaRefletoresKw" valor={form.cargaRefletoresKw || null} aoMudar={set0('cargaRefletoresKw')} unidade="kW" />
                      </div>
                      <div>
                        <Rotulo htmlFor="inp-cargaInstaladaTotalKw">Carga instalada total</Rotulo>
                        <CampoNumero id="inp-cargaInstaladaTotalKw" valor={form.cargaInstaladaTotalKw || null} aoMudar={set0('cargaInstaladaTotalKw')} unidade="kW" />
                      </div>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                      <Marcador id="inp-coop" marcado={form.cooperativaEletrificacaoRural} aoMudar={(v) => set('cooperativaEletrificacaoRural', v)} rotulo="Cooperativa de eletrificação rural (≤ 1.125 kVA)" />
                      <Marcador id="inp-hotel" marcado={form.hotelariaTurismo} aoMudar={(v) => set('hotelariaTurismo', v)} rotulo="Hotelaria/pousada em área de veraneio ou turismo" />
                      <Marcador id="inp-prepag" marcado={form.prePagamento} aoMudar={(v) => set('prePagamento', v)} rotulo="Pré-pagamento (exceção do custo de disponibilidade)" />
                    </div>
                    <Dica>
                      Faturamento: tarifa Convencional do subgrupo B derivado da atividade (Residencial → B1; Rural → B2;
                      demais → B3). Classe/subclasse do perfil desambiguam a tarifa; monômia sem demanda/ultrapassagem;
                      custo de disponibilidade (30/50/100 kWh) quando o consumo for menor.
                    </Dica>
                  </div>
                ) : null}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Rotulo htmlFor="inp-tipoLigacao">Tipo de ligação</Rotulo>
                  <CampoSelecao
                    id="inp-tipoLigacao"
                    valor={form.tipoLigacao}
                    aoMudar={(v) => set('tipoLigacao', v as InvoiceFormData['tipoLigacao'])}
                    opcoes={['Trifásico', 'Bifásico', 'Monofásico'].map((x) => ({ valor: x, rotulo: x }))}
                  />
                  <Dica>Define o custo de disponibilidade (30/50/100 kWh).</Dica>
                </div>
              </div>
            )}
          </div>
        </Cartao>

        {/* 2. Consumo e demanda */}
        <Cartao id="sec-consumo">
          <TituloSecao
            titulo="Consumo e demanda"
            sub={
              <>
                Valores de energia ativa e de demanda <strong>faturados</strong> (coluna “Faturado” ou Histórico de
                Consumo): eles já incluem as perdas de transformação, quando houver.
              </>
            }
            acao={
              <Segmentos
                rotuloAria="Entrada de consumo"
                valor={aba}
                aoMudar={setAba}
                opcoes={[
                  { valor: 'mes', rotulo: 'Uma fatura' },
                  { valor: 'historico', rotulo: 'Histórico de 12 meses' },
                ]}
              />
            }
          />

          {aba === 'mes' ? (
            <div className="space-y-5">
              <h3 className="font-bold">Energia ativa do mês</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <Rotulo htmlFor="inp-consumoPonta" obrigatorio={grupoA || mod === 'branca'}>
                    Consumo ponta
                  </Rotulo>
                  <CampoNumero id="inp-consumoPonta" valor={form.consumoPonta} aoMudar={(v) => set('consumoPonta', v)} unidade="kWh" invalido={falta('Consumo ponta')} />
                </div>
                <div>
                  <Rotulo htmlFor="inp-consumoForaPonta" obrigatorio>
                    Consumo fora ponta
                  </Rotulo>
                  <CampoNumero id="inp-consumoForaPonta" valor={form.consumoForaPonta} aoMudar={(v) => set('consumoForaPonta', v)} unidade="kWh" invalido={falta('Consumo fora')} />
                </div>
                <div>
                  <Rotulo htmlFor="inp-consumoIntermediario" obrigatorio={mod === 'branca'}>
                    Consumo intermediário
                  </Rotulo>
                  <CampoNumero id="inp-consumoIntermediario" valor={form.consumoIntermediario} aoMudar={(v) => set('consumoIntermediario', v)} unidade="kWh" invalido={falta('Consumo intermediário')} />
                  <Dica>Só na Branca.</Dica>
                </div>
                <Calculado rotulo="Consumo total" valor={`${numero(consumoTotal)} kWh`} />
              </div>
              <div className="border-t border-borda2 pt-5 space-y-4">
                <h3 className="font-bold">Demanda do mês</h3>
                {blocoDemandaMes}
                {blocoIsenta}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <Rotulo htmlFor="inp-historico12">Cole aqui o histórico</Rotulo>
                <textarea
                  id="inp-historico12"
                  rows={5}
                  value={form.historico12}
                  onChange={(e) => set('historico12', e.target.value)}
                  className="w-full rounded-xl border border-borda px-3.5 py-2.5 num text-sm outline-none focus:border-tinta focus:ring-2 focus:ring-acento/40"
                  placeholder={
                    'Por posto: MM/AAAA; demanda ponta; demanda fora ponta; consumo ponta; consumo fora ponta\n12/2023; 193; 200; 7.000; 54.950\nVerde (demanda única): MM/AAAA; demanda; consumo ponta; consumo fora ponta\n11/2023; 231; 8.750; 63.000'
                  }
                />
                <Dica>
                  Uma linha por mês, do quadro “Histórico de Consumo” da fatura (valores faturados). Sem histórico, o
                  planejamento usa só o mês desta fatura (resultado indicativo). Meses ausentes não entram no cálculo —
                  nunca viram zero.
                </Dica>
                {hist.meses.length > 0 && hist.erros.length === 0 ? (
                  <p className="text-sm font-semibold text-verde mt-2">
                    ✓ Reconhecemos {hist.meses.length} {hist.meses.length === 1 ? 'mês' : 'meses'}
                    {plano.periodo ? ` (planejamento ${plano.periodo})` : ''}. Confira na tabela.
                  </p>
                ) : null}
                {hist.erros.length > 0 ? (
                  <ul className="text-sm text-alerta list-disc pl-5 mt-2">
                    {hist.erros.map((e) => (
                      <li key={e}>{e}</li>
                    ))}
                  </ul>
                ) : null}
              </div>

              <div
                className="rounded-xl border-2 border-dashed border-borda p-5 text-center"
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  void lerCsv(e.dataTransfer.files[0]);
                }}
              >
                <div className="font-bold">Arraste o arquivo CSV aqui</div>
                <div className="text-sm text-texto2 mt-1">ou escolha no computador</div>
                <input
                  type="file"
                  accept=".csv,text/csv"
                  aria-label="Arquivo CSV do histórico"
                  className="mt-3 text-sm max-w-full"
                  onChange={(e) => void lerCsv(e.target.files?.[0])}
                />
                <div>
                  <button type="button" onClick={baixarModelo} className="mt-2 text-sm font-semibold underline cursor-pointer">
                    Baixar planilha modelo
                  </button>
                </div>
              </div>

              {linhas.length > 0 ? (
                <div className="rounded-xl border border-borda overflow-x-auto max-w-full">
                  <table className="w-full text-sm min-w-[560px]">
                    <thead className="bg-fundo text-texto2">
                      <tr>
                        <th className="text-left px-3 py-2 font-semibold">Mês</th>
                        <th className="text-right px-2 py-2 font-semibold">Demanda ponta (kW)</th>
                        <th className="text-right px-2 py-2 font-semibold">Demanda fora ponta / única (kW)</th>
                        <th className="text-right px-2 py-2 font-semibold">Consumo ponta (kWh)</th>
                        <th className="text-right px-2 py-2 font-semibold">Consumo fora ponta (kWh)</th>
                        <th className="w-8" />
                      </tr>
                    </thead>
                    <tbody>
                      {linhas.map((l, i) => {
                        const iso = `${l.mes.slice(3)}-${l.mes.slice(0, 2)}-15`;
                        const fora = foraPadrao.some((f) => f.mes === iso);
                        const celula = (campo: keyof LinhaTabela, rotulo: string) => (
                          <td className="px-1.5 py-1">
                            <input
                              aria-label={`${rotulo} ${l.mes}`}
                              value={l[campo]}
                              placeholder={campo === 'dPonta' ? '—' : ''}
                              onChange={(e) => setLinhas(linhas.map((x, j) => (j === i ? { ...x, [campo]: e.target.value } : x)))}
                              className={`w-full h-9 rounded-lg border px-2 text-right num outline-none focus:border-tinta ${
                                fora && (campo === 'ePonta' || campo === 'eFora') ? 'border-acento bg-acento/10' : 'border-borda'
                              }`}
                            />
                          </td>
                        );
                        return (
                          <tr key={`${l.mes}-${i}`} className="border-t border-borda2">
                            <td className="px-3 py-1 font-semibold num">{/^\d{2}\/\d{4}$/.test(l.mes) ? rotuloMes(iso) : l.mes}</td>
                            {celula('dPonta', 'Demanda ponta')}
                            {celula('dFora', 'Demanda fora ponta')}
                            {celula('ePonta', 'Consumo ponta')}
                            {celula('eFora', 'Consumo fora ponta')}
                            <td className="pr-2">
                              <button
                                type="button"
                                aria-label={`Remover ${l.mes}`}
                                className="text-texto2 hover:text-alerta cursor-pointer"
                                onClick={() => setLinhas(linhas.filter((_, j) => j !== i))}
                              >
                                ×
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : null}
              <button type="button" onClick={adicionarMes} className="text-sm font-semibold underline cursor-pointer">
                + Adicionar mês na tabela
              </button>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Calculado rotulo="Consumo total no período" valor={`${numero(consumoPeriodo)} kWh`} />
                <Calculado
                  rotulo="Maior demanda faturável"
                  valor={`${numero(Math.max(maiorDemanda, contratadaRef), 2)} kW`}
                  dica="máx(medida, contratada) no período"
                />
              </div>
              {blocoIsenta}
              {foraPadrao.length > 0 ? (
                <Aviso>
                  Consumo longe da média do período (±25%):{' '}
                  {foraPadrao
                    .map((f) => `${rotuloMes(f.mes)} ${f.desvio < 0 ? '−' : '+'}${numero(Math.abs(f.desvio) * 100)}%`)
                    .join(' · ')}
                  . Se estiver certo, pode seguir.
                </Aviso>
              ) : null}
              {plano.avisos.map((a) => (
                <Aviso key={a} tom="info">
                  {a}
                </Aviso>
              ))}
              <Aviso tom="info">
                O mês da fatura (aba “Uma fatura”) também é obrigatório: é ele que a etapa 2 recalcula e confere.
              </Aviso>
            </div>
          )}
        </Cartao>

        {/* 3. Tarifas, impostos e adicionais */}
        <Cartao id="sec-tarifas">
          <TituloSecao titulo="Tarifas, impostos e adicionais" sub="Abra uma seção para conferir ou mudar. As opcionais abrem quando a fatura tem o item." />
          <div className="space-y-3">
            <Sanfona
              id="san-bandeira"
              letra="A"
              titulo="Bandeira tarifária"
              resumo={form.bandeiraAutomatica ? `Automática${bandeiraAtivaApi ? ` · vigente: ${bandeiraAtivaApi}` : ''}` : `Fixa: ${opcoesBandeira.find((b) => b.id === form.bandeira)?.rotulo ?? form.bandeira}`}
              aberta={aberta('A', !form.bandeiraAutomatica)}
              aoAlternar={() => alternar('A', !form.bandeiraAutomatica)}
            >
              <Marcador
                id="inp-bandeiraAutomatica"
                marcado={form.bandeiraAutomatica}
                aoMudar={(v) => aoMudar({ ...form, bandeiraAutomatica: v, bandeira: v ? 'verde' : form.bandeira })}
                rotulo="Automática (bandeira real de cada mês)"
                dica="Recomendado. A API busca na ANEEL se o mês foi verde, amarela ou vermelha."
              />
              {!form.bandeiraAutomatica ? (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {opcoesBandeira.map((b) => (
                    <button
                      key={b.id}
                      type="button"
                      aria-pressed={form.bandeira === b.id}
                      onClick={() => set('bandeira', b.id)}
                      className={`rounded-xl border px-3 py-2 text-sm font-semibold cursor-pointer ${form.bandeira === b.id ? 'border-tinta ring-2 ring-tinta' : 'border-borda'}`}
                    >
                      {b.rotulo}
                      <span className="block text-xs text-texto2 num">R$ {numero(b.kwh, 5)}/kWh</span>
                    </button>
                  ))}
                </div>
              ) : null}
              <Dica>Desligue a opção automática para escolher uma bandeira fixa.</Dica>
            </Sanfona>

            <Sanfona
              id="san-tributos"
              letra="B"
              titulo="Tributos"
              resumo={
                form.aplicarTributos
                  ? `PIS ${fmtPct(form.pis)} · COFINS ${fmtPct(form.cofins)} · ICMS ${fmtPct(form.icms)} (${form.tipoIcms === 'fora' ? 'por fora' : 'por dentro'})`
                  : 'Sem tributos (valores líquidos)'
              }
              aberta={aberta('B', true)}
              aoAlternar={() => alternar('B', true)}
            >
              <Marcador
                id="inp-aplicarTributos"
                marcado={form.aplicarTributos}
                aoMudar={(v) => set('aplicarTributos', v)}
                rotulo="Aplicar PIS/COFINS/ICMS"
                dica="Desligue para ver os valores líquidos, sem tributos."
              />
              {form.aplicarTributos ? (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                      <Rotulo htmlFor="inp-pis" obrigatorio>
                        PIS/PASEP
                      </Rotulo>
                      <CampoNumero id="inp-pis" valor={form.pis} aoMudar={(v) => set('pis', v)} unidade="%" invalido={falta('PIS')} />
                    </div>
                    <div>
                      <Rotulo htmlFor="inp-cofins" obrigatorio>
                        COFINS
                      </Rotulo>
                      <CampoNumero id="inp-cofins" valor={form.cofins} aoMudar={(v) => set('cofins', v)} unidade="%" invalido={falta('COFINS')} />
                    </div>
                    <div>
                      <Rotulo htmlFor="inp-icms" obrigatorio>
                        ICMS
                      </Rotulo>
                      <CampoNumero id="inp-icms" valor={form.icms} aoMudar={(v) => set('icms', v)} unidade="%" invalido={falta('ICMS')} />
                      <Dica>Digite 0 se a unidade é isenta.</Dica>
                    </div>
                  </div>
                  <div>
                    <Rotulo>Tipo de ICMS</Rotulo>
                    <Segmentos
                      rotuloAria="Tipo de ICMS"
                      valor={form.tipoIcms}
                      aoMudar={(v) => set('tipoIcms', v)}
                      opcoes={[
                        { valor: 'fora', rotulo: 'Por fora' },
                        { valor: 'dentro', rotulo: 'Por dentro' },
                      ]}
                    />
                    <p className="num text-xs text-texto2 mt-2">
                      {form.tipoIcms === 'fora'
                        ? 'preço = tarifa ÷ [(1 − PIS − COFINS) × (1 − ICMS)]'
                        : 'preço = tarifa ÷ (1 − PIS − COFINS − ICMS)'}
                    </p>
                    <Dica>
                      {form.tipoIcms === 'fora'
                        ? 'Multiplicativa. Reproduz a fatura Copel validada (docs/validacao_conta_real_copel_verde_2023.md).'
                        : 'Aditiva (forma da fonte oficial).'}{' '}
                      Na parcela de demanda isenta: preço = tarifa ÷ (1 − PIS − COFINS).
                    </Dica>
                  </div>
                  <Marcador
                    id="inp-arredondar"
                    marcado={form.arredondarCentavos}
                    aoMudar={(v) => set('arredondarCentavos', v)}
                    rotulo="Arredondar linhas a centavos"
                    dica="Como a fatura impressa."
                  />
                </>
              ) : null}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Rotulo htmlFor="inp-cipCosip">CIP/COSIP (iluminação pública)</Rotulo>
                  <CampoNumero id="inp-cipCosip" valor={form.cipCosip || null} aoMudar={set0('cipCosip')} unidade="R$/mês" placeholder="0,00" />
                  <Dica>Fora do custo técnico (premissa D4): soma no total, não entra nas comparações de tarifa.</Dica>
                </div>
              </div>
            </Sanfona>

            <Sanfona
              id="san-reativos"
              letra="C"
              titulo="Reativos excedentes"
              resumo={`Opcional · art. 304 da REN 1.000/2021 · ${temReativo ? 'informados' : 'não informados'}`}
              aberta={aberta('C', temReativo)}
              aoAlternar={() => alternar('C', temReativo)}
            >
              <Marcador
                id="inp-buscarReativoAuto"
                marcado={form.buscarReativoAuto}
                aoMudar={(v) => set('buscarReativoAuto', v)}
                rotulo="Buscar tarifa de reativo automaticamente (VRERE/VRDRE)"
              />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {(
                  [
                    ['consumoReativoPonta', 'Consumo de energia reativa excedente — ponta', 'kVArh'],
                    ['consumoReativoForaPonta', 'Consumo de energia reativa excedente — fora ponta', 'kVArh'],
                    ['demandaReativaPonta', 'Demanda de potência reativa excedente — ponta', 'kVAr'],
                    ['demandaReativaForaPonta', 'Demanda de potência reativa excedente — fora ponta', 'kVAr'],
                    ['reativoEnergiaCapacitiva', 'Energia reativa capacitiva (0h–6h)', 'kVArh'],
                    ['reativoDemandaCapacitiva', 'Demanda reativa capacitiva (0h–6h)', 'kVAr'],
                  ] as const
                ).map(([campo, rotulo, un]) => (
                  <div key={campo}>
                    <Rotulo htmlFor={`inp-${campo}`}>{rotulo}</Rotulo>
                    <CampoNumero id={`inp-${campo}`} valor={form[campo] || null} aoMudar={set0(campo)} unidade={un} placeholder="0" />
                  </div>
                ))}
              </div>
              {!form.buscarReativoAuto ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Rotulo htmlFor="inp-tarifaReativoEnergia" obrigatorio={temReativo}>
                      Tarifa — energia reativa
                    </Rotulo>
                    <CampoNumero id="inp-tarifaReativoEnergia" valor={form.tarifaReativoEnergia || null} aoMudar={set0('tarifaReativoEnergia')} unidade="R$/kVArh" invalido={falta('Tarifa de energia reativa')} />
                  </div>
                  <div>
                    <Rotulo htmlFor="inp-tarifaReativoDemanda" obrigatorio={temReativo}>
                      Tarifa — demanda reativa
                    </Rotulo>
                    <CampoNumero id="inp-tarifaReativoDemanda" valor={form.tarifaReativoDemanda || null} aoMudar={set0('tarifaReativoDemanda')} unidade="R$/kVAr" invalido={falta('Tarifa de demanda reativa')} />
                  </div>
                </div>
              ) : null}
              <Marcador
                id="inp-tributarReativos"
                marcado={form.tributarReativos}
                aoMudar={(v) => set('tributarReativos', v)}
                rotulo="Tributar reativos excedentes (PIS/COFINS/ICMS)"
                dica="Faturas CEMIG/Equatorial."
              />
            </Sanfona>

            <Sanfona
              id="san-outros"
              letra="D"
              titulo="Outros valores da fatura"
              resumo="Opcional · outros lançamentos e leitura do mês anterior"
              aberta={aberta('D', form.outrosValores > 0 || form.percentualConsumoMesAnterior > 0)}
              aoAlternar={() => alternar('D', form.outrosValores > 0 || form.percentualConsumoMesAnterior > 0)}
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Rotulo htmlFor="inp-outrosValores">Outros valores</Rotulo>
                  <CampoNumero id="inp-outrosValores" valor={form.outrosValores || null} aoMudar={set0('outrosValores')} unidade="R$" placeholder="0,00" />
                  <Dica>Multas, juros, serviços e iluminação pública cobrados na fatura (fora do custo técnico, D4).</Dica>
                </div>
                <div>
                  <Rotulo htmlFor="inp-percentual">% do consumo do mês anterior</Rotulo>
                  <CampoNumero
                    id="inp-percentual"
                    valor={form.percentualConsumoMesAnterior > 0 ? Number((form.percentualConsumoMesAnterior * 100).toFixed(4)) : null}
                    aoMudar={(v) => set('percentualConsumoMesAnterior', v === null ? 0 : Math.min(100, v) / 100)}
                    unidade="%"
                    placeholder="0"
                  />
                  <Dica>Quando a leitura pega parte do mês anterior (tarifas do mês anterior nessa parte).</Dica>
                </div>
              </div>
            </Sanfona>

            <Sanfona
              id="san-acl"
              letra="E"
              titulo="Mercado livre (ACL)"
              resumo={`Opcional · compare uma proposta com o E-PI${form.precoMedioACL > 0 ? ` · proposta R$ ${numero(form.precoMedioACL, 2)}/MWh` : ''}`}
              aberta={aberta('E', form.precoMedioACL > 0 || form.opexMensal > 0 || form.capex > 0 || form.encargosAcl !== null)}
              aoAlternar={() => alternar('E', form.precoMedioACL > 0 || form.opexMensal > 0 || form.capex > 0 || form.encargosAcl !== null)}
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Rotulo htmlFor="inp-precoMedioACL">Preço de uma proposta no ACL</Rotulo>
                  <CampoNumero id="inp-precoMedioACL" valor={form.precoMedioACL || null} aoMudar={set0('precoMedioACL')} unidade="R$/MWh" />
                  <Dica>Se você já tem uma proposta. Em branco, o sistema só calcula o E-PI.</Dica>
                </div>
                <div>
                  <Rotulo htmlFor="inp-encargosAcl">Encargos do ACL</Rotulo>
                  <CampoNumero id="inp-encargosAcl" valor={form.encargosAcl} aoMudar={(v) => set('encargosAcl', v)} unidade="R$/MWh" />
                  <Dica>ESS/EER e contribuição CCEE. Vazio: fica fora do E-PI e isso aparece nas premissas.</Dica>
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <Rotulo htmlFor="inp-opexMensal">OPEX da migração</Rotulo>
                  <CampoNumero id="inp-opexMensal" valor={form.opexMensal || null} aoMudar={set0('opexMensal')} unidade="R$/mês" />
                  <Dica>gestão, CCEE, comercializadora</Dica>
                </div>
                <div>
                  <Rotulo htmlFor="inp-capex">CAPEX da migração</Rotulo>
                  <CampoNumero id="inp-capex" valor={form.capex || null} aoMudar={set0('capex')} unidade="R$" />
                  <Dica>adequação da medição (SMF)</Dica>
                </div>
                <div>
                  <Rotulo htmlFor="inp-horizonteMeses" obrigatorio={form.capex > 0}>
                    Amortizar o CAPEX em
                  </Rotulo>
                  <CampoNumero id="inp-horizonteMeses" valor={form.horizonteMeses || null} aoMudar={set0('horizonteMeses')} unidade="meses" inteiro invalido={falta('Meses de amortização')} />
                </div>
              </div>
              <Dica>
                Sem OPEX e CAPEX o sistema calcula o E-PI simplificado (perdas k = 3%). Com eles, o E-PI desconta os custos
                de migração.
              </Dica>
            </Sanfona>

            <Sanfona
              id="san-total"
              letra="F"
              titulo="Total da fatura"
              resumo={form.totalFatura !== null ? `R$ ${numero(form.totalFatura, 2)} · conferência ligada` : 'Opcional · para conferir o recálculo'}
              aberta={aberta('F', form.totalFatura !== null)}
              aoAlternar={() => alternar('F', form.totalFatura !== null)}
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Rotulo htmlFor="inp-totalFatura">Total a pagar impresso na fatura</Rotulo>
                  <CampoNumero id="inp-totalFatura" valor={form.totalFatura} aoMudar={(v) => set('totalFatura', v)} unidade="R$" />
                  <Dica>A etapa 2 mostra a diferença entre o recalculado e a conta.</Dica>
                </div>
              </div>
            </Sanfona>
          </div>
        </Cartao>

        {/* 4. Tudo certo? */}
        <Cartao id="sec-resumo">
          <TituloSecao titulo="Tudo certo?" sub="Confira o resumo. Toque em “Editar” para voltar a um bloco." />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Resumo
              titulo="Unidade"
              aoEditar={() => irPara('sec-unidade')}
              itens={[
                ['UC', [form.unidadeNome, form.ucCode].filter(Boolean).join(' · ') || '—'],
                ['Distribuidora', [form.distribuidora || '—', form.subgrupo].filter(Boolean).join(' · ')],
                ['Data de referência', form.dataReferencia || '—'],
                ['Modalidade', [...MODALIDADES_PRINCIPAIS, ...OUTRAS_MODALIDADES].find((m) => m.id === mod)?.titulo ?? mod],
                [
                  'Demanda contratada',
                  verde
                    ? form.demandaContratada === null ? '—' : `${numero(form.demandaContratada, 2)} kW`
                    : azul
                      ? `${form.demandaContratadaPontaKw ?? '—'} / ${form.demandaContratadaForaPontaKw ?? '—'} kW`
                      : 'não se aplica',
                ],
                ['Transformadores', form.potenciaTransformadoresKva === null ? 'não informado' : `${numero(form.potenciaTransformadoresKva, 1)} kVA`],
              ]}
            />
            <Resumo
              titulo="Consumo e demanda"
              aoEditar={() => irPara('sec-consumo')}
              itens={[
                ['Consumo do mês', `${numero(consumoTotal)} kWh`],
                ['Histórico', hist.meses.length ? `${hist.meses.length} meses${plano.periodo ? ` · ${plano.periodo}` : ''}` : 'sem histórico (só o mês)'],
                ['Maior demanda medida', hist.meses.length ? `${numero(maiorDemanda, 2)} kW` : '—'],
                ['Demanda isenta de ICMS', form.demandaIsentaIcmsAtiva ? (form.demandaIsentaIcms > 0 ? `${numero(form.demandaIsentaIcms, 2)} kW` : 'contratada − medida') : 'desligada'],
              ]}
            />
            <div className="md:col-span-2">
              <Resumo
                titulo="Tarifas e adicionais"
                aoEditar={() => irPara('sec-tarifas')}
                itens={[
                  ['Bandeira', form.bandeiraAutomatica ? 'automática' : (opcoesBandeira.find((b) => b.id === form.bandeira)?.rotulo ?? form.bandeira)],
                  ['PIS + COFINS', form.aplicarTributos ? `${numero(num(form.pis) + num(form.cofins), 2)}%` : 'sem tributos'],
                  ['ICMS', form.aplicarTributos ? `${fmtPct(form.icms)} · ${form.tipoIcms === 'fora' ? 'por fora' : 'por dentro'}` : 'sem tributos'],
                  ['CIP/COSIP · outros', `R$ ${numero(form.cipCosip, 2)} · R$ ${numero(form.outrosValores, 2)}`],
                  ['Reativos', temReativo ? 'informados' : 'não informados'],
                  ['Proposta ACL', form.precoMedioACL > 0 ? `R$ ${numero(form.precoMedioACL, 2)}/MWh` : 'não informada (só E-PI)'],
                  ['Mês anterior na leitura', form.percentualConsumoMesAnterior > 0 ? pct(form.percentualConsumoMesAnterior) : '0%'],
                  ['Total da fatura', form.totalFatura !== null ? `R$ ${numero(form.totalFatura, 2)}` : 'sem conferência'],
                ]}
              />
            </div>
          </div>

          {pendencias.length > 0 ? (
            <div className="mt-5">
              <Aviso tom="erro">
                <strong>Preencha antes de calcular ({pendencias.length}):</strong>
                <ul className="list-disc pl-5 mt-1 space-y-0.5">
                  {pendencias.map((p) => (
                    <li key={p}>{p}</li>
                  ))}
                </ul>
                <p className="mt-1">Campos vazios não são tratados como zero. Para zero, digite 0.</p>
              </Aviso>
            </div>
          ) : null}

          <Botao type="submit" variante="primario" className="w-full mt-5 text-base py-4" disabled={carregando}>
            {carregando ? 'Calculando na API…' : 'Calcular e ver a fatura →'}
          </Botao>
        </Cartao>
      </form>
    </div>
  );
};

const fmtPct = (v: number | null) => (v === null ? '—' : `${numero(v, Number.isInteger(v) ? 0 : 2)}%`);

const CampoKva: React.FC<{
  form: InvoiceFormData;
  set: <K extends keyof InvoiceFormData>(c: K, v: InvoiceFormData[K]) => void;
  obrigatorio?: boolean;
}> = ({ form, set, obrigatorio }) => (
  <div>
    <Rotulo htmlFor="inp-kva" obrigatorio={obrigatorio}>
      Potência dos transformadores
    </Rotulo>
    <CampoNumero id="inp-kva" valor={form.potenciaTransformadoresKva} aoMudar={(v) => set('potenciaTransformadoresKva', v)} unidade="kVA" />
    <Dica>
      Até 112,5 kVA (ou 1.125 kVA em cooperativa rural) a unidade pode optar pelo Grupo B (art. 292). Vazio: Optante B
      “não avaliado”.
    </Dica>
  </div>
);

const Resumo: React.FC<{ titulo: string; aoEditar: () => void; itens: [string, string][] }> = ({ titulo, aoEditar, itens }) => (
  <div className="border border-borda rounded-xl p-4 h-full">
    <div className="flex justify-between items-center mb-2">
      <h3 className="font-bold">{titulo}</h3>
      <button type="button" onClick={aoEditar} className="text-sm font-semibold underline cursor-pointer">
        Editar
      </button>
    </div>
    <dl>
      {itens.map(([k, v]) => (
        <div key={k} className="flex justify-between gap-4 py-2 border-b border-borda2 last:border-0 text-sm">
          <dt className="text-texto2">{k}</dt>
          <dd className="font-semibold text-right min-w-0 break-words">{v}</dd>
        </div>
      ))}
    </dl>
  </div>
);
