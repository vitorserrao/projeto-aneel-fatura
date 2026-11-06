/**
 * Etapa 2 — Fatura simulada (Fatura.dc.html). Abas por modalidade, papel de
 * fatura com as linhas da API, conferência com a fatura real e composição.
 */
import React from 'react';
import type { Analise, ModalidadeAnalise } from '../lib/analise';
import { Cenario, Composicao, FaturaModalidade, SELO_HIPOTETICO, composicaoDe, resumoTributos, textoContrato } from '../lib/cenarios';
import { nomeModalidade } from '../lib/rotulos';
import { COR, brl, corModalidade, numero, pct, tarifa } from '../lib/formato';
import { num } from '../lib/numeros';
import { dataReferenciaIso } from '../lib/api';
import { fatorCarga, mesesBase } from '../lib/series';
import { Aviso, Botao, Segmentos, Selo } from './ui';
import { BarraEmpilhada, GraficoBarras, Legenda } from './graficos';

const MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];

export const FATIAS_COMPOSICAO: { chave: keyof Composicao; nome: string; cor: string }[] = [
  { chave: 'TE', nome: 'Energia (TE)', cor: COR.te },
  { chave: 'Demanda', nome: 'Demanda (TUSD)', cor: COR.demanda },
  { chave: 'Fio', nome: 'Fio por kWh (TUSD)', cor: COR.fio },
  { chave: 'Tributos', nome: 'Tributos', cor: COR.tributos },
  { chave: 'Outros', nome: 'Outros (bandeira, reativos, CIP, outros)', cor: COR.outros },
];

const fmtQ = (q: number, unidade: string) => {
  if (unidade === '') return '—';
  const casas = unidade === 'MWh' || unidade === 'MVArh' ? 3 : 2;
  return numero(q, casas);
};

export const EtapaFatura: React.FC<{ analise: Analise; aoEditar: () => void; aoAvancar: () => void }> = ({
  analise,
  aoEditar,
  aoAvancar,
}) => {
  const [cenario, setCenario] = React.useState<Cenario>('atual');
  const disponiveis = analise.modalidades.filter((m) => m.estado === 'ok');
  const [sel, setSel] = React.useState<string>(analise.modalidadeAtual);
  const mod = analise.modalidades.find((m) => m.modalidade === sel) ?? disponiveis[0];
  const fatura: FaturaModalidade | null =
    !mod || mod.estado !== 'ok' ? null : cenario === 'otima' && mod.otima ? mod.otima : mod.atual;

  const form = analise.form;
  const iso = dataReferenciaIso(form.dataReferencia);
  const mesTxt = /^\d{4}-\d{2}/.test(iso) ? `${MESES[Number(iso.slice(5, 7)) - 1]}/${iso.slice(0, 4)}` : form.dataReferencia;
  const ehReal = !!fatura && fatura.modalidade === analise.modalidadeAtual && fatura.cenario === 'atual';

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-2xl sm:text-3xl font-bold">Fatura simulada</h1>
          <p className="text-sm text-texto2 mt-1">
            Como ficaria a sua fatura em cada modalidade
            {analise.planejamento ? ', com o contrato atual ou com a demanda contratada ideal' : ''}. Compare com a fatura
            real.
          </p>
        </div>
        <div className="flex gap-2 no-print">
          <Botao onClick={aoEditar}>Ajustar dados</Botao>
          <Botao variante="escuro" onClick={() => window.print()}>
            Baixar PDF
          </Botao>
        </div>
      </div>

      {analise.planejamento ? (
        <div className="flex flex-wrap items-center gap-3 no-print">
          <Segmentos
            rotuloAria="Cenário de demanda contratada"
            valor={cenario}
            aoMudar={setCenario}
            opcoes={[
              { valor: 'atual', rotulo: 'Contrato atual' },
              { valor: 'otima', rotulo: 'Demanda ideal (planejamento)' },
            ]}
          />
          {cenario === 'otima' ? (
            <span className="text-sm text-texto2">
              DC ótima do planejamento ({analise.mesesPlanejamento.length}{' '}
              {analise.mesesPlanejamento.length === 1 ? 'mês' : 'meses'}), aplicada a este mês.
            </span>
          ) : null}
        </div>
      ) : null}

      {/* Abas por modalidade */}
      <div role="tablist" aria-label="Modalidades" className="grid grid-cols-1 sm:grid-cols-3 gap-3 no-print">
        {analise.modalidades.map((m) => (
          <AbaModalidade key={m.modalidade} m={m} cenario={cenario} ativa={m.modalidade === mod?.modalidade} aoEscolher={() => setSel(m.modalidade)} />
        ))}
      </div>

      {analise.conferencia && ehReal ? <FaixaConferencia c={analise.conferencia} /> : null}

      {fatura ? (
        <PapelFatura analise={analise} fatura={fatura} mesTxt={mesTxt} hipotetica={mod!.hipotetica} />
      ) : (
        <Aviso tom="info">Nenhuma fatura disponível para esta modalidade.</Aviso>
      )}

      {fatura ? <ComposicaoFatura fatura={fatura} /> : null}

      {analise.notas.length > 0 ? (
        <div className="space-y-2">
          {analise.notas.map((n, i) => (
            <Aviso key={i} tom="info">
              <span className="num text-xs mr-2">{n.tipo}</span>
              {n.mensagem}
            </Aviso>
          ))}
        </div>
      ) : null}

      <div className="flex flex-wrap justify-between items-center gap-3 no-print">
        <p className="text-sm text-texto2">
          Tarifas da base ANEEL pela vigência do mês; valores calculados pela API.
        </p>
        <Botao variante="primario" onClick={aoAvancar}>
          Ver análise completa e E-PI →
        </Botao>
      </div>
    </div>
  );
};

