/**
 * Etapa 3 — Análise e E-PI (Analise.dc.html + relatório anterior).
 * Toda frase de leitura é montada a partir dos números da API.
 */
import React from 'react';
import { recomendacaoMes } from '../lib/analise';
import type { Analise } from '../lib/analise';
import type { InvoiceFormData } from '../types/energy';
import type { PlanejamentoApi } from '../lib/api';
import { Composicao, Contrato, composicaoDe, composicaoVazia, detalharLinhas, textoContrato } from '../lib/cenarios';
import {
  ModSerie,
  PontoCurva,
  ResultadoSeries,
  calcularCurva,
  faixaBoa,
  fatorCarga,
  media,
  mesesBase,
  mesesComUltrapassagem,
  pontosCurva,
  usoPontaHoras,
} from '../lib/series';
import { nomeModalidade } from '../lib/rotulos';
import { COR, brl, brlCurto, compacto, corModalidade, numero, pct } from '../lib/formato';
import { num } from '../lib/numeros';
import { Aviso, Botao, Cartao, CampoNumero, Dica, Kpi, Leitura, Progresso, Rotulo, Segmentos, Selo, TituloSecao } from './ui';
import { ComparacaoComposicao, GraficoBarras, GraficoCascata, GraficoCurva, GraficoEconomiaPreco, GraficoLinhas, Legenda } from './graficos';
import { FATIAS_COMPOSICAO } from './EtapaFatura';

interface Props {
  analise: Analise;
  series: ResultadoSeries | null;
  progressoSeries: { feitas: number; total: number } | null;
  cacheCurva: Map<string, number | null>;
  aoAtualizarAcl: (m: Partial<InvoiceFormData>) => void;
  aoVoltar: () => void;
}

const kw = (n: number) => `${numero(n, Number.isInteger(n) ? 0 : 2)} kW`;
const fmtContrato = (c: Contrato) => textoContrato(c, (n) => numero(n, Number.isInteger(n) ? 0 : 2));

type ModPlano = PlanejamentoApi['modalidades'][number];

