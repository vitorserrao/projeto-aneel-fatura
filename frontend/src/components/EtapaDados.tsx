/**
 * Etapa 1 — Dados em 5 passos (Main.dc.html, versão aprovada na rodada 2).
 * Mesmo mapeamento de InvoiceFormData para a API; obrigatórios e pendências
 * seguem validarFormulario. Campo vazio fica vazio (null) — nunca vira zero.
 */
import React from 'react';
import type { InvoiceFormData, TariffModalidade } from '../types/energy';
import { BandeiraOpcao, bandeiraApiParaForm, dataReferenciaIso, lerHistorico } from '../lib/api';
import { ehGrupoA, montarMesesPlanejamento, num, validarFormulario } from '../lib/validacao';
import { trocarModalidade } from '../lib/formulario';
import { DISTRIBUIDORAS_APOIO, SUBGROUPS } from '../lib/listas';
import {
  LinhaTabela,
  linhasDeMeses,
  mesesForaDoPadrao,
  modeloCsv,
  textoDeCsv,
  textoDeLinhas,
} from '../lib/historico';
import { numero } from '../lib/formato';
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
  bandeirasApi: BandeiraOpcao[] | null;
  bandeiraAtivaApi: string | null;
  /** Competência (AAAA-MM) da bandeira automática devolvida pela API. */
  bandeiraCompetencia: string | null;
}

export type Passo = 1 | 2 | 3 | 4 | 5;

export const PASSOS: { n: Passo; t: string }[] = [
  { n: 1, t: 'Sua unidade' },
  { n: 2, t: 'Demanda e consumo' },
  { n: 3, t: 'Tarifas e tributos' },
  { n: 4, t: 'Histórico' },
  { n: 5, t: 'Revisar e calcular' },
];

/** Passo onde se corrige cada pendência de validarFormulario. */
export function passoDaPendencia(p: string): Passo {
  if (/^(Distribuidora|Subgrupo|Data|Modalidade|Branca|Optante B)/.test(p)) return 1;
  if (/^(PIS|COFINS|ICMS|Valor da bandeira)/.test(p)) return 3;
  if (/^Histórico/.test(p)) return 4;
  if (/^Meses de amortização/.test(p)) return 5;
  return 2;
}

const PRINCIPAIS_A: { id: TariffModalidade; titulo: string; desc: string }[] = [
  { id: 'verde', titulo: 'Horária Verde', desc: 'Uma demanda contratada; energia na ponta mais cara' },
  { id: 'azul', titulo: 'Horária Azul', desc: 'Demanda contratada na ponta e fora de ponta' },
];
const OUTRAS_A: { id: TariffModalidade; titulo: string; desc: string }[] = [
  { id: 'optante_b', titulo: 'Optante B', desc: 'Grupo A faturado como B (art. 292)' },
];
const MODALIDADES_B: { id: TariffModalidade; titulo: string; desc: string }[] = [
  { id: 'convencional', titulo: 'Convencional', desc: 'Monômia: só energia' },
  { id: 'branca', titulo: 'Branca', desc: 'Três postos: ponta, intermediário e fora' },
];
const TODAS = [...PRINCIPAIS_A, ...OUTRAS_A, ...MODALIDADES_B];

const DICAS = [
  {
    t: 'Onde encontro isso?',
    d: (
      <>
        Na primeira página da fatura, perto do nome do cliente: <strong>subgrupo</strong> (ex.: A4),{' '}
        <strong>modalidade tarifária</strong> e <strong>demanda contratada</strong>.
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
        Bandeira automática e tributos obrigatórios. Reativos, outros valores e a conferência com a conta são opcionais.
        O E-PI e o mercado livre ficam na análise.
      </>
    ),
  },
];

const fmtPct = (v: number | null) => (v === null ? '—' : `${numero(v, Number.isInteger(v) ? 0 : 2)}%`);
const fmtKw = (v: number | null) => (v === null ? '—' : `${numero(v, Number.isInteger(v) ? 0 : 2)} kW`);