const AbaModalidade: React.FC<{ m: ModalidadeAnalise; cenario: Cenario; ativa: boolean; aoEscolher: () => void }> = ({
  m,
  cenario,
  ativa,
  aoEscolher,
}) => {
  const cor = corModalidade(m.modalidade);
  if (m.estado !== 'ok') {
    return (
      <div className="listrado rounded-xl border border-dashed border-borda px-4 py-3 min-w-0" aria-disabled>
        <div className="flex justify-between gap-2">
          <span className="font-bold text-texto2">{nomeModalidade(m.modalidade)}</span>
          <span className="text-sm text-texto2">{m.estado === 'nao_avaliado' ? 'não avaliado' : 'indisponível'}</span>
        </div>
        <p className="text-xs text-texto2 mt-1 break-words">{m.motivo}</p>
      </div>
    );
  }
  const f = cenario === 'otima' && m.otima ? m.otima : m.atual!;
  const contrato = cenario === 'otima' && m.otima ? m.contratoOtimo : m.contratoAtual;
  return (
    <button
      type="button"
      role="tab"
      aria-selected={ativa}
      onClick={aoEscolher}
      className={`text-left rounded-xl border px-4 py-3 cursor-pointer transition min-w-0 ${ativa ? 'bg-white ring-2' : 'bg-white border-borda hover:border-texto2'}`}
      style={ativa ? { borderColor: cor, boxShadow: `0 0 0 2px ${cor}` } : undefined}
    >
      <div className="flex items-center gap-2 font-bold">
        <span className="w-2.5 h-2.5 rounded-full" style={{ background: cor }} />
        {nomeModalidade(m.modalidade)}
      </div>
      <div className="flex justify-between items-baseline gap-2 mt-1">
        <span className="text-sm text-texto2 num">{m.modalidade === 'Optante B' ? 'sem demanda' : textoContrato(contrato, (n) => numero(n, Number.isInteger(n) ? 0 : 2))}</span>
        <span className="num font-semibold text-lg">{brl(f.total)}</span>
      </div>
      {m.hipotetica ? (
        <Selo cor={COR.alerta} className="mt-1.5">
          {SELO_HIPOTETICO[m.modalidade]}
        </Selo>
      ) : null}
    </button>
  );
};