export const EtapaAnalise: React.FC<Props> = ({ analise, series, progressoSeries, cacheCurva, aoAtualizarAcl, aoVoltar }) => {
  const plano = analise.planejamento;
  const form = analise.form;
  const n = analise.mesesPlanejamento.length;
  const base = mesesBase(analise.mesesPlanejamento);
  const periodoTxt = n >= 12 ? 'por ano' : `em ${n} ${n === 1 ? 'mês' : 'meses'}`;
  const rotuloPeriodo = n >= 12 ? analise.periodo : `parcial · ${n} ${n === 1 ? 'mês' : 'meses'}`;

  const modAtual = analise.modalidadeAtual as ModSerie;
  const pAtual = plano?.modalidades.find((m) => m.modalidade === modAtual) ?? null;
  const pMelhor = plano?.modalidades.find((m) => m.modalidade === plano.melhor_demanda_otimizada) ?? null;

  // E-PI: período (API /planejamento) e mês (API /epi/calcular).
  const epiMes = analise.epi.simplificado;
  const piPeriodo = pMelhor?.pi?.anual ?? null;
  const eTotalMwh = base.reduce((a, m) => a + (m.ePontaKwh + m.eForaKwh) / 1000, 0);
  // Base ACL por MWh vem da própria resposta da API (base_acl ÷ e_mwh).
  const baseAclPorMwh = epiMes && epiMes.e_mwh > 0 ? epiMes.base_acl / epiMes.e_mwh : null;
  const basePeriodo = baseAclPorMwh !== null && eTotalMwh > 0 ? baseAclPorMwh * eTotalMwh : null;
  const piReferencia = piPeriodo ?? epiMes?.pi ?? null;

  return (
    <div className="space-y-6">
      {plano && pAtual && pMelhor ? (
        <Diagnostico analise={analise} plano={plano} pAtual={pAtual} pMelhor={pMelhor} periodoTxt={periodoTxt} rotuloPeriodo={rotuloPeriodo} pi={piReferencia} />
      ) : (
        <DiagnosticoMes analise={analise} />
      )}

      {plano && pAtual && pMelhor ? (
        <Kpis plano={plano} pAtual={pAtual} pMelhor={pMelhor} base={base} n={n} eTotalMwh={eTotalMwh} />
      ) : null}

      {series ? (
        <CompararModalidades series={series} form={form} eTotalMwh={eTotalMwh} atual={analise.modalidadeAtual} />
      ) : null}

      {plano && pAtual && pMelhor ? (
        <Cascata
          plano={plano}
          pAtual={pAtual}
          pMelhor={pMelhor}
          periodoTxt={periodoTxt}
          proposta={form.precoMedioACL}
          piPeriodo={piReferencia}
          basePeriodo={basePeriodo}
        />
      ) : null}

      {plano && pAtual ? (
        <CurvaDemanda analise={analise} pAtual={pAtual} cache={cacheCurva} periodoTxt={periodoTxt} />
      ) : null}

      {plano ? (
        series ? (
          <>
            <MesAMes analise={analise} series={series} />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <PorQueVence analise={analise} series={series} plano={plano} />
              <DemandaMedida analise={analise} series={series} pAtual={pAtual} />
            </div>
          </>
        ) : progressoSeries ? (
          <Progresso
            feitas={progressoSeries.feitas}
            total={progressoSeries.total}
            rotulo="Calculando as faturas mês a mês na API (até 6 por vez)…"
          />
        ) : null
      ) : null}

      <MercadoLivre
        analise={analise}
        piPeriodo={piPeriodo}
        basePeriodo={basePeriodo}
        n={n}
        aoAtualizarAcl={aoAtualizarAcl}
      />

      <ConferenciaPremissas analise={analise} series={series} />

      <div className="flex justify-between no-print">
        <Botao onClick={aoVoltar}>← Fatura simulada</Botao>
        <Botao variante="escuro" onClick={() => window.print()}>
          Baixar PDF
        </Botao>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* 1. Diagnóstico                                                      */
/* ------------------------------------------------------------------ */

const Diagnostico: React.FC<{
  analise: Analise;
  plano: PlanejamentoApi;
  pAtual: ModPlano;
  pMelhor: ModPlano;
  periodoTxt: string;
  rotuloPeriodo: string;
  pi: number | null;
}> = ({ analise, plano, pAtual, pMelhor, periodoTxt, rotuloPeriodo, pi }) => {
  const g = plano.ganho;
  const atual = pAtual.modalidade;
  const melhor = pMelhor.modalidade;
  const troca = melhor !== atual && g.modalidade > 1;
  const dcAtual = pAtual.dc_atual;
  const dcOtima = pAtual.dc_otima;

  return (
    <section className="bg-tinta text-white rounded-2xl px-6 py-5">
      <div className="flex flex-wrap items-end gap-x-10 gap-y-5">
        <div className="min-w-0">
          <div className="tela-rotulo" style={{ color: COR.acento }}>
            Economia potencial · {analise.form.distribuidora} · {analise.form.subgrupo} · {rotuloPeriodo}
          </div>
          <div className="num tela-destaque mt-2" style={{ color: g.total > 1 ? COR.acento : '#FFFFFF' }}>
            {brlCurto(Math.max(g.total, 0))}
          </div>
          <div className="tela-apoio text-white/70">
            {g.total > 1 ? periodoTxt : 'a configuração atual já é a de menor custo'}
          </div>
        </div>
        <dl className="grid grid-cols-2 sm:grid-cols-3 gap-x-8 gap-y-4 min-w-0">
          <div>
            <dt className="tela-rotulo text-white/60">Demanda contratada</dt>
            <dd className="num tela-bloco mt-1">{fmtContrato(contratoDe(dcOtima))}</dd>
            <dd className="tela-apoio text-white/60">hoje {fmtContrato(contratoDe(dcAtual))}</dd>
          </div>
          <div>
            <dt className="tela-rotulo text-white/60">Modalidade</dt>
            <dd className="tela-bloco mt-1">
              {troca ? `${nomeModalidade(atual)} → ${nomeModalidade(melhor)}` : nomeModalidade(atual)}
            </dd>
            <dd className="tela-apoio text-white/60">
              {troca ? `${brl(g.modalidade, 0)} ${periodoTxt}` : 'menor custo do período'}
            </dd>
          </div>
          <div>
            <dt className="tela-rotulo text-white/60">E-PI · teto no ACL</dt>
            <dd className="num tela-bloco mt-1">{pi !== null && pi > 0 ? `${brl(pi, 0)}/MWh` : '—'}</dd>
            <dd className="tela-apoio text-white/60">
              {n12(analise) ? '12 meses' : `${analise.mesesPlanejamento.length} de 12 meses`}
            </dd>
          </div>
        </dl>
      </div>
    </section>
  );
};

const n12 = (a: Analise) => a.mesesPlanejamento.length >= 12;

function contratoDe(dc: number | [number, number] | null): Contrato {
  if (dc === null) return null;
  return Array.isArray(dc) ? { ponta: dc[0], fora: dc[1] } : { unica: dc };
}

/** Sem planejamento (Grupo B, Optante B ou erro): diagnóstico só do mês. */
const DiagnosticoMes: React.FC<{ analise: Analise }> = ({ analise }) => {
  // B10: a recomendação nunca custa mais do que a modalidade atual.
  const rec = recomendacaoMes(analise);
  const titulo = rec
    ? `Neste mês, a ${nomeModalidade(rec.modalidade)} sairia ${brl(rec.economia)} mais barata`
    : 'A modalidade atual já é a mais barata';
  const naoAvaliadas = analise.modalidades.filter((m) => m.estado === 'nao_avaliado').map((m) => nomeModalidade(m.modalidade));
  return (
    <section className="bg-tinta text-white rounded-2xl p-6 sm:p-8">
      <div className="text-acento text-xs font-bold tracking-widest uppercase">Diagnóstico · parcial · 1 mês</div>
      <h1 className="text-2xl sm:text-3xl font-bold mt-3">{titulo}</h1>
      <p className="text-white/80 mt-3 text-sm">
        {analise.planejamentoErro
          ? `O planejamento anual não pôde ser calculado: ${analise.planejamentoErro}`
          : 'O planejamento de demanda e a comparação mês a mês valem para unidades Verde ou Azul.'}
        {naoAvaliadas.length ? ` Não avaliadas: ${naoAvaliadas.join(', ')} (faltam dados; veja a etapa 2).` : ''}
      </p>
    </section>
  );
};

/* ------------------------------------------------------------------ */
/* 2. KPIs                                                             */
/* ------------------------------------------------------------------ */

const Kpis: React.FC<{ plano: PlanejamentoApi; pAtual: ModPlano; pMelhor: ModPlano; base: ReturnType<typeof mesesBase>; n: number; eTotalMwh: number }> = ({
  pAtual,
  pMelhor,
  base,
  n,
  eTotalMwh,
}) => {
  const rot = n >= 12 ? 'anual' : `${n} ${n === 1 ? 'mês' : 'meses'}`;
  const hoje = pAtual.custo_contrato_atual;
  const otim = pMelhor.custo_demanda_otimizada;
  const uso = media(base.map(usoPontaHoras));
  const ePonta = base.reduce((a, m) => a + m.ePontaKwh, 0) / 1000;
  const fc = media(base.map(fatorCarga));
  return (
    <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
      <Kpi
        rotulo="Custo hoje"
        valor={brlCurto(hoje)}
        sub={`${rot} · ${nomeModalidade(pAtual.modalidade)} ${fmtContrato(contratoDe(pAtual.dc_atual))}`}
      />
      <Kpi
        rotulo="Economia potencial"
        valor={brlCurto(Math.max(hoje - otim, 0))}
        cor={COR.verde}
        sub={hoje > 0 ? `${pct((otim - hoje) / hoje)} sobre o custo atual` : undefined}
      />
      <Kpi
        rotulo="Custo otimizado"
        valor={brlCurto(otim)}
        sub={`${rot} · ${nomeModalidade(pMelhor.modalidade)}`}
      />
      <Kpi
        rotulo="Custo médio"
        valor={eTotalMwh > 0 ? `${brl(otim / eTotalMwh, 0)}/MWh` : '—'}
        sub={eTotalMwh > 0 ? `hoje ${brl(hoje / eTotalMwh, 0)}/MWh` : undefined}
      />
      <Kpi
        rotulo="Fator de carga"
        valor={fc === null ? '—' : numero(fc, 2)}
        sub={
          uso === null
            ? 'sem demanda de ponta medida'
            : `ponta ${numero(uso, 0)} h/mês · ${pct(ePonta / Math.max(eTotalMwh, 0.001))} da energia`
        }
      />
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* 3. Cascata                                                          */
/* ------------------------------------------------------------------ */

const Cascata: React.FC<{
  plano: PlanejamentoApi;
  pAtual: ModPlano;
  pMelhor: ModPlano;
  periodoTxt: string;
  proposta: number;
  piPeriodo: number | null;
  basePeriodo: number | null;
}> = ({ plano, pAtual, pMelhor, periodoTxt, proposta, piPeriodo, basePeriodo }) => {
  const g = plano.ganho;
  const hoje = pAtual.custo_contrato_atual;
  const otim = pMelhor.custo_demanda_otimizada;
  const temAcl = proposta > 0 && piPeriodo !== null && basePeriodo !== null;
  const ganhoAcl = temAcl ? (piPeriodo! - proposta) * basePeriodo! : 0;
  const degraus = [
    { rotulo: 'Fatura hoje', sub: `${nomeModalidade(pAtual.modalidade).replace('Horária ', '')} ${fmtContrato(contratoDe(pAtual.dc_atual))}`, tipo: 'total' as const, valor: hoje, cor: COR.tinta },
    {
      rotulo: 'Ajustar demanda',
      sub: `${fmtContrato(contratoDe(pAtual.dc_atual))} → ${fmtContrato(contratoDe(pAtual.dc_otima))}`,
      tipo: 'delta' as const,
      valor: -g.demanda,
      cor: COR.verde,
    },
    {
      rotulo: 'Trocar modalidade',
      sub: g.modalidade > 1 ? `para ${nomeModalidade(pMelhor.modalidade)}` : 'não compensa',
      tipo: 'delta' as const,
      valor: -g.modalidade,
      cor: COR.azul,
    },
    { rotulo: 'Cativo otimizado', sub: `${nomeModalidade(pMelhor.modalidade).replace('Horária ', '')} ${fmtContrato(contratoDe(pMelhor.dc_otima))}`, tipo: 'total' as const, valor: otim, cor: COR.tinta },
    ...(temAcl
      ? [
          { rotulo: 'Migrar ao ACL', sub: `proposta ${brl(proposta, 0)}/MWh`, tipo: 'delta' as const, valor: -ganhoAcl, cor: COR.acl, tracejado: true },
          { rotulo: 'Potencial no livre', sub: 'estimativa', tipo: 'total' as const, valor: otim - ganhoAcl, cor: COR.acl, tracejado: true },
        ]
      : []),
  ];
  return (
    <Cartao>
      <TituloSecao
        titulo="De onde vem a economia"
        sub={`Do custo de hoje ao custo otimizado no cativo (${periodoTxt}).${temAcl ? ' As barras tracejadas dependem da proposta no livre.' : ''}`}
      />
      <Legenda
        itens={[
          { nome: 'Total', cor: COR.tinta },
          { nome: 'Ajuste de demanda', cor: COR.verde },
          { nome: 'Troca de modalidade', cor: COR.azul },
          ...(temAcl ? [{ nome: 'Mercado livre (estimativa)', cor: COR.acl, tracejada: true }] : []),
        ]}
      />
      <div className="mt-3">
        <GraficoCascata degraus={degraus} titulo="Cascata da economia" />
      </div>
      <Leitura>
        {g.demanda > 1
          ? `O ajuste de demanda vale ${brl(g.demanda, 0)} ${periodoTxt} e só depende de um pedido à distribuidora. `
          : 'A demanda contratada atual já é a de menor custo. '}
        {g.modalidade > 1
          ? `Trocar para a ${nomeModalidade(pMelhor.modalidade)} soma ${brl(g.modalidade, 0)}. `
          : `Trocar de modalidade não reduz o custo. `}
        {temAcl
          ? `O ganho no livre é uma estimativa para a proposta de ${brl(proposta, 2)}/MWh: (E-PI ${brl(piPeriodo!, 2)} − proposta) × energia-base do ACL.`
          : 'Informe uma proposta do mercado livre (etapa 1 ou seção E-PI abaixo) para ver a estimativa no livre.'}
      </Leitura>
    </Cartao>
  );
};

/* ------------------------------------------------------------------ */
/* 4. Qual demanda contratar? (sob demanda, com cache)                 */
/* ------------------------------------------------------------------ */

const CurvaDemanda: React.FC<{ analise: Analise; pAtual: ModPlano; cache: Map<string, number | null>; periodoTxt: string }> = ({
  analise,
  pAtual,
  cache,
  periodoTxt,
}) => {
  const [aberta, setAberta] = React.useState(false);
  const [pontos, setPontos] = React.useState<PontoCurva[] | null>(null);
  const [prog, setProg] = React.useState<{ feitas: number; total: number } | null>(null);
  const base = mesesBase(analise.mesesPlanejamento);
  const mod = pAtual.modalidade as ModSerie;
  const azul = mod === 'Azul';
  const dcOtima = Array.isArray(pAtual.dc_otima) ? pAtual.dc_otima[1] : pAtual.dc_otima;
  const pontaFixa = Array.isArray(pAtual.dc_otima) ? pAtual.dc_otima[0] : null;
  const dcAtual = Array.isArray(pAtual.dc_atual) ? pAtual.dc_atual[1] : pAtual.dc_atual;
  const dMax = Math.max(...base.map((m) => (azul ? m.dFora : m.dVerde)), 0);
  const semHistorico = base.length < 2;

  React.useEffect(() => {
    if (!aberta || pontos || semHistorico) return;
    let vivo = true;
    void calcularCurva(analise.form, base, mod, pontosCurva(dMax, dcOtima, dcAtual), pontaFixa, cache, (f, t) => vivo && setProg({ feitas: f, total: t })).then(
      (p) => vivo && setPontos(p),
    );
    return () => {
      vivo = false;
    };
  }, [aberta]); // eslint-disable-line react-hooks/exhaustive-deps

  const validos = (pontos ?? []).filter((p): p is { dc: number; custo: number } => p.custo !== null);
  const faixa = pontos ? faixaBoa(pontos) : null;
  const pOtimo = validos.find((p) => p.dc === Math.round(dcOtima));
  const pAtualC = dcAtual !== null ? validos.find((p) => p.dc === Math.round(dcAtual)) : undefined;

  return (
    <Cartao>
      <TituloSecao
        titulo="Qual demanda contratar?"
        sub={`Custo ${periodoTxt} na ${nomeModalidade(mod)} para cada valor de demanda contratada${azul ? ' fora de ponta (ponta fixa na ideal)' : ''}: soma das faturas mensais da API em 12 a 15 valores de DC.`}
        acao={
          !semHistorico ? (
            <Botao onClick={() => setAberta(!aberta)} aria-expanded={aberta} className="no-print">
              {aberta ? 'Recolher' : 'Calcular a curva'}
            </Botao>
          ) : null
        }
      />
      {semHistorico ? (
        <Aviso tom="info">
          A curva precisa de mais meses de histórico: com um só mês, a demanda ótima é indicativa e picos de outros meses
          não aparecem. Informe o histórico de 12 meses na etapa 1.
        </Aviso>
      ) : !aberta ? (
        <p className="text-sm text-texto2">
          Abre sob demanda: são {pontosCurva(dMax, dcOtima, dcAtual).length} valores × {base.length} meses de chamadas à API
          (guardadas em cache).
        </p>
      ) : !pontos ? (
        prog ? <Progresso feitas={prog.feitas} total={prog.total} rotulo="Calculando a curva na API…" /> : null
      ) : (
        <>
          <GraficoCurva
            titulo="Custo por demanda contratada"
            cor={corModalidade(mod)}
            pontos={validos.map((p) => ({ x: p.dc, y: p.custo }))}
            faixa={faixa}
            rotuloX={`Demanda contratada${azul ? ' fora de ponta' : ''} (kW)`}
            marcadores={[
              ...(pOtimo ? [{ x: pOtimo.dc, y: pOtimo.custo, rotulo: `ideal · ${kw(pOtimo.dc)} · ${compacto(pOtimo.custo)}`, cor: COR.verde }] : []),
              ...(pAtualC && pAtualC.dc !== pOtimo?.dc ? [{ x: pAtualC.dc, y: pAtualC.custo, rotulo: `hoje · ${kw(pAtualC.dc)} · ${compacto(pAtualC.custo)}`, cor: COR.tinta }] : []),
            ]}
          />
          {validos.length < (pontos?.length ?? 0) ? (
            <Aviso>Alguns valores de DC não puderam ser calculados pela API e ficaram fora da curva.</Aviso>
          ) : null}
          {faixa && pOtimo ? (
            <Leitura>
              Entre cerca de {kw(faixa[0])} e {kw(faixa[1])} o custo fica até 0,5% acima do menor valor (bordas
              interpoladas entre os pontos calculados): a margem de segurança é sua escolha. Na DC ideal do planejamento ({kw(dcOtima)}) a soma das faturas dá {brl(pOtimo.custo, 0)}
              {Math.abs(pOtimo.custo - pAtual.custo_demanda_otimizada) > 1
                ? ` (o planejamento informa ${brl(pAtual.custo_demanda_otimizada, 0)})`
                : ', igual ao planejamento'}
              .
            </Leitura>
          ) : null}
        </>
      )}
    </Cartao>
  );
};

/* ------------------------------------------------------------------ */
/* 5. Verde × Azul mês a mês                                           */
/* ------------------------------------------------------------------ */

const AvisosSeries: React.FC<{ series: ResultadoSeries }> = ({ series }) => {
  const ruins = series.conferencias.filter((c) => !c.ok);
  if (ruins.length === 0 && series.erros.length === 0) return null;
  return (
    <div className="space-y-2 mt-3">
      {ruins.map((c) => (
        <Aviso key={c.modalidade + c.cenario}>
          Soma das faturas mensais da {nomeModalidade(c.modalidade)} ({c.cenario === 'atual' ? 'contrato atual' : 'DC ótima'}) ={' '}
          {brl(c.soma)}; o planejamento informa {brl(c.planejamento)} (Δ {brl(c.diferenca)})
          {c.mesesFaltando ? ` · ${c.mesesFaltando} mês(es) sem resposta da API` : ''}.
        </Aviso>
      ))}
      {series.erros.map((e) => (
        <Aviso key={e} tom="erro">
          {e}
        </Aviso>
      ))}
    </div>
  );
};

const MesAMes: React.FC<{ analise: Analise; series: ResultadoSeries }> = ({ analise, series }) => {
  const [unid, setUnid] = React.useState<'rs' | 'mwh'>('rs');
  const [vista, setVista] = React.useState<'grafico' | 'tabela'>('grafico');
  const base = series.base;
  const eMwh = base.map((m) => (m.ePontaKwh + m.eForaKwh) / 1000);
  const verde = series.series.find((s) => s.modalidade === 'Verde');
  const azul = series.series.find((s) => s.modalidade === 'Azul');
  const porMwh = (v: (number | null)[]) => v.map((x, i) => (x === null || eMwh[i] <= 0 ? null : x / eMwh[i]));
  const linhas = series.series.map((s) => ({
    nome: s.modalidade,
    cor: corModalidade(s.modalidade),
    valores: unid === 'rs' ? s.otima : porMwh(s.otima),
  }));
  const comparaveis = verde && azul ? base.map((_, i) => (verde.otima[i] !== null && azul.otima[i] !== null ? [verde.otima[i]!, azul.otima[i]!] : null)) : [];
  const nVerde = comparaveis.filter((p) => p && p[0] < p[1]).length;
  const nComp = comparaveis.filter(Boolean).length;
  const hip = analise.modalidadeAtual === 'Verde' ? 'Azul' : analise.modalidadeAtual === 'Azul' ? 'Verde' : null;

  let leitura = '';
  if (nComp > 0) {
    if (nVerde === nComp) leitura = 'A Verde fica mais barata em todos os meses.';
    else if (nVerde === 0) leitura = 'A Azul fica mais barata em todos os meses.';
    else leitura = `A Verde fica mais barata em ${nVerde} de ${nComp} meses.`;
  }
  const rsMwh = verde ? porMwh(verde.otima) : [];
  const valid = rsMwh.filter((x): x is number => x !== null);
  if (valid.length > 1) {
    const iMax = rsMwh.indexOf(Math.max(...valid));
    leitura += ` O custo por MWh da Verde vai de ${brl(Math.min(...valid), 0)} a ${brl(Math.max(...valid), 0)} (maior em ${base[iMax].rotulo}).`;
  }

  return (
    <Cartao>
      <TituloSecao
        titulo="Verde × Azul mês a mês"
        sub="Com a demanda ideal de cada modalidade (faturas mensais da API)."
        acao={
          <div className="flex flex-wrap gap-2 no-print">
            <Segmentos rotuloAria="Unidade" valor={unid} aoMudar={setUnid} opcoes={[{ valor: 'rs', rotulo: 'Fatura (R$)' }, { valor: 'mwh', rotulo: 'Custo por MWh' }]} />
            <Segmentos rotuloAria="Vista" valor={vista} aoMudar={setVista} opcoes={[{ valor: 'grafico', rotulo: 'Gráfico' }, { valor: 'tabela', rotulo: 'Tabela' }]} />
          </div>
        }
      />
      <div className="flex flex-wrap items-center gap-3">
        <Legenda itens={series.series.map((s) => ({ nome: nomeModalidade(s.modalidade), cor: corModalidade(s.modalidade) }))} />
        {hip ? <Selo cor={COR.alerta}>{hip}: hipotético, a unidade não tem esse contrato</Selo> : null}
      </div>
      {vista === 'grafico' ? (
        <div className="mt-3">
          <GraficoLinhas
            titulo="Custo mensal por modalidade"
            rotulosX={base.map((m) => m.rotulo)}
            series={linhas}
            preencherEntre
            fmtY={unid === 'rs' ? compacto : (v) => numero(v, 0)}
          />
        </div>
      ) : (
        <div className="overflow-x-auto mt-3 rounded-xl border border-borda">
          <table className="w-full text-sm min-w-[640px]">
            <thead className="bg-fundo text-texto2">
              <tr>
                <th className="text-left px-3 py-2">Mês</th>
                <th className="text-right px-3">Energia (kWh)</th>
                <th className="text-right px-3">Verde (R$)</th>
                <th className="text-right px-3">Azul (R$)</th>
                <th className="text-right px-3">Azul − Verde</th>
                <th className="text-right px-3">Verde (R$/MWh)</th>
                <th className="text-right px-3">Uso ponta (h)</th>
              </tr>
            </thead>
            <tbody className="num">
              {base.map((m, i) => {
                const v = verde?.otima[i] ?? null;
                const a = azul?.otima[i] ?? null;
                const u = usoPontaHoras(m);
                return (
                  <tr key={m.data} className="border-t border-borda2">
                    <td className="px-3 py-2 font-semibold">{m.rotulo}</td>
                    <td className="text-right px-3">{numero(m.ePontaKwh + m.eForaKwh)}</td>
                    <td className="text-right px-3">{v === null ? '—' : numero(v, 0)}</td>
                    <td className="text-right px-3">{a === null ? '—' : numero(a, 0)}</td>
                    <td className="text-right px-3">{v === null || a === null ? '—' : `${a - v >= 0 ? '+' : '−'}${numero(Math.abs(a - v), 0)}`}</td>
                    <td className="text-right px-3">{v === null || eMwh[i] <= 0 ? '—' : numero(v / eMwh[i], 0)}</td>
                    <td className="text-right px-3">{u === null ? '—' : numero(u, 0)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
      {leitura ? <Leitura>{leitura}</Leitura> : null}
      <AvisosSeries series={series} />
    </Cartao>
  );
};

/* ------------------------------------------------------------------ */
/* 6. Por que a modalidade vence                                       */
/* ------------------------------------------------------------------ */

function composicaoAnual(series: ResultadoSeries, mod: ModSerie, form: InvoiceFormData): Composicao | null {
  const s = series.series.find((x) => x.modalidade === mod);
  if (!s) return null;
  const acc = composicaoVazia();
  for (let i = 0; i < series.base.length; i += 1) {
    const com = s.otimaFaturas[i];
    if (!com) return null;
    composicaoDe(detalharLinhas(com, s.otimaSem[i], form), acc);
  }
  return acc;
}

const PorQueVence: React.FC<{ analise: Analise; series: ResultadoSeries; plano: PlanejamentoApi }> = ({ analise, series, plano }) => {
  const base = series.base;
  const usos = base.map(usoPontaHoras);
  const uso = media(usos);
  const melhor = plano.melhor_demanda_otimizada;
  const cv = composicaoAnual(series, 'Verde', analise.form);
  const ca = composicaoAnual(series, 'Azul', analise.form);
  const linhaTe = cv && ca ? { v: cv.TE, a: ca.TE } : null;
  const tusd = cv && ca ? { v: cv.Demanda + cv.Fio, a: ca.Demanda + ca.Fio } : null;
  const teIgual = linhaTe ? Math.abs(linhaTe.v - linhaTe.a) <= 0.01 * Math.max(linhaTe.v, linhaTe.a) : false;

  return (
    <Cartao>
      <TituloSecao
        titulo={`Por que a ${nomeModalidade(melhor).replace('Horária ', '')} ganha`}
        nivel="h3"
        sub="Horas de uso da demanda na ponta em cada mês (energia na ponta ÷ demanda na ponta)."
      />
      {usos.some((u) => u !== null) ? (
        <GraficoBarras
          titulo="Uso da ponta por mês"
          altura={240}
          barras={base.map((m, i) => ({ rotulo: m.rotulo.slice(0, 3), valor: usos[i], cor: corModalidade(melhor) }))}
          fmtY={(v) => numero(v, 0)}
        />
      ) : (
        <Aviso tom="info">O histórico não traz demanda medida na ponta (só a demanda única): o uso da ponta não pode ser medido.</Aviso>
      )}
      {linhaTe && tusd ? (
        <div className="overflow-x-auto mt-4">
          <table className="w-full text-xs sm:text-sm">
            <thead className="text-texto2">
              <tr>
                <th className="text-left py-1">No período, com a DC ideal</th>
                <th className="text-right" style={{ color: COR.verde }}>
                  Verde
                </th>
                <th className="text-right" style={{ color: COR.azul }}>
                  Azul
                </th>
              </tr>
            </thead>
            <tbody className="num">
              <tr className="border-t border-borda2">
                <td className="py-1.5 font-sans">Energia (TE)</td>
                <td className="text-right">{brl(linhaTe.v, 0)}</td>
                <td className="text-right">{brl(linhaTe.a, 0)}</td>
              </tr>
              <tr className="border-t border-borda2">
                <td className="py-1.5 font-sans">Uso do sistema (TUSD: demanda + fio)</td>
                <td className="text-right">{brl(tusd.v, 0)}</td>
                <td className="text-right">{brl(tusd.a, 0)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      ) : null}
      <Leitura>
        {uso !== null ? `A unidade usa em média ${numero(uso, 0)} h/mês a demanda de ponta. ` : ''}
        {linhaTe && tusd
          ? teIgual
            ? `A TE é praticamente igual nas duas (${brl(linhaTe.v, 0)} × ${brl(linhaTe.a, 0)}); a diferença de ${brl(Math.abs(tusd.a - tusd.v), 0)} está na TUSD. `
            : `TE: ${brl(linhaTe.v, 0)} na Verde × ${brl(linhaTe.a, 0)} na Azul; TUSD: ${brl(tusd.v, 0)} × ${brl(tusd.a, 0)}. `
          : ''}
        {plano.equilibrio ? plano.equilibrio.mensagem : ''}
      </Leitura>
    </Cartao>
  );
};

/* ------------------------------------------------------------------ */
/* 7. Demanda medida × contratada                                      */
/* ------------------------------------------------------------------ */

const DemandaMedida: React.FC<{ analise: Analise; series: ResultadoSeries; pAtual: ModPlano | null }> = ({ series, pAtual }) => {
  if (!pAtual) return null;
  const mod = pAtual.modalidade as ModSerie;
  const azul = mod === 'Azul';
  const s = series.series.find((x) => x.modalidade === mod);
  if (!s) return null;
  const base = series.base;
  const ult = mesesComUltrapassagem(s.otimaFaturas);
  const dcAtual = Array.isArray(pAtual.dc_atual) ? pAtual.dc_atual[1] : pAtual.dc_atual;
  const dcOtima = Array.isArray(pAtual.dc_otima) ? pAtual.dc_otima[1] : pAtual.dc_otima;
  const meses = base.filter((_, i) => ult[i]).map((m) => m.rotulo);
  return (
    <Cartao>
      <TituloSecao
        titulo="Demanda medida × contratada"
        nivel="h3"
        sub={`Demanda medida no mês${azul ? ' fora de ponta' : ''} (kW). Faixa: tolerância de 5% acima da DC ideal.`}
      />
      <GraficoBarras
        titulo="Demanda medida por mês"
        altura={260}
        barras={base.map((m, i) => ({
          rotulo: m.rotulo.slice(0, 3),
          valor: azul ? m.dFora : m.dVerde,
          cor: ult[i] ? COR.alerta : '#5E7C93',
        }))}
        referencias={[
          ...(dcAtual !== null ? [{ valor: dcAtual, rotulo: `contratada hoje · ${kw(dcAtual)}`, cor: COR.tinta, tracejada: true }] : []),
          { valor: dcOtima, rotulo: `ideal · ${kw(dcOtima)}`, cor: COR.acl },
        ]}
        faixa={{ de: dcOtima, ate: dcOtima * 1.05, cor: COR.acento }}
        fmtY={(v) => numero(v, 0)}
      />
      <div className="mt-2">
        <Legenda
          itens={[
            { nome: 'dentro do limite', cor: '#5E7C93' },
            { nome: 'ultrapassagem cobrada (fatura da API)', cor: COR.alerta },
          ]}
        />
      </div>
      <Leitura>
        {meses.length === 0
          ? `Com ${kw(dcOtima)}, nenhum mês teve ultrapassagem cobrada.`
          : `Com ${kw(dcOtima)}, ${meses.join(' e ')} ${meses.length === 1 ? 'passa' : 'passam'} do limite e ${meses.length === 1 ? 'paga' : 'pagam'} ultrapassagem. Mesmo assim o período fecha ${brl(pAtual.custo_contrato_atual - pAtual.custo_demanda_otimizada, 0)} mais barato do que manter ${dcAtual !== null ? kw(dcAtual) : 'a DC atual'}.`}
      </Leitura>
    </Cartao>
  );
};

/* ------------------------------------------------------------------ */
/* 8. Para onde vai o dinheiro                                         */
/* ------------------------------------------------------------------ */

const CompararModalidades: React.FC<{
  series: ResultadoSeries;
  form: InvoiceFormData;
  eTotalMwh: number;
  atual: string;
}> = ({ series, form, eTotalMwh, atual }) => {
  const linhas = series.series.map((s) => ({
    s,
    c: composicaoAnual(series, s.modalidade, form),
    total: s.otima.reduce<number>((a, v) => a + (v ?? 0), 0),
  }));
  const validas = linhas.filter((l) => l.c !== null && l.total > 0);
  if (validas.length === 0) {
    return (
      <Cartao>
        <TituloSecao titulo="Comparação de modalidades" />
        <Aviso tom="info">Sem faturas mensais suficientes para comparar as modalidades no período.</Aviso>
      </Cartao>
    );
  }
  const menor = Math.min(...validas.map((l) => l.total));
  const totalAtual = linhas.find((l) => l.s.modalidade === atual)?.total ?? 0;
  const semComposicao = linhas.filter((l) => l.c === null).map((l) => nomeModalidade(l.s.modalidade));

  return (
    <Cartao>
      <TituloSecao
        titulo="Comparação de modalidades"
        sub="Período completo, com a demanda ideal de cada modalidade."
      />
      <div className="overflow-x-auto -mx-1 px-1">
        <table className="tela-tabela">
          <thead>
            <tr>
              <th>Modalidade</th>
              <th>Contrato</th>
              <th>Custo</th>
              <th>R$/MWh</th>
              <th>TE</th>
              <th>TUSD energia</th>
              <th>Demanda</th>
              <th>Tributos</th>
              <th>Outros</th>
              <th>Δ vs atual</th>
            </tr>
          </thead>
          <tbody>
            {validas.map(({ s, c, total }) => {
              const melhor = total === menor;
              const delta = total - totalAtual;
              return (
                <tr key={s.modalidade} className={melhor ? 'melhor' : undefined}>
                  <td>{nomeModalidade(s.modalidade)}</td>
                  <td className="celula-num">{fmtContrato(s.contratoOtimo)}</td>
                  <td className="celula-num font-semibold">{brl(total, 0)}</td>
                  <td className="celula-num">{eTotalMwh > 0 ? brl(total / eTotalMwh, 0) : '—'}</td>
                  <td className="celula-num">{brl(c!.TE, 0)}</td>
                  <td className="celula-num">{brl(c!.Fio, 0)}</td>
                  <td className="celula-num">{brl(c!.Demanda, 0)}</td>
                  <td className="celula-num">{brl(c!.Tributos, 0)}</td>
                  <td className="celula-num">{brl(c!.Outros, 0)}</td>
                  <td className="celula-num">
                    {Math.abs(delta) < 1 ? '—' : `${delta > 0 ? '+' : '−'}${brl(Math.abs(delta), 0)}`}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="mt-6">
        <ComparacaoComposicao
          titulo="Composição do custo por modalidade"
          linhas={validas.map(({ s, c, total }) => ({
            rotulo: nomeModalidade(s.modalidade),
            total,
            porMwh: eTotalMwh > 0 ? total / eTotalMwh : null,
            destaque: total === menor,
            fatias: FATIAS_COMPOSICAO.map((f) => ({ nome: f.nome, valor: c![f.chave], cor: f.cor })),
          }))}
          legenda={FATIAS_COMPOSICAO.map((f) => ({ nome: f.nome, cor: f.cor }))}
        />
      </div>
      {semComposicao.length ? (
        <p className="tela-apoio mt-3">
          Sem faturas mensais para compor: {semComposicao.join(', ')}.
        </p>
      ) : null}
    </Cartao>
  );
};

/* ------------------------------------------------------------------ */
/* 9. Mercado livre — E-PI                                             */
/* ------------------------------------------------------------------ */

const MercadoLivre: React.FC<{
  analise: Analise;
  piPeriodo: number | null;
  basePeriodo: number | null;
  n: number;
  aoAtualizarAcl: (m: Partial<InvoiceFormData>) => void;
}> = ({ analise, piPeriodo, basePeriodo, n, aoAtualizarAcl }) => {
  const epi = analise.epi;
  const form = analise.form;
  const temCustos = (form.opexMensal || 0) > 0 || (form.capex || 0) > 0;
  const [modo, setModo] = React.useState<'simples' | 'custos'>(temCustos ? 'custos' : 'simples');
  const sel = modo === 'custos' && epi.comCustos ? epi.comCustos : epi.simplificado;
  const [edit, setEdit] = React.useState({ opex: form.opexMensal || null, capex: form.capex || null, horiz: form.horizonteMeses || null, prop: form.precoMedioACL || null, enc: form.encargosAcl });
  const periodo = n >= 12 ? 'por ano' : `em ${n} ${n === 1 ? 'mês' : 'meses'}`;

  // Curva: período (E-PI do /planejamento) ou só o mês (E-PI do /epi/calcular).
  const curvaPeriodo = piPeriodo !== null && basePeriodo !== null;
  const piCurva = curvaPeriodo ? piPeriodo! : sel?.pi ?? null;
  const baseCurva = curvaPeriodo ? basePeriodo! : sel?.base_acl ?? null;

  return (
    <section className="rounded-2xl overflow-hidden border border-borda bg-white">
      <div className="bg-tinta text-white p-6 sm:p-8 flex flex-wrap justify-between gap-6">
        <div className="min-w-0 max-w-xl">
          <div className="tela-rotulo" style={{ color: COR.acento }}>Mercado livre</div>
          <h2 className="tela-titulo mt-2">Preço de indiferença (E-PI)</h2>
          <p className="tela-apoio text-white/70 mt-1">
            Teto para negociar a energia no ACL
            {epi.modalidade ? ` · modalidade ${nomeModalidade(epi.modalidade)}` : ''}
          </p>
        </div>
        <div className="text-right min-w-0">
          {sel ? (
            <>
              <div className="num text-4xl sm:text-5xl font-semibold" style={{ color: COR.acento }}>
                {numero(sel.pi, 2)} <span className="text-base text-white/70">R$/MWh</span>
              </div>
              <div className="tela-apoio text-white/60 mt-1">mês da fatura · {modo === 'custos' ? 'com custos de migração' : 'simplificado'}</div>
              {analise.epiRecomendada?.simplificado && analise.epiRecomendada.modalidade ? (
                <div className="num tela-apoio text-white/80 mt-1">
                  {nomeModalidade(analise.epiRecomendada.modalidade)}: {numero((modo === 'custos' && analise.epiRecomendada.comCustos ? analise.epiRecomendada.comCustos : analise.epiRecomendada.simplificado).pi, 2)} R$/MWh
                </div>
              ) : null}
              {piPeriodo !== null ? (
                <div className="num tela-apoio text-white/80 mt-1">
                  período ({n} {n === 1 ? 'mês' : 'meses'}): {numero(piPeriodo, 2)} R$/MWh
                </div>
              ) : null}
            </>
          ) : (
            <div className="max-w-sm text-left">
              <div className="tela-bloco" style={{ color: COR.acento }}>E-PI indisponível</div>
              <div className="tela-apoio text-white/70 mt-1 break-words">{epi.erro}</div>
            </div>
          )}
          {temCustos ? (
            <div className="mt-3 no-print">
              <Segmentos
                rotuloAria="Tipo de E-PI"
                valor={modo}
                aoMudar={setModo}
                opcoes={[
                  { valor: 'simples', rotulo: 'Simplificado' },
                  { valor: 'custos', rotulo: 'Com custos de migração' },
                ]}
              />
            </div>
          ) : null}
        </div>
      </div>

      <div className="p-5 sm:p-8 space-y-5">
        {epi.erro && sel ? <Aviso>{epi.erro}</Aviso> : null}
        {sel?.aviso ? <Aviso>{sel.aviso}</Aviso> : null}
        {piCurva !== null && baseCurva !== null && piCurva > 0 ? (
          <div>
            <h3 className="tela-bloco mb-3">Economia conforme o preço ofertado</h3>
            <GraficoEconomiaPreco
              titulo="Economia por preço ofertado"
              epi={piCurva}
              base={baseCurva}
              proposta={form.precoMedioACL || null}
              rotuloEpi={`E-PI ${numero(piCurva, 2)}`}
            />
            <p className="tela-apoio mt-2">
              R$ 10/MWh abaixo do E-PI = {brl(10 * baseCurva, 0)} {curvaPeriodo ? periodo : 'por mês'}
            </p>
          </div>
        ) : null}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-end">
          <div>
            <Rotulo htmlFor="epi-prop">Preço da proposta (R$/MWh)</Rotulo>
            <CampoNumero id="epi-prop" valor={edit.prop} aoMudar={(v) => setEdit({ ...edit, prop: v })} unidade="R$/MWh" />
          </div>
          {form.precoMedioACL > 0 && piCurva !== null && baseCurva !== null ? (
            <div className="text-sm">
              <strong style={{ color: form.precoMedioACL < piCurva ? COR.verde : COR.alerta }}>
                {form.precoMedioACL < piCurva ? 'Proposta abaixo do E-PI: migrar economiza' : 'Proposta acima do E-PI: migrar custa mais'}
              </strong>
              <div className="num">
                {brl(Math.abs((piCurva - form.precoMedioACL) * baseCurva), 0)} {curvaPeriodo ? periodo : 'por mês'} (estimativa)
              </div>
            </div>
          ) : null}
        </div>
        <div className="rounded-xl bg-fundo p-4">
          <h3 className="font-bold mb-3">Encargos e custos de migração</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <Rotulo htmlFor="epi-enc">Encargos do ACL</Rotulo>
              <CampoNumero id="epi-enc" valor={edit.enc} aoMudar={(v) => setEdit({ ...edit, enc: v })} unidade="R$/MWh" />
              <Dica>ESS/EER e CCEE. Vazio: fora do E-PI (premissa declarada).</Dica>
            </div>
            <div>
              <Rotulo htmlFor="epi-opex">OPEX mensal (R$)</Rotulo>
              <CampoNumero id="epi-opex" valor={edit.opex} aoMudar={(v) => setEdit({ ...edit, opex: v })} unidade="R$/mês" />
              <Dica>gestão, CCEE, comercializadora</Dica>
            </div>
            <div>
              <Rotulo htmlFor="epi-capex">CAPEX total (R$)</Rotulo>
              <CampoNumero id="epi-capex" valor={edit.capex} aoMudar={(v) => setEdit({ ...edit, capex: v })} unidade="R$" />
              <Dica>adequação da medição (SMF)</Dica>
            </div>
            <div>
              <Rotulo htmlFor="epi-horiz">Amortizar em (meses)</Rotulo>
              <CampoNumero id="epi-horiz" valor={edit.horiz} aoMudar={(v) => setEdit({ ...edit, horiz: v })} inteiro unidade="meses" />
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-3 mt-4 no-print">
            <Botao
              variante="escuro"
              disabled={(edit.capex ?? 0) > 0 && !((edit.horiz ?? 0) > 0)}
              onClick={() => {
                aoAtualizarAcl({
                  opexMensal: edit.opex ?? 0,
                  capex: edit.capex ?? 0,
                  horizonteMeses: edit.horiz ?? 60,
                  precoMedioACL: edit.prop ?? 0,
                  encargosAcl: edit.enc,
                });
                if ((edit.opex ?? 0) > 0 || (edit.capex ?? 0) > 0) setModo('custos');
              }}
            >
              Recalcular E-PI na API
            </Botao>
            <span className="text-xs text-texto2">
              Recalcula o E-PI do mês. O E-PI do período vem do planejamento feito com os valores da etapa 1.
            </span>
          </div>
        </div>

        <details className="border-t border-borda2 pt-4">
          <summary className="font-bold cursor-pointer">Como o E-PI é calculado</summary>
          <div className="text-sm text-texto2 mt-3 space-y-2">
            <p>Fórmula de docs/epi.md (Lemos, 2025), calculada pela API para um mês:</p>
            <pre className="num text-xs bg-fundo rounded-lg p-3 overflow-x-auto text-tinta">{`E          = e_ponta + e_fora_ponta
C_TE       = e_ponta·te_ponta + e_fora_ponta·te_fora_ponta
C_E_ACR    = (C_TE + E·bandeira) / ((1 − pis − cofins)·(1 − icms))
CUSTOS_ACL = opex_mensal + capex / horizonte_meses + E·(1+k)·encargos
BASE_ACL   = E·(1 + k) / (1 − icms)
PI         = (C_E_ACR − CUSTOS_ACL) / BASE_ACL`}</pre>
            <p>
              No período, a API soma mês a mês: PI = (Σ C_E_ACR − Σ CUSTOS_ACL) / Σ BASE_ACL, com a TE e a bandeira de cada
              mês. Perdas k = 3%. Sem OPEX/CAPEX o E-PI é o simplificado.
            </p>
            {epi.simplificado ? (
              <p className="num text-xs">
                Mês da fatura (API): E = {numero(epi.simplificado.e_mwh, 3)} MWh · C_TE = {brl(epi.simplificado.c_te)} · C_E_ACR ={' '}
                {brl(epi.simplificado.c_e_acr)} · BASE_ACL = {numero(epi.simplificado.base_acl, 3)} MWh · bandeira ={' '}
                {numero(epi.simplificado.bandeira_r_mwh, 2)} R$/MWh
              </p>
            ) : null}
          </div>
        </details>
      </div>
    </section>
  );
};

/* ------------------------------------------------------------------ */
/* 10. Conferência e premissas                                         */
/* ------------------------------------------------------------------ */

const ConferenciaPremissas: React.FC<{ analise: Analise; series: ResultadoSeries | null }> = ({ analise, series }) => {
  const ob = analise.modalidades.find((m) => m.modalidade === 'Optante B');
  const outrasIndisp = analise.modalidades.filter((m) => m.modalidade !== 'Optante B' && m.estado !== 'ok');
  const c = analise.conferencia;
  return (
    <details className="bg-white border border-borda rounded-2xl px-5 sm:px-6 py-4 scroll-mt-24">
      <summary className="cursor-pointer tela-secao">
        Detalhes técnicos
        <span className="tela-apoio ml-2 font-normal">conferência com a fatura, premissas e notas da API</span>
      </summary>
      <ul className="text-sm space-y-2 mt-4">
        <li>
          <strong>Conferência:</strong>{' '}
          {c
            ? `${c.retencoes !== null ? `recalculado ${brl(c.totalCalculado)} − retenções ${brl(c.retencoes)} = líquido ${brl(c.liquido)}` : `recalculada ${brl(c.totalCalculado)}`} × fatura real ${brl(c.totalFatura)} · Δ ${c.diferenca >= 0 ? '+' : '−'}${brl(Math.abs(c.diferenca))}.${c.reativoNaoCobrado ? ' O reativo informado não gerou excedente (art. 304): a diferença é o reativo da fatura real.' : ''}`
            : 'total da fatura não informado: sem conferência com a conta real.'}
        </li>
        <li>
          <strong>Optante B:</strong>{' '}
          {!ob
            ? 'não se aplica a este subgrupo.'
            : ob.estado === 'ok'
              ? `avaliado: ${brl(ob.atual!.total)} no mês.`
              : ob.estado === 'nao_avaliado'
                ? 'não avaliado — a potência dos transformadores (kVA) não foi informada (não avaliado ≠ inelegível).'
                : `inelegível — ${ob.motivo}`}
        </li>
        {outrasIndisp.map((m) => (
          <li key={m.modalidade}>
            <strong>{nomeModalidade(m.modalidade)}:</strong> {m.estado === 'nao_avaliado' ? 'não avaliada' : 'indisponível'} — {m.motivo}
          </li>
        ))}
        {analise.modalidades
          .filter((m) => m.selo)
          .map((m) => (
            <li key={`h-${m.modalidade}`}>
              <strong>{nomeModalidade(m.modalidade)}:</strong> {m.selo}.
            </li>
          ))}
        {analise.premissas
          .filter((p) => !p.startsWith('Optante B') && !p.startsWith('Total da fatura'))
          .map((p) => (
            <li key={p}>• {p}</li>
          ))}
        {[...analise.avisosPlanejamento, ...(analise.planejamento?.avisos ?? [])].map((a) => (
          <li key={a}>• {a}</li>
        ))}
        {analise.planejamentoErro ? <li>• Planejamento (API): {analise.planejamentoErro}</li> : null}
        {analise.notas.map((n, i) => (
          <li key={i}>
            • <span className="num text-xs">{n.tipo}</span> {n.mensagem}
          </li>
        ))}
        {series?.erros.map((e) => (
          <li key={e}>• Série mensal: {e}</li>
        ))}
        <li>• Comparação do Grupo A: Verde, Azul e Optante B (Convencional e Branca não entram).</li>
        <li>• CIP/COSIP e outros valores ficam fora do custo técnico (D4) nas comparações mensais e no planejamento.</li>
      </ul>
      {analise.epi.erro && analise.epi.corpo ? (
        <details className="mt-4">
          <summary className="tela-bloco cursor-pointer">Corpo enviado ao E-PI</summary>
          <pre className="num text-xs bg-fundo rounded-lg p-3 mt-2 overflow-x-auto">{JSON.stringify(analise.epi.corpo, null, 2)}</pre>
          <p className="tela-apoio mt-1">Resposta: {analise.epi.erro}</p>
        </details>
      ) : null}
    </details>
  );
};