export const EtapaDados: React.FC<Props> = (props) => {
  const { form, aoMudar, aoCalcular, aoPreencherExemplo, carregando, pendencias } = props;
  const [passo, setPasso] = React.useState<Passo>(1);
  const topo = React.useRef<HTMLDivElement>(null);
  const irPasso = (p: Passo) => {
    setPasso(p);
    topo.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };
  // Pendências do cálculo: leva ao passo 5 para mostrá-las.
  React.useEffect(() => {
    if (pendencias.length > 0) setPasso(5);
  }, [pendencias]);

  const pend = validarFormulario(form);
  const pendPorPasso = (p: Passo) => pend.filter((x) => passoDaPendencia(x) === p).length;

  return (
    <div ref={topo} className="grid grid-cols-1 lg:grid-cols-[240px_minmax(0,1fr)] gap-6 scroll-mt-24">
      <aside className="hidden lg:block no-print">
        <div className="sticky top-28 space-y-4">
          <nav aria-label="Passos do formulário" className="bg-white border border-borda rounded-2xl p-3">
            <ol className="space-y-1">
              {PASSOS.map((s) => (
                <li key={s.n}>
                  <button
                    type="button"
                    aria-current={passo === s.n ? 'step' : undefined}
                    onClick={() => irPasso(s.n)}
                    className={`w-full flex items-center gap-2 rounded-lg px-2 py-2 text-sm text-left cursor-pointer ${
                      passo === s.n ? 'bg-tinta text-white' : 'hover:bg-fundo'
                    }`}
                  >
                    <span className={`w-6 h-6 shrink-0 rounded-full flex items-center justify-center text-xs font-bold ${passo === s.n ? 'bg-acento text-tinta' : 'bg-fundo'}`}>
                      {s.n}
                    </span>
                    <span className="flex-1">{s.t}</span>
                    {pendPorPasso(s.n) > 0 && s.n !== 5 ? (
                      <span className="text-[11px] font-semibold text-alerta" title="pendências">
                        {pendPorPasso(s.n)}
                      </span>
                    ) : null}
                  </button>
                </li>
              ))}
            </ol>
          </nav>
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
        className="space-y-5 min-w-0"
        onSubmit={(e) => {
          e.preventDefault();
          if (passo < 5) irPasso((passo + 1) as Passo);
          else aoCalcular();
        }}
      >
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="text-sm text-texto2">
              Etapa {passo} de 5 · <strong className="text-tinta">{PASSOS[passo - 1].t}</strong>
            </div>
            <div className="h-1.5 rounded-full bg-borda2 mt-2 overflow-hidden" role="progressbar" aria-valuemin={1} aria-valuemax={5} aria-valuenow={passo}>
              <div className="h-full bg-tinta transition-all" style={{ width: `${(passo / 5) * 100}%` }} />
            </div>
          </div>
          <Botao className="bg-acento/15 border border-acento/60 text-tinta" onClick={aoPreencherExemplo}>
            Preencher com exemplo real
          </Botao>
        </div>

        {passo === 1 ? <PassoUnidade {...props} /> : null}
        {passo === 2 ? <PassoDemanda form={form} aoMudar={aoMudar} /> : null}
        {passo === 3 ? <PassoTarifas {...props} /> : null}
        {passo === 4 ? <PassoHistorico form={form} aoMudar={aoMudar} /> : null}
        {passo === 5 ? (
          <PassoRevisar {...props} aoEditar={irPasso} pend={pend} carregando={carregando} />
        ) : null}

        <div className="flex justify-between gap-3 no-print">
          <Botao onClick={() => irPasso(Math.max(1, passo - 1) as Passo)} disabled={passo === 1} className={passo === 1 ? 'invisible' : ''}>
            Voltar
          </Botao>
          {passo < 5 ? (
            <Botao type="submit" variante="escuro">
              Continuar
            </Botao>
          ) : null}
        </div>
      </form>
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* Passo 1 — Sua unidade                                               */
/* ------------------------------------------------------------------ */

const PassoUnidade: React.FC<Props> = ({ form, aoMudar, distribuidorasApi, subgruposApi }) => {
  const set = <K extends keyof InvoiceFormData>(c: K, v: InvoiceFormData[K]) => aoMudar({ ...form, [c]: v });
  const pend = validarFormulario(form);
  const falta = (t: string) => pend.some((p) => p.startsWith(t));
  const [grupo, setGrupo] = React.useState<'A' | 'B'>(
    form.subgrupo.trim().toUpperCase().startsWith('B') || form.modalidadeAtual === 'branca' || form.modalidadeAtual === 'convencional' ? 'B' : 'A',
  );
  const mod = form.modalidadeAtual;
  const optante = mod === 'optante_b';

  const subgrupos = (subgruposApi && subgruposApi.length ? subgruposApi : SUBGROUPS.map((s) => s.id))
    .filter((s) => s.toUpperCase().startsWith(grupo))
    .map((s) => ({ valor: s, rotulo: SUBGROUPS.find((x) => x.id === s)?.label ?? s }));

  const mudarGrupo = (g: 'A' | 'B') => {
    setGrupo(g);
    let f = { ...form };
    if (f.subgrupo && !f.subgrupo.toUpperCase().startsWith(g)) f.subgrupo = '';
    const modOk = g === 'A' ? ['verde', 'azul', 'optante_b'] : ['branca', 'convencional'];
    if (!modOk.includes(f.modalidadeAtual)) f = trocarModalidade(f, g === 'A' ? 'verde' : 'convencional');
    aoMudar(f);
  };

  const cartao = (m: { id: TariffModalidade; titulo: string; desc: string }, grande: boolean) => {
    const ativo = mod === m.id;
    return (
      <button
        key={m.id}
        type="button"
        aria-pressed={ativo}
        onClick={() => aoMudar(trocarModalidade(form, m.id))}
        className={`text-left rounded-xl border px-4 cursor-pointer transition min-w-0 bg-white ${grande ? 'py-3.5' : 'py-2.5'} ${
          ativo ? 'border-tinta ring-2 ring-tinta' : 'border-borda hover:border-texto2'
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

  return (
    <Cartao>
      <TituloSecao titulo="Sua unidade consumidora" sub="Enquadramento tarifário. Com isso o sistema busca as tarifas certas na base da ANEEL." />
      <div className="space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <Rotulo htmlFor="inp-distribuidora" obrigatorio>
              Distribuidora
            </Rotulo>
            <CampoSelecao
              id="inp-distribuidora"
              valor={form.distribuidora}
              aoMudar={(v) => set('distribuidora', v)}
              opcoes={(distribuidorasApi ?? DISTRIBUIDORAS_APOIO).map((s) => ({ valor: s, rotulo: s }))}
              vazio="Selecione…"
            />
            <Dica>Lista da ANEEL.</Dica>
          </div>
          <div>
            <Rotulo htmlFor="inp-grupo" obrigatorio>
              Grupo
            </Rotulo>
            <CampoSelecao
              id="inp-grupo"
              valor={grupo}
              aoMudar={(v) => mudarGrupo(v as 'A' | 'B')}
              opcoes={[
                { valor: 'A', rotulo: 'A · média/alta tensão' },
                { valor: 'B', rotulo: 'B · baixa tensão' },
              ]}
            />
            <Dica>Na fatura, junto da classificação.</Dica>
          </div>
          <div>
            <Rotulo htmlFor="inp-subgrupo" obrigatorio>
              Subgrupo
            </Rotulo>
            <CampoSelecao id="inp-subgrupo" valor={form.subgrupo} aoMudar={(v) => set('subgrupo', v)} opcoes={subgrupos} vazio="Selecione…" />
            <Dica>{grupo === 'A' ? 'A1 a AS, com a tensão.' : 'B1 a B4, com a classe.'}</Dica>
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
          <Rotulo>
            Modalidade faturada na conta<span className="text-alerta ml-0.5">*</span>
          </Rotulo>
          {grupo === 'A' ? (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">{PRINCIPAIS_A.map((m) => cartao(m, true))}</div>
              <div className="text-sm text-texto2 mt-4 mb-2">Outras modalidades</div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">{OUTRAS_A.map((m) => cartao(m, false))}</div>
            </>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">{MODALIDADES_B.map((m) => cartao(m, true))}</div>
          )}
          {pend
            .filter((p) => p.includes('exige subgrupo') || p.includes('exigem subgrupo'))
            .map((p) => (
              <p key={p} className="text-sm text-alerta mt-2">
                {p}
              </p>
            ))}
        </div>

        {optante ? (
          <div className="space-y-4 border-t border-borda2 pt-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Rotulo htmlFor="inp-kva" obrigatorio>
                  Potência dos transformadores
                </Rotulo>
                <CampoNumero id="inp-kva" valor={form.potenciaTransformadoresKva} aoMudar={(v) => set('potenciaTransformadoresKva', v)} unidade="kVA" invalido={falta('Optante B')} />
                <Dica>Obrigatório no Optante B: até 112,5 kVA (ou 1.125 kVA em cooperativa de eletrificação rural), art. 292.</Dica>
              </div>
              <div>
                <Rotulo htmlFor="inp-atividade">Atividade</Rotulo>
                <CampoSelecao
                  id="inp-atividade"
                  valor={form.atividade}
                  aoMudar={(v) => set('atividade', v as InvoiceFormData['atividade'])}
                  opcoes={['Comercial ou Industrial', 'Rural', 'Residencial', 'Esportivo ou Parque Agropecuário'].map((x) => ({ valor: x, rotulo: x }))}
                />
                <Dica>Define a tarifa do Grupo B: Residencial → B1; Rural → B2; demais → B3.</Dica>
              </div>
            </div>
            <details>
              <summary className="text-sm font-semibold cursor-pointer">Outros critérios do art. 292 e custo de disponibilidade</summary>
              <div className="mt-3 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
                    <CampoNumero id="inp-cargaRefletoresKw" valor={form.cargaRefletoresKw || null} aoMudar={(v) => set('cargaRefletoresKw', v ?? 0)} unidade="kW" />
                  </div>
                  <div>
                    <Rotulo htmlFor="inp-cargaInstaladaTotalKw">Carga instalada total</Rotulo>
                    <CampoNumero id="inp-cargaInstaladaTotalKw" valor={form.cargaInstaladaTotalKw || null} aoMudar={(v) => set('cargaInstaladaTotalKw', v ?? 0)} unidade="kW" />
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <Marcador id="inp-coop" marcado={form.cooperativaEletrificacaoRural} aoMudar={(v) => set('cooperativaEletrificacaoRural', v)} rotulo="Cooperativa de eletrificação rural (≤ 1.125 kVA)" />
                  <Marcador id="inp-hotel" marcado={form.hotelariaTurismo} aoMudar={(v) => set('hotelariaTurismo', v)} rotulo="Hotelaria/pousada em área de veraneio ou turismo" />
                  <Marcador id="inp-prepag" marcado={form.prePagamento} aoMudar={(v) => set('prePagamento', v)} rotulo="Pré-pagamento (exceção do custo de disponibilidade)" />
                </div>
                <Dica>
                  Faturamento: tarifa Convencional do subgrupo B derivado da atividade; monômia sem demanda/ultrapassagem;
                  custo de disponibilidade (30/50/100 kWh) quando o consumo for menor.
                </Dica>
              </div>
            </details>
          </div>
        ) : grupo === 'B' ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 border-t border-borda2 pt-4">
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
        ) : null}
      </div>
    </Cartao>
  );
};

/* ------------------------------------------------------------------ */
/* Passo 2 — Demanda e consumo                                         */
/* ------------------------------------------------------------------ */

const PassoDemanda: React.FC<{ form: InvoiceFormData; aoMudar: (f: InvoiceFormData) => void }> = ({ form, aoMudar }) => {
  const set = <K extends keyof InvoiceFormData>(c: K, v: InvoiceFormData[K]) => aoMudar({ ...form, [c]: v });
  const set0 = (c: keyof InvoiceFormData) => (v: number | null) => aoMudar({ ...form, [c]: v ?? 0 });
  const pend = validarFormulario(form);
  const falta = (t: string) => pend.some((p) => p.startsWith(t));
  const mod = form.modalidadeAtual;
  const grupoA = ehGrupoA(form);
  const temReativo =
    form.consumoReativoPonta + form.consumoReativoForaPonta + form.demandaReativaPonta + form.demandaReativaForaPonta +
      form.reativoEnergiaCapacitiva + form.reativoDemandaCapacitiva > 0;
  const [reatAberta, setReatAberta] = React.useState(temReativo);
  const consumoTotal = num(form.consumoPonta) + num(form.consumoForaPonta) + num(form.consumoIntermediario);

  const linhaPosto = (
    rotulo: string,
    contrCampo: 'demandaContratada' | 'demandaContratadaPontaKw' | 'demandaContratadaForaPontaKw',
    medCampo: 'demandaMedida' | 'demandaPontaKw' | 'demandaForaPontaKw',
    obrig: boolean,
    pendC: string,
    pendM: string,
  ) => (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div>
        <Rotulo htmlFor={`inp-${contrCampo}`} obrigatorio={obrig}>
          Demanda contratada {rotulo}
        </Rotulo>
        <CampoNumero id={`inp-${contrCampo}`} valor={form[contrCampo]} aoMudar={(v) => set(contrCampo, v)} unidade="kW" invalido={falta(pendC)} />
        <Dica>Quadro do contrato, na 1ª página.{mod === 'verde' ? ' Mínimo 30 kW.' : ''}</Dica>
      </div>
      <div>
        <Rotulo htmlFor={`inp-${medCampo}`} obrigatorio={obrig}>
          Demanda medida {rotulo}
        </Rotulo>
        <CampoNumero id={`inp-${medCampo}`} valor={form[medCampo]} aoMudar={(v) => set(medCampo, v)} unidade="kW" invalido={falta(pendM)} />
      </div>
      <Calculado
        rotulo={`Faturável ${rotulo}`}
        valor={form[contrCampo] === null && form[medCampo] === null ? '—' : `${numero(Math.max(num(form[medCampo]), num(form[contrCampo])), 2)} kW`}
        dica="maior entre medida e contratada"
      />
    </div>
  );

  return (
    <Cartao>
      <TituloSecao
        titulo="Demanda e consumo"
        sub={
          <>
            Valores do mês da fatura, coluna <strong>“Faturado”</strong>. A demanda contratada e a medida ficam juntas:
            delas sai a demanda faturável e a ultrapassagem.
          </>
        }
      />
      <div className="space-y-5">
        <h3 className="font-bold">Demanda do mês</h3>
        {mod === 'verde' ? (
          linhaPosto('única', 'demandaContratada', 'demandaMedida', true, 'Demanda contratada', 'Demanda medida única')
        ) : mod === 'azul' ? (
          <div className="space-y-4">
            {linhaPosto('ponta', 'demandaContratadaPontaKw', 'demandaPontaKw', true, 'Demanda contratada ponta', 'Demanda medida ponta')}
            {linhaPosto('fora ponta', 'demandaContratadaForaPontaKw', 'demandaForaPontaKw', true, 'Demanda contratada fora', 'Demanda medida fora')}
          </div>
        ) : mod === 'optante_b' ? (
          <div className="space-y-3">
            <Aviso tom="info">
              A fatura do Optante B não cobra demanda. <strong>Verde e Azul só são calculadas se você informar a demanda
              medida e a contratada</strong>; sem elas, aparecem como “não avaliado” na comparação.
            </Aviso>
            {linhaPosto('única (opcional)', 'demandaContratada', 'demandaMedida', false, '—', '—')}
          </div>
        ) : (
          <Aviso tom="info">
            Sem faturamento de demanda nesta modalidade — Convencional Monômia e Branca faturam energia (e custo de
            disponibilidade) sem cobrança de demanda.
          </Aviso>
        )}

        {mod === 'verde' || mod === 'azul' ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-start">
            <Marcador
              id="inp-demandaIsentaIcmsAtiva"
              marcado={form.demandaIsentaIcmsAtiva}
              aoMudar={(v) => set('demandaIsentaIcmsAtiva', v)}
              rotulo="Demanda contratada e não utilizada sem ICMS"
              dica="A fatura separa “Demanda isenta de ICMS”. Ligado: a API divide a demanda."
            />
            {form.demandaIsentaIcmsAtiva ? (
              <div>
                <Rotulo htmlFor="inp-demandaIsentaIcms">Demanda isenta de ICMS</Rotulo>
                <CampoNumero
                  id="inp-demandaIsentaIcms"
                  valor={form.demandaIsentaIcms > 0 ? form.demandaIsentaIcms : null}
                  aoMudar={set0('demandaIsentaIcms')}
                  unidade="kW"
                  placeholder="vazio = faturada − medida"
                />
                <Dica>Opcional. Vazio: a API calcula faturada − medida.</Dica>
              </div>
            ) : null}
          </div>
        ) : null}

        <div className="border-t border-borda2 pt-5 space-y-4">
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
            {mod === 'branca' ? (
              <div>
                <Rotulo htmlFor="inp-consumoIntermediario" obrigatorio>
                  Consumo intermediário
                </Rotulo>
                <CampoNumero id="inp-consumoIntermediario" valor={form.consumoIntermediario} aoMudar={(v) => set('consumoIntermediario', v)} unidade="kWh" invalido={falta('Consumo intermediário')} />
              </div>
            ) : null}
            <Calculado rotulo="Consumo total" valor={`${numero(consumoTotal)} kWh`} />
          </div>
        </div>

        <Sanfona
          id="san-reativos"
          letra="R"
          titulo="Reativos excedentes"
          resumo={`Opcional · art. 304 da REN 1.000/2021 · ${temReativo ? 'informados' : 'não informados'}`}
          aberta={reatAberta}
          aoAlternar={() => setReatAberta(!reatAberta)}
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
            ).map(([c, r, u]) => (
              <div key={c}>
                <Rotulo htmlFor={`inp-${c}`}>{r}</Rotulo>
                <CampoNumero id={`inp-${c}`} valor={form[c] || null} aoMudar={set0(c)} unidade={u} placeholder="0" />
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
          <Dica>Pelo art. 304, só há excedente com fator de potência abaixo de 0,92: valores pequenos podem não gerar cobrança.</Dica>
        </Sanfona>
      </div>
    </Cartao>
  );
};

/* ------------------------------------------------------------------ */
/* Passo 3 — Tarifas e tributos                                        */
/* ------------------------------------------------------------------ */

const PassoTarifas: React.FC<Props> = ({ form, aoMudar, bandeirasApi, bandeiraAtivaApi, bandeiraCompetencia }) => {
  const set = <K extends keyof InvoiceFormData>(c: K, v: InvoiceFormData[K]) => aoMudar({ ...form, [c]: v });
  const set0 = (c: keyof InvoiceFormData) => (v: number | null) => aoMudar({ ...form, [c]: v ?? 0 });
  const pend = validarFormulario(form);
  const falta = (t: string) => pend.some((p) => p.startsWith(t));
  const opcoes =
    bandeirasApi && bandeirasApi.length
      ? bandeirasApi.map((b) => ({ id: bandeiraApiParaForm(b.bandeira), rotulo: b.bandeira, kwh: b.valor_kwh }))
      : [];
  const compTxt = bandeiraCompetencia ? `${bandeiraCompetencia.slice(5, 7)}/${bandeiraCompetencia.slice(0, 4)}` : null;
  const [conferirAberta, setConferirAberta] = React.useState(form.totalFatura !== null || form.retencoesCreditos !== null);
  const [outrosAberta, setOutrosAberta] = React.useState(form.outrosValores > 0 || form.percentualConsumoMesAnterior > 0 || form.cipCosip > 0);

  return (
    <Cartao>
      <TituloSecao titulo="Tarifas e tributos" sub="Bandeira, tributos e outros valores da fatura. As tarifas vêm da base da ANEEL." />
      <div className="space-y-6">
        <div className="space-y-3">
          <h3 className="font-bold">Bandeira tarifária</h3>
          <Segmentos
            rotuloAria="Bandeira"
            valor={form.bandeiraAutomatica ? 'auto' : 'manual'}
            aoMudar={(v) => aoMudar({ ...form, bandeiraAutomatica: v === 'auto', bandeira: v === 'auto' ? 'verde' : form.bandeira })}
            opcoes={[
              { valor: 'auto', rotulo: 'Automática' },
              { valor: 'manual', rotulo: 'Manual (R$/kWh)' },
            ]}
          />
          {form.bandeiraAutomatica ? (
            <p className="text-sm text-texto2">
              {bandeiraAtivaApi && compTxt
                ? `Bandeira de ${compTxt} (mês da data de referência): ${bandeiraAtivaApi}. A API aplica a bandeira vigente na competência.`
                : 'A API aplica a bandeira vigente no mês da data de referência.'}
            </p>
          ) : (
            <div className="space-y-3">
              {opcoes.length ? (
                <div className="flex flex-wrap gap-2">
                  {opcoes.map((b) => (
                    <button
                      key={b.id}
                      type="button"
                      onClick={() => aoMudar({ ...form, bandeira: b.id, bandeiraManualRkwh: b.kwh })}
                      className={`rounded-xl border px-3 py-2 text-sm font-semibold cursor-pointer ${form.bandeiraManualRkwh === b.kwh ? 'border-tinta ring-2 ring-tinta' : 'border-borda'}`}
                    >
                      {b.rotulo} <span className="num text-xs text-texto2">{numero(b.kwh, 5)}</span>
                    </button>
                  ))}
                </div>
              ) : null}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Rotulo htmlFor="inp-bandeiraManual" obrigatorio>
                    Valor da bandeira
                  </Rotulo>
                  <CampoNumero id="inp-bandeiraManual" valor={form.bandeiraManualRkwh} aoMudar={(v) => set('bandeiraManualRkwh', v)} unidade="R$/kWh" invalido={falta('Valor da bandeira')} />
                  <Dica>
                    Para bandeira proporcional aos dias, como imprime a fatura (ex.: amarela de 22/11 a 30/11: 0,01885 × 9/32 =
                    0,0053016).
                  </Dica>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="space-y-4 border-t border-borda2 pt-5">
          <h3 className="font-bold">Tributos</h3>
          <Marcador id="inp-aplicarTributos" marcado={form.aplicarTributos} aoMudar={(v) => set('aplicarTributos', v)} rotulo="Aplicar PIS/COFINS/ICMS" dica="Desligue para ver os valores líquidos, sem tributos." />
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
                  {form.tipoIcms === 'fora' ? 'preço = tarifa ÷ [(1 − PIS − COFINS) × (1 − ICMS)]' : 'preço = tarifa ÷ (1 − PIS − COFINS − ICMS)'}
                </p>
                <Dica>
                  {form.tipoIcms === 'fora' ? 'Multiplicativa (reproduz a fatura Copel validada).' : 'Aditiva (forma da fonte oficial).'} Na parcela de
                  demanda isenta: preço = tarifa ÷ (1 − PIS − COFINS).
                </Dica>
              </div>
              <Marcador
                id="inp-tributarReativos"
                marcado={form.tributarReativos}
                aoMudar={(v) => set('tributarReativos', v)}
                rotulo="Tributar o reativo excedente (PIS/COFINS/ICMS)"
                dica="Como nas faturas CEMIG e Equatorial."
              />
              <Marcador id="inp-arredondar" marcado={form.arredondarCentavos} aoMudar={(v) => set('arredondarCentavos', v)} rotulo="Arredondar linhas a centavos" dica="Como a fatura impressa." />
            </>
          ) : null}
        </div>

        <Sanfona
          id="san-outros"
          letra="+"
          titulo="CIP e outros valores"
          resumo={`Opcional · CIP R$ ${numero(form.cipCosip, 2)} · outros R$ ${numero(form.outrosValores, 2)}`}
          aberta={outrosAberta}
          aoAlternar={() => setOutrosAberta(!outrosAberta)}
        >
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <Rotulo htmlFor="inp-cipCosip">CIP/COSIP (iluminação pública)</Rotulo>
              <CampoNumero id="inp-cipCosip" valor={form.cipCosip || null} aoMudar={set0('cipCosip')} unidade="R$" placeholder="0,00" />
            </div>
            <div>
              <Rotulo htmlFor="inp-outrosValores">Outros valores</Rotulo>
              <CampoNumero id="inp-outrosValores" valor={form.outrosValores || null} aoMudar={set0('outrosValores')} unidade="R$" placeholder="0,00" />
              <Dica>Multas, juros e serviços cobrados na fatura.</Dica>
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
              <Dica>Quando a leitura pega parte do mês anterior.</Dica>
            </div>
          </div>
          <Dica>CIP e outros valores ficam fora do custo técnico (D4): somam no total, não entram nas comparações.</Dica>
        </Sanfona>

        <Sanfona
          id="san-conferir"
          letra="✓"
          titulo="Conferir com a conta"
          resumo={form.totalFatura !== null ? `Total R$ ${numero(form.totalFatura, 2)}${form.retencoesCreditos ? ` · retenções R$ ${numero(form.retencoesCreditos, 2)}` : ''}` : 'Opcional · compara o recálculo com o total impresso'}
          aberta={conferirAberta}
          aoAlternar={() => setConferirAberta(!conferirAberta)}
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <Rotulo htmlFor="inp-totalFatura">Total a pagar impresso na fatura</Rotulo>
              <CampoNumero id="inp-totalFatura" valor={form.totalFatura} aoMudar={(v) => set('totalFatura', v)} unidade="R$" />
            </div>
            <div>
              <Rotulo htmlFor="inp-retencoes">Retenções e créditos na fatura</Rotulo>
              <CampoNumero id="inp-retencoes" valor={form.retencoesCreditos} aoMudar={(v) => set('retencoesCreditos', v)} unidade="R$" />
              <Dica>
                Opcional, só para conferência (ex.: IRPJ, CSLL, PIS e COFINS retidos de órgão público). Retenção não é
                desconto: não reduz o custo da unidade nem entra em nenhum outro número.
              </Dica>
            </div>
          </div>
        </Sanfona>
      </div>
    </Cartao>
  );
};

/* ------------------------------------------------------------------ */
/* Passo 4 — Histórico                                                 */
/* ------------------------------------------------------------------ */

const PassoHistorico: React.FC<{ form: InvoiceFormData; aoMudar: (f: InvoiceFormData) => void }> = ({ form, aoMudar }) => {
  const set = <K extends keyof InvoiceFormData>(c: K, v: InvoiceFormData[K]) => aoMudar({ ...form, [c]: v });
  const [modo, setModo] = React.useState<'colar' | 'digitar' | 'csv'>('colar');
  const hist = lerHistorico(form.historico12);
  const verdeAzul = form.modalidadeAtual === 'verde' || form.modalidadeAtual === 'azul';
  const plano = verdeAzul ? montarMesesPlanejamento(form) : { meses: [], avisos: [], periodo: '' };
  const foraPadrao = mesesForaDoPadrao(hist.meses);

  const [linhas, setLinhasLocal] = React.useState<LinhaTabela[]>(() => linhasDeMeses(hist.meses));
  const textoTabela = React.useRef(form.historico12);
  React.useEffect(() => {
    if (form.historico12 !== textoTabela.current) {
      textoTabela.current = form.historico12;
      setLinhasLocal(linhasDeMeses(lerHistorico(form.historico12).meses));
    }
  }, [form.historico12]);
  const setLinhas = (ls: LinhaTabela[]) => {
    const t = textoDeLinhas(ls);
    textoTabela.current = t;
    setLinhasLocal(ls);
    set('historico12', t);
  };
  const adicionarMes = () => {
    const ultimo = linhas[linhas.length - 1]?.mes;
    const [mm, aaaa] = ultimo ? ultimo.split('/').map(Number) : [0, 0];
    const d = ultimo ? new Date(aaaa, mm, 1) : new Date();
    setLinhas([...linhas, { mes: `${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`, dPonta: '', dFora: '', ePonta: '', eFora: '' }]);
  };
  const baixarModelo = () => {
    const blob = new Blob([modeloCsv(dataReferenciaIso(form.dataReferencia))], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'historico_12_meses_modelo.csv';
    a.click();
    URL.revokeObjectURL(url);
  };
  const lerCsv = async (arq: File | undefined) => {
    if (arq) set('historico12', textoDeCsv(await arq.text()));
  };
  const consumoPeriodo = hist.meses.reduce((a, m) => a + m.e_ponta_kwh + m.e_fora_ponta_kwh, 0);
  const maiorDemanda = hist.meses.reduce((a, m) => Math.max(a, m.d_med_unica ?? 0, m.d_med_ponta ?? 0, m.d_med_fora_ponta ?? 0), 0);

  return (
    <Cartao>
      <TituloSecao
        titulo={
          <span className="inline-flex items-center gap-2">
            Histórico de 12 meses <span className="text-xs font-semibold bg-fundo rounded-md px-2 py-0.5">opcional</span>
          </span>
        }
        sub="Usado só no planejamento anual. Sem histórico, o planejamento usa só o mês da fatura e o resultado sai como indicativo. Mês que faltar não vira zero."
      />
      {!verdeAzul ? (
        <Aviso tom="info">O planejamento anual vale para unidades Verde ou Azul; nesta modalidade o histórico não é usado.</Aviso>
      ) : null}
      <div className="space-y-4 mt-2">
        <Segmentos
          rotuloAria="Como informar o histórico"
          valor={modo}
          aoMudar={setModo}
          opcoes={[
            { valor: 'colar', rotulo: 'Colar' },
            { valor: 'digitar', rotulo: 'Digitar mês a mês' },
            { valor: 'csv', rotulo: 'CSV' },
          ]}
        />
        {modo === 'colar' ? (
          <div>
            <Rotulo htmlFor="inp-historico12">Cole aqui o histórico</Rotulo>
            <textarea
              id="inp-historico12"
              rows={6}
              value={form.historico12}
              onChange={(e) => set('historico12', e.target.value)}
              className="w-full rounded-xl border border-borda px-3.5 py-2.5 num text-sm outline-none focus:border-tinta focus:ring-2 focus:ring-acento/40"
              placeholder={'Por posto: MM/AAAA; demanda ponta; demanda fora ponta; consumo ponta; consumo fora ponta\n12/2023; 193; 200; 7.000; 54.950\nVerde (demanda única): MM/AAAA; demanda; consumo ponta; consumo fora ponta\n11/2023; 231; 8.750; 63.000'}
            />
            <Dica>Uma linha por mês, do quadro “Histórico de Consumo” da fatura (valores faturados).</Dica>
          </div>
        ) : null}
        {modo === 'csv' ? (
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
            <input type="file" accept=".csv,text/csv" aria-label="Arquivo CSV do histórico" className="mt-3 text-sm max-w-full" onChange={(e) => void lerCsv(e.target.files?.[0])} />
            <div>
              <button type="button" onClick={baixarModelo} className="mt-2 text-sm font-semibold underline cursor-pointer">
                Baixar planilha modelo
              </button>
            </div>
          </div>
        ) : null}

        {hist.meses.length > 0 && hist.erros.length === 0 ? (
          <p className="text-sm font-semibold text-verde">
            ✓ Reconhecemos {hist.meses.length} {hist.meses.length === 1 ? 'mês' : 'meses'}
            {plano.periodo ? ` (planejamento ${plano.periodo})` : ''}. Confira na tabela.
          </p>
        ) : null}
        {hist.erros.length > 0 ? (
          <ul className="text-sm text-alerta list-disc pl-5">
            {hist.erros.map((e) => (
              <li key={e}>{e}</li>
            ))}
          </ul>
        ) : null}

        {modo === 'digitar' || linhas.length > 0 ? (
          <>
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
                      const cel = (c: keyof LinhaTabela, r: string) => (
                        <td className="px-1.5 py-1">
                          <input
                            aria-label={`${r} ${l.mes}`}
                            value={l[c]}
                            placeholder={c === 'dPonta' ? '—' : ''}
                            onChange={(e) => setLinhas(linhas.map((x, j) => (j === i ? { ...x, [c]: e.target.value } : x)))}
                            className={`w-full h-9 rounded-lg border px-2 text-right num outline-none focus:border-tinta ${fora && (c === 'ePonta' || c === 'eFora') ? 'border-acento bg-acento/10' : 'border-borda'}`}
                          />
                        </td>
                      );
                      return (
                        <tr key={`${l.mes}-${i}`} className="border-t border-borda2">
                          <td className="px-3 py-1 font-semibold num">{/^\d{2}\/\d{4}$/.test(l.mes) ? rotuloMes(iso) : l.mes}</td>
                          {cel('dPonta', 'Demanda ponta')}
                          {cel('dFora', 'Demanda fora ponta')}
                          {cel('ePonta', 'Consumo ponta')}
                          {cel('eFora', 'Consumo fora ponta')}
                          <td className="pr-2">
                            <button type="button" aria-label={`Remover ${l.mes}`} className="text-texto2 hover:text-alerta cursor-pointer" onClick={() => setLinhas(linhas.filter((_, j) => j !== i))}>
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
              + Adicionar mês
            </button>
          </>
        ) : null}

        {hist.meses.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Calculado rotulo="Consumo total no período" valor={`${numero(consumoPeriodo)} kWh`} />
            <Calculado rotulo="Maior demanda medida" valor={fmtKw(maiorDemanda)} dica="no período" />
          </div>
        ) : null}
        {foraPadrao.length > 0 ? (
          <Aviso>
            Consumo longe da média do período (±25%):{' '}
            {foraPadrao.map((f) => `${rotuloMes(f.mes)} ${f.desvio < 0 ? '−' : '+'}${numero(Math.abs(f.desvio) * 100)}%`).join(' · ')}. Se
            estiver certo, pode seguir.
          </Aviso>
        ) : null}
        {plano.avisos.map((a) => (
          <Aviso key={a} tom="info">
            {a}
          </Aviso>
        ))}
      </div>
    </Cartao>
  );
};

/* ------------------------------------------------------------------ */
/* Passo 5 — Revisar e calcular                                        */
/* ------------------------------------------------------------------ */

const PassoRevisar: React.FC<Props & { aoEditar: (p: Passo) => void; pend: string[] }> = ({
  form,
  aoEditar,
  pendencias,
  pend,
  carregando,
  bandeiraAtivaApi,
}) => {
  const mod = form.modalidadeAtual;
  const hist = lerHistorico(form.historico12);
  const plano = mod === 'verde' || mod === 'azul' ? montarMesesPlanejamento(form) : { meses: [], avisos: [], periodo: '' };
  const temReativo =
    form.consumoReativoPonta + form.consumoReativoForaPonta + form.demandaReativaPonta + form.demandaReativaForaPonta +
      form.reativoEnergiaCapacitiva + form.reativoDemandaCapacitiva > 0;
  const consumoTotal = num(form.consumoPonta) + num(form.consumoForaPonta) + num(form.consumoIntermediario);
  const lista = pendencias.length ? pendencias : pend;
  const demandaTxt =
    mod === 'verde'
      ? `${fmtKw(form.demandaContratada)} contratada · ${fmtKw(form.demandaMedida)} medida`
      : mod === 'azul'
        ? `ponta ${fmtKw(form.demandaContratadaPontaKw)} / ${fmtKw(form.demandaPontaKw)} · fora ${fmtKw(form.demandaContratadaForaPontaKw)} / ${fmtKw(form.demandaForaPontaKw)}`
        : mod === 'optante_b' && form.demandaMedida !== null && form.demandaContratada !== null
          ? `${fmtKw(form.demandaContratada)} / ${fmtKw(form.demandaMedida)} (só para comparar)`
          : 'não se aplica';

  return (
    <Cartao>
      <TituloSecao titulo="Tudo certo?" sub="Confira o resumo. Toque em “Editar” para voltar a um passo." />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Resumo
          titulo="Unidade"
          aoEditar={() => aoEditar(1)}
          itens={[
            ['Distribuidora', [form.distribuidora || '—', form.subgrupo].filter(Boolean).join(' · ')],
            ['Data de referência', form.dataReferencia || '—'],
            ['Modalidade', TODAS.find((m) => m.id === mod)?.titulo ?? mod],
            ...(mod === 'optante_b'
              ? ([
                  ['Transformadores', form.potenciaTransformadoresKva === null ? 'não informado' : `${numero(form.potenciaTransformadoresKva, 1)} kVA`],
                  ['Atividade', form.atividade],
                ] as [string, string][])
              : []),
          ]}
        />
        <Resumo
          titulo="Demanda e consumo"
          aoEditar={() => aoEditar(2)}
          itens={[
            ['Demanda (contratada / medida)', demandaTxt],
            ['Consumo do mês', `${numero(consumoTotal)} kWh`],
            ['Demanda isenta de ICMS', mod === 'verde' || mod === 'azul' ? (form.demandaIsentaIcmsAtiva ? (form.demandaIsentaIcms > 0 ? fmtKw(form.demandaIsentaIcms) : 'faturada − medida') : 'desligada') : 'não se aplica'],
            ['Reativos', temReativo ? 'informados' : 'não informados'],
          ]}
        />
        <Resumo
          titulo="Tarifas e tributos"
          aoEditar={() => aoEditar(3)}
          itens={[
            ['Bandeira', form.bandeiraAutomatica ? `automática${bandeiraAtivaApi ? ` (${bandeiraAtivaApi})` : ''}` : form.bandeiraManualRkwh === null ? 'manual: valor não informado' : `manual: R$ ${numero(form.bandeiraManualRkwh, 7)}/kWh`],
            ['PIS + COFINS', form.aplicarTributos ? `${fmtPct(form.pis)} + ${fmtPct(form.cofins)}` : 'sem tributos'],
            ['ICMS', form.aplicarTributos ? `${fmtPct(form.icms)} · ${form.tipoIcms === 'fora' ? 'por fora' : 'por dentro'}` : 'sem tributos'],
            ['Tributar reativo', form.tributarReativos ? 'sim' : 'não'],
            ['CIP · outros', `R$ ${numero(form.cipCosip, 2)} · R$ ${numero(form.outrosValores, 2)}`],
            ['Conferência', form.totalFatura !== null ? `R$ ${numero(form.totalFatura, 2)}${form.retencoesCreditos ? ` (retenções R$ ${numero(form.retencoesCreditos, 2)})` : ''}` : 'sem conferência'],
          ]}
        />
        <Resumo
          titulo="Histórico"
          aoEditar={() => aoEditar(4)}
          itens={[
            ['Meses', hist.meses.length ? `${hist.meses.length}` : 'sem histórico (só o mês da fatura)'],
            ['Planejamento', plano.periodo || (mod === 'verde' || mod === 'azul' ? '—' : 'não se aplica')],
          ]}
        />
      </div>

      {lista.length > 0 ? (
        <div className="mt-5">
          <Aviso tom="erro">
            <strong>Preencha antes de calcular ({lista.length}):</strong>
            <ul className="list-disc pl-5 mt-1 space-y-0.5">
              {lista.map((p) => (
                <li key={p}>
                  {p}{' '}
                  <button type="button" className="underline text-xs cursor-pointer" onClick={() => aoEditar(passoDaPendencia(p))}>
                    ir ao passo {passoDaPendencia(p)}
                  </button>
                </li>
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
  );
};

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