const FaixaConferencia: React.FC<{ c: NonNullable<Analise['conferencia']> }> = ({ c }) => {
  const ok = Math.abs(c.diferenca) <= 1;
  return (
    <div
      className={`rounded-xl border px-4 py-3 flex flex-wrap items-center gap-x-4 gap-y-1 ${ok ? 'border-verde/40 bg-verde/5' : 'border-alerta/40 bg-alerta/5'}`}
    >
      <strong>Conferência</strong>
      <span className="num text-sm">
        Fatura real {brl(c.totalFatura)} × recalculada {brl(c.totalCalculado)} · Δ {c.diferenca >= 0 ? '+' : '−'}
        {brl(Math.abs(c.diferenca))} ({pct(c.diferenca / c.totalFatura, 2)})
      </span>
      <span className="text-sm" style={{ color: ok ? COR.verde : COR.alerta }}>
        {ok ? 'confere (|Δ| ≤ R$ 1,00)' : 'diferença acima de R$ 1,00: confira os itens opcionais (reativos, outros, CIP)'}
      </span>
    </div>
  );
};

const PapelFatura: React.FC<{ analise: Analise; fatura: FaturaModalidade; mesTxt: string; hipotetica: boolean }> = ({
  analise,
  fatura,
  mesTxt,
  hipotetica,
}) => {
  const form = analise.form;
  const trib = resumoTributos(fatura.linhas, form);
  const contrato = fatura.contrato ?? analise.modalidades.find((m) => m.modalidade === fatura.modalidade)?.contratoAtual ?? null;
  const base = mesesBase(analise.mesesPlanejamento);
  const verde = analise.modalidadeAtual === 'Verde';
  const fcMes = (() => {
    const dMax = verde ? num(form.demandaMedida) : Math.max(num(form.demandaPontaKw), num(form.demandaForaPontaKw));
    const iso = dataReferenciaIso(form.dataReferencia);
    if (dMax <= 0 || !/^\d{4}-\d{2}/.test(iso)) return null;
    return fatorCarga({
      data: `${iso.slice(0, 7)}-15`,
      rotulo: '',
      ePontaKwh: num(form.consumoPonta),
      eForaKwh: num(form.consumoForaPonta),
      dVerde: dMax,
      dPonta: dMax,
      dFora: dMax,
      pontaInformada: false,
    });
  })();
  const cor = corModalidade(fatura.modalidade);

  return (
    <article className="relative bg-white border border-borda rounded-2xl shadow-sm overflow-hidden">
      <div className="p-5 sm:p-7">
        <div className="flex flex-wrap justify-between gap-4">
          <div className="min-w-0">
            <h2 className="text-2xl font-bold">{form.distribuidora}</h2>
            <p className="text-sm text-texto2">Fatura simulada de energia elétrica · {form.subgrupo.toUpperCase().startsWith('A') ? 'Grupo A' : 'Grupo B'}</p>
            <span className="inline-block mt-2 -rotate-2 border-2 border-alerta text-alerta rounded-md px-2 py-0.5 text-[11px] font-bold tracking-wider">
              SIMULAÇÃO · NÃO É DOCUMENTO DE COBRANÇA
            </span>
          </div>
          <div className="flex gap-3 flex-wrap">
            <div className="border border-borda rounded-xl px-4 py-3 min-w-[140px]">
              <div className="text-[11px] tracking-wider text-texto2 font-semibold">REFERENTE A</div>
              <div className="num text-lg font-semibold mt-1">{mesTxt}</div>
            </div>
            <div className="bg-tinta text-white rounded-xl px-4 py-3 min-w-[170px]">
              <div className="text-[11px] tracking-wider text-white/70 font-semibold">TOTAL A PAGAR</div>
              <div className="num text-2xl font-semibold mt-1 text-acento">{brl(fatura.total)}</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-5">
          <Info rotulo="Classificação" valor={`${form.subgrupo}${fatura.modalidade === 'Optante B' ? ` · ${form.atividade}` : ''}`} />
          <Info
            rotulo="Modalidade tarifária"
            valor={
              <span className="inline-flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ background: cor }} />
                {nomeModalidade(fatura.modalidade)}
                {hipotetica ? <Selo cor={COR.alerta}>hipotético</Selo> : null}
              </span>
            }
          />
          <Info
            rotulo="Demanda contratada"
            valor={fatura.modalidade === 'Optante B' ? 'não se aplica' : `${textoContrato(contrato, (n) => numero(n, 2))}${fatura.cenario === 'otima' ? ' (ideal)' : ''}`}
          />
        </div>

        <div className="mt-6">
          <div className="text-[11px] tracking-wider text-texto2 font-semibold mb-2">ITENS DA FATURA</div>
          <div className="overflow-x-auto -mx-5 sm:mx-0 px-5 sm:px-0">
            <table className="w-full text-sm min-w-[760px]">
              <thead>
                <tr className="border-y-2 border-tinta text-texto2 text-xs">
                  <th className="text-left py-2 pr-2 font-semibold">Descrição</th>
                  <th className="text-right px-2 font-semibold">Unid.</th>
                  <th className="text-right px-2 font-semibold">Quant.</th>
                  <th className="text-right px-2 font-semibold">Tarifa ANEEL</th>
                  <th className="text-right px-2 font-semibold">Preço c/ tributos</th>
                  <th className="text-right px-2 font-semibold">PIS/COFINS</th>
                  <th className="text-right px-2 font-semibold">ICMS</th>
                  <th className="text-right pl-2 font-semibold">Valor (R$)</th>
                </tr>
              </thead>
              <tbody>
                {fatura.linhas.map((l, i) => (
                  <tr key={l.descricao + i} className="border-b border-dashed border-borda2">
                    <td className="py-2 pr-2" title={l.descricao}>
                      {l.rotulo}
                    </td>
                    <td className="text-right px-2 text-texto2">{l.unidade || '—'}</td>
                    <td className="text-right px-2 num">{fmtQ(l.quantidade, l.unidade)}</td>
                    <td className="text-right px-2 num">{l.unidade === '' ? '—' : l.tarifaSem === null ? '—' : tarifa(l.tarifaSem)}</td>
                    <td className="text-right px-2 num">{l.unidade === '' ? '—' : tarifa(l.tarifaCom)}</td>
                    <td className="text-right px-2 num">{l.pisCofins > 0.005 ? numero(l.pisCofins, 2) : '—'}</td>
                    <td className="text-right px-2 num">{l.icms > 0.005 ? numero(l.icms, 2) : l.isentaIcms ? 'isento' : '—'}</td>
                    <td className="text-right pl-2 num font-semibold">{numero(l.valor, 2)}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-tinta">
                  <td className="py-3 font-bold" colSpan={7}>
                    Total
                  </td>
                  <td className="text-right pl-2 num font-bold text-base">{numero(fatura.total, 2)}</td>
                </tr>
              </tfoot>
            </table>
          </div>
          <p className="text-xs text-texto2 mt-2">
            Tarifa ANEEL sem tributos (R$/MWh, R$/kW) da mesma API com tributos desligados; tributo da linha = valor com −
            valor sem tributos.
          </p>
        </div>
      </div>

      <div className="border-t-2 border-dashed border-borda p-5 sm:p-7 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="border border-borda rounded-xl p-4 min-w-0">
          <div className="text-[11px] tracking-wider text-texto2 font-semibold mb-2">HISTÓRICO DE CONSUMO (MWH)</div>
          {base.length > 1 ? (
            <GraficoBarras
              titulo="Histórico de consumo"
              altura={220}
              mostrarValores={false}
              barras={base.map((m) => ({ rotulo: m.rotulo.slice(0, 3), valor: (m.ePontaKwh + m.eForaKwh) / 1000, cor: COR.texto2 }))}
              fmtY={(v) => numero(v, 0)}
            />
          ) : (
            <p className="text-sm text-texto2">Sem histórico informado.</p>
          )}
        </div>
        <div className="border border-borda rounded-xl p-4 min-w-0">
          <div className="text-[11px] tracking-wider text-texto2 font-semibold mb-2">GRANDEZAS MEDIDAS</div>
          <Linhas
            itens={[
              ...(verde
                ? [['Demanda medida', `${numero(num(form.demandaMedida), 2)} kW`]]
                : [
                    ['Demanda ponta', `${numero(num(form.demandaPontaKw), 2)} kW`],
                    ['Demanda fora ponta', `${numero(num(form.demandaForaPontaKw), 2)} kW`],
                  ]),
              ['Energia ponta', `${numero(num(form.consumoPonta))} kWh`],
              ['Energia fora ponta', `${numero(num(form.consumoForaPonta))} kWh`],
              ['Fator de carga', fcMes === null ? '—' : numero(fcMes, 2)],
            ]}
          />
        </div>
        <div className="border border-borda rounded-xl p-4 min-w-0">
          <div className="text-[11px] tracking-wider text-texto2 font-semibold mb-2">TRIBUTOS</div>
          {form.aplicarTributos ? (
            <Linhas
              itens={[
                ['Base de cálculo', brl(trib.base)],
                [`ICMS ${numero(num(form.icms), 2)}%`, brl(trib.icms)],
                [`PIS ${numero(num(form.pis), 2)}%`, brl(trib.pis)],
                [`COFINS ${numero(num(form.cofins), 2)}%`, brl(trib.cofins)],
              ]}
            />
          ) : (
            <p className="text-sm text-texto2">Tributos desligados: valores líquidos.</p>
          )}
        </div>
      </div>
    </article>
  );
};

const Info: React.FC<{ rotulo: string; valor: React.ReactNode }> = ({ rotulo, valor }) => (
  <div className="border border-borda rounded-xl px-4 py-3 min-w-0">
    <div className="text-[11px] tracking-wider text-texto2 font-semibold uppercase">{rotulo}</div>
    <div className="font-semibold mt-1 break-words">{valor}</div>
  </div>
);

const Linhas: React.FC<{ itens: string[][] }> = ({ itens }) => (
  <dl className="text-sm">
    {itens.map(([k, v]) => (
      <div key={k} className="flex justify-between gap-3 py-1">
        <dt className="text-texto2">{k}</dt>
        <dd className="num">{v}</dd>
      </div>
    ))}
  </dl>
);

const ComposicaoFatura: React.FC<{ fatura: FaturaModalidade }> = ({ fatura }) => {
  const c = composicaoDe(fatura.linhas);
  const fatias = FATIAS_COMPOSICAO.map((f) => ({ nome: f.nome, valor: c[f.chave], cor: f.cor }));
  return (
    <div className="bg-white border border-borda rounded-2xl p-5">
      <div className="flex flex-wrap justify-between items-baseline gap-2 mb-3">
        <h3 className="font-bold">Composição do custo desta fatura</h3>
        <span className="text-sm text-texto2">soma das linhas da API · sem tributos por componente + tributos</span>
      </div>
      <BarraEmpilhada fatias={fatias} titulo="Composição do custo" />
      <div className="mt-3">
        <Legenda itens={fatias.filter((f) => f.valor > 0.005).map((f) => ({ nome: `${f.nome} · ${brl(f.valor)}`, cor: f.cor }))} />
      </div>
    </div>
  );
};
