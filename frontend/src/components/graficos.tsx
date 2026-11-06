/**
 * Gráficos SVG simples (sem biblioteca). Escalam pela largura do contêiner
 * (viewBox) e nunca causam rolagem horizontal. Só desenham números recebidos.
 */
import React from 'react';
import { COR, compacto, numero } from '../lib/formato';

/** Largura real do contêiner (px): o desenho usa essa escala e o texto fica legível no celular. */
function useLargura(padrao = 800) {
  const ref = React.useRef<HTMLDivElement>(null);
  const [L, setL] = React.useState(padrao);
  React.useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const medir = () => setL(Math.max(320, Math.round(el.clientWidth || padrao)));
    medir();
    const ro = new ResizeObserver(medir);
    ro.observe(el);
    return () => ro.disconnect();
  }, [padrao]);
  return { ref, L };
}

function escala(min: number, max: number, a: number, b: number) {
  const d = max - min || 1;
  return (v: number) => a + ((v - min) / d) * (b - a);
}

/** Marcas "bonitas" para o eixo. */
export function marcas(min: number, max: number, n = 5): number[] {
  if (!(max > min)) return [min];
  const passoBruto = (max - min) / n;
  const p10 = 10 ** Math.floor(Math.log10(passoBruto));
  const passo = [1, 2, 2.5, 5, 10].map((m) => m * p10).find((p) => p >= passoBruto) ?? passoBruto;
  const ini = Math.ceil(min / passo) * passo;
  const out: number[] = [];
  for (let v = ini; v <= max + passo * 1e-9; v += passo) out.push(Number(v.toFixed(10)));
  return out;
}

const EixoY: React.FC<{ ticks: number[]; y: (v: number) => number; x0: number; x1: number; fmt?: (v: number) => string }> = ({
  ticks,
  y,
  x0,
  x1,
  fmt = compacto,
}) => (
  <g>
    {ticks.map((t) => (
      <g key={t}>
        <line x1={x0} x2={x1} y1={y(t)} y2={y(t)} stroke={COR.borda2} />
        <text x={x0 - 8} y={y(t) + 4} textAnchor="end" fontSize="12" fill={COR.texto2} className="num">
          {fmt(t)}
        </text>
      </g>
    ))}
  </g>
);

/* ------------------------------------------------------------------ */

export interface SerieLinha {
  nome: string;
  cor: string;
  valores: (number | null)[];
  tracejada?: boolean;
}

/** Linhas por mês (Verde × Azul etc.), com rótulo no fim de cada série. */
export const GraficoLinhas: React.FC<{
  rotulosX: string[];
  series: SerieLinha[];
  altura?: number;
  fmtY?: (v: number) => string;
  titulo: string;
  preencherEntre?: boolean;
}> = ({ rotulosX, series, altura = 300, fmtY, titulo, preencherEntre }) => {
  const { ref, L } = useLargura();
  const todos = series.flatMap((s) => s.valores.filter((v): v is number => v !== null));
  if (todos.length === 0) return null;
  const min0 = Math.min(...todos);
  const max0 = Math.max(...todos);
  const folga = (max0 - min0) * 0.12 || max0 * 0.1 || 1;
  const ticks = marcas(Math.max(0, min0 - folga), max0 + folga);
  const x0 = 64;
  const x1 = L - 70;
  const yA = 16;
  const yB = altura - 34;
  const y = escala(ticks[0], ticks[ticks.length - 1], yB, yA);
  const n = rotulosX.length;
  const x = (i: number) => (n === 1 ? (x0 + x1) / 2 : x0 + 20 + (i * (x1 - x0 - 40)) / (n - 1));
  const caminho = (v: (number | null)[]) =>
    v
      .map((val, i) => (val === null ? null : `${x(i).toFixed(1)},${y(val).toFixed(1)}`))
      .filter(Boolean)
      .join(' L ');
  let area: string | null = null;
  if (preencherEntre && series.length === 2) {
    const [a, b] = series;
    const ok = a.valores.every((v) => v !== null) && b.valores.every((v) => v !== null);
    if (ok) {
      const ida = a.valores.map((v, i) => `${x(i)},${y(v as number)}`);
      const volta = b.valores.map((v, i) => `${x(i)},${y(v as number)}`).reverse();
      area = `M ${[...ida, ...volta].join(' L ')} Z`;
    }
  }
  return (
    <div ref={ref} className="w-full">
      <svg viewBox={`0 0 ${L} ${altura}`} width="100%" role="img" aria-label={titulo} className="block">
      <EixoY ticks={ticks} y={y} x0={x0} x1={x1} fmt={fmtY} />
      {area ? <path d={area} fill={series[1].cor} opacity={0.08} /> : null}
      {rotulosX.map((r, i) =>
        n > 6 && L < 640 && i % 2 === 1 ? null : (
          <text key={r + i} x={x(i)} y={altura - 10} textAnchor="middle" fontSize="12" fill={COR.texto2}>
            {r}
          </text>
        ),
      )}
      {series.map((s) => {
        const ultimo = [...s.valores].reverse().find((v) => v !== null);
        const iU = s.valores.lastIndexOf(ultimo ?? null);
        return (
          <g key={s.nome}>
            <path
              d={`M ${caminho(s.valores)}`}
              fill="none"
              stroke={s.cor}
              strokeWidth={2.5}
              strokeDasharray={s.tracejada ? '6 5' : undefined}
            />
            {s.valores.map((v, i) =>
              v === null ? null : (
                <circle key={i} cx={x(i)} cy={y(v)} r={3.5} fill={s.cor}>
                  <title>{`${s.nome} · ${rotulosX[i]}: ${fmtY ? fmtY(v) : numero(v)}`}</title>
                </circle>
              ),
            )}
            {ultimo !== undefined && ultimo !== null ? (
              <text x={x(iU) + 10} y={y(ultimo) + 4} fontSize="13" fontWeight={700} fill={COR.tinta}>
                {s.nome}
              </text>
            ) : null}
          </g>
        );
      })}
    </svg>
    </div>
  );
};

/* ------------------------------------------------------------------ */

export interface Barra {
  rotulo: string;
  valor: number | null;
  cor: string;
  marca?: string; // texto sobre a barra
  destaque?: boolean;
}

/** Barras verticais com linhas de referência opcionais. */
export const GraficoBarras: React.FC<{
  barras: Barra[];
  titulo: string;
  altura?: number;
  referencias?: { valor: number; rotulo: string; cor: string; tracejada?: boolean }[];
  faixa?: { de: number; ate: number; cor: string; rotulo?: string };
  fmtY?: (v: number) => string;
  mostrarValores?: boolean;
}> = ({ barras, titulo, altura = 260, referencias = [], faixa, fmtY, mostrarValores = true }) => {
  const { ref, L } = useLargura();
  const vals = [
    ...barras.map((b) => b.valor ?? 0),
    ...referencias.map((r) => r.valor),
    faixa ? faixa.ate : 0,
  ];
  const ticks = marcas(0, Math.max(...vals, 1) * 1.12);
  const x0 = 56;
  const x1 = L - 12;
  const yA = 18;
  const yB = altura - 30;
  const y = escala(0, ticks[ticks.length - 1], yB, yA);
  const n = barras.length;
  const larg = (x1 - x0) / Math.max(n, 1);
  return (
    <div ref={ref} className="w-full">
      <svg viewBox={`0 0 ${L} ${altura}`} width="100%" role="img" aria-label={titulo} className="block">
      <EixoY ticks={ticks} y={y} x0={x0} x1={x1} fmt={fmtY} />
      {faixa ? (
        <g>
          <rect x={x0} width={x1 - x0} y={y(faixa.ate)} height={Math.max(1, y(faixa.de) - y(faixa.ate))} fill={faixa.cor} opacity={0.18} />
          {faixa.rotulo ? (
            <text x={x1 - 4} y={y(faixa.ate) - 4} textAnchor="end" fontSize="11" fill={COR.texto2}>
              {faixa.rotulo}
            </text>
          ) : null}
        </g>
      ) : null}
      {barras.map((b, i) => {
        const bx = x0 + i * larg + larg * 0.18;
        const bw = larg * 0.64;
        if (b.valor === null) {
          return (
            <text key={i} x={bx + bw / 2} y={yB - 6} textAnchor="middle" fontSize="11" fill={COR.texto2}>
              —
            </text>
          );
        }
        return (
          <g key={i}>
            <rect x={bx} width={bw} y={y(b.valor)} height={Math.max(0, yB - y(b.valor))} rx={3} fill={b.cor}>
              <title>{`${b.rotulo}: ${fmtY ? fmtY(b.valor) : numero(b.valor, 1)}`}</title>
            </rect>
            {mostrarValores && bw >= 18 ? (
              <text x={bx + bw / 2} y={y(b.valor) - 5} textAnchor="middle" fontSize={bw < 28 ? 9 : 11} fontWeight={600} fill={COR.tinta} className="num">
                {b.marca ?? numero(b.valor, 0)}
              </text>
            ) : null}
            <text x={bx + bw / 2} y={altura - 10} textAnchor="middle" fontSize="11" fill={COR.texto2}>
              {b.rotulo}
            </text>
          </g>
        );
      })}
      {referencias.map((r) => (
        <g key={r.rotulo}>
          <line x1={x0} x2={x1} y1={y(r.valor)} y2={y(r.valor)} stroke={r.cor} strokeWidth={2} strokeDasharray={r.tracejada ? '6 4' : undefined} />
          <text x={x0 + 6} y={y(r.valor) - 5} fontSize="11" fontWeight={700} fill={r.cor}>
            {r.rotulo}
          </text>
        </g>
      ))}
      <line x1={x0} x2={x1} y1={yB} y2={yB} stroke={COR.tinta} />
    </svg>
    </div>
  );
};

/* ------------------------------------------------------------------ */

export interface Fatia {
  nome: string;
  valor: number;
  cor: string;
}

/** Barra horizontal empilhada com % em cada fatia. */
export const BarraEmpilhada: React.FC<{ fatias: Fatia[]; titulo: string; alturaPx?: number }> = ({ fatias, titulo, alturaPx = 34 }) => {
  const total = fatias.reduce((a, f) => a + Math.max(0, f.valor), 0);
  if (total <= 0) return null;
  return (
    <div role="img" aria-label={titulo} className="flex w-full overflow-hidden rounded-md" style={{ height: alturaPx }}>
      {fatias
        .filter((f) => f.valor > 0)
        .map((f) => {
          const p = f.valor / total;
          return (
            <div
              key={f.nome}
              title={`${f.nome}: ${numero(p * 100, 1)}%`}
              className="flex items-center justify-center text-[11px] font-semibold text-tinta/90 num border-r border-white last:border-r-0 min-w-0"
              style={{ width: `${p * 100}%`, background: f.cor }}
            >
              {p >= 0.06 ? `${numero(p * 100)}%` : ''}
            </div>
          );
        })}
    </div>
  );
};

export const Legenda: React.FC<{ itens: { nome: string; cor: string; tracejada?: boolean }[] }> = ({ itens }) => (
  <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm">
    {itens.map((i) => (
      <span key={i.nome} className="inline-flex items-center gap-1.5">
        <span
          className="w-3 h-3 rounded-sm"
          style={i.tracejada ? { border: `2px dashed ${i.cor}`, background: `${i.cor}33` } : { background: i.cor }}
        />
        {i.nome}
      </span>
    ))}
  </div>
);

/* ------------------------------------------------------------------ */

export interface DegrauCascata {
  rotulo: string;
  sub?: string;
  /** total = barra cheia a partir de 0; delta = variação a partir do anterior. */
  tipo: 'total' | 'delta';
  valor: number;
  cor: string;
  tracejado?: boolean;
}

/** Cascata: do custo de hoje ao custo otimizado (e ao livre, tracejado). */
export const GraficoCascata: React.FC<{ degraus: DegrauCascata[]; titulo: string; altura?: number }> = ({
  degraus,
  titulo,
  altura = 320,
}) => {
  const { ref, L } = useLargura();
  let nivel = 0;
  const barras = degraus.map((d) => {
    if (d.tipo === 'total') {
      nivel = d.valor;
      return { ...d, de: 0, ate: d.valor };
    }
    const de = nivel;
    nivel = nivel + d.valor;
    return { ...d, de, ate: nivel };
  });
  const tops = barras.flatMap((b) => [b.de, b.ate]).filter((v) => v > 0);
  const totais = barras.filter((b) => b.tipo === 'total').map((b) => b.ate);
  const minTotal = Math.min(...totais, ...barras.filter((b) => b.tipo === 'delta').map((b) => Math.min(b.de, b.ate)));
  const maxV = Math.max(...tops);
  // Eixo começa perto do menor valor para a variação ficar visível (como no protótipo).
  const ticks = marcas(Math.max(0, minTotal - (maxV - minTotal) * 0.6), maxV * 1.02);
  const x0 = 64;
  const x1 = L - 10;
  const yA = 26;
  const yB = altura - 48;
  const y = escala(ticks[0], ticks[ticks.length - 1], yB, yA);
  const yc = (v: number) => Math.min(yB, Math.max(yA, y(v)));
  const n = barras.length;
  const larg = (x1 - x0) / n;
  return (
    <div ref={ref} className="w-full">
      <svg viewBox={`0 0 ${L} ${altura}`} width="100%" role="img" aria-label={titulo} className="block">
      <EixoY ticks={ticks} y={y} x0={x0} x1={x1} />
      {barras.map((b, i) => {
        const bx = x0 + i * larg + larg * 0.12;
        const bw = larg * 0.76;
        const top = yc(Math.max(b.de, b.ate));
        const bot = b.tipo === 'total' ? yB : yc(Math.min(b.de, b.ate));
        const h = Math.max(2, bot - top);
        const rot = b.tipo === 'total' ? compacto(b.valor) : b.valor === 0 ? '0' : `${b.valor < 0 ? '−' : '+'}${compacto(Math.abs(b.valor))}`;
        return (
          <g key={b.rotulo}>
            <rect
              x={bx}
              y={top}
              width={bw}
              height={h}
              rx={3}
              fill={b.tracejado ? `${b.cor}55` : b.cor}
              stroke={b.tracejado ? b.cor : undefined}
              strokeWidth={b.tracejado ? 2 : undefined}
              strokeDasharray={b.tracejado ? '6 4' : undefined}
            />
            <text x={bx + bw / 2} y={top - 7} textAnchor="middle" fontSize="13" fontWeight={700} className="num" fill={COR.tinta}>
              {rot}
            </text>
            {i < n - 1 ? (
              <line x1={bx + bw} x2={bx + larg} y1={yc(b.ate)} y2={yc(b.ate)} stroke={COR.texto2} strokeDasharray="3 3" />
            ) : null}
            {L < 560 ? (
              <text x={bx + bw / 2} y={altura - 30} textAnchor="middle" fontSize={10} fontWeight={600} fill={COR.tinta}>
                {b.rotulo.split(' ').map((p, k, arr) => (
                  <tspan key={k} x={bx + bw / 2} dy={k === 0 ? (arr.length > 1 ? 0 : 6) : 12}>
                    {p}
                  </tspan>
                ))}
              </text>
            ) : (
              <text x={bx + bw / 2} y={altura - 28} textAnchor="middle" fontSize={13} fontWeight={600} fill={COR.tinta}>
                {b.rotulo}
              </text>
            )}
            {b.sub && L >= 560 ? (
              <text x={bx + bw / 2} y={altura - 12} textAnchor="middle" fontSize="11" fill={COR.texto2}>
                {b.sub}
              </text>
            ) : null}
          </g>
        );
      })}
      <line x1={x0} x2={x1} y1={yB} y2={yB} stroke={COR.tinta} />
    </svg>
    </div>
  );
};

/* ------------------------------------------------------------------ */

/** Curva custo × DC (pontos amostrados), com faixa boa e marcadores. */
export const GraficoCurva: React.FC<{
  pontos: { x: number; y: number }[];
  titulo: string;
  cor: string;
  faixa?: [number, number] | null;
  marcadores?: { x: number; y: number; rotulo: string; cor: string }[];
  rotuloX: string;
  altura?: number;
}> = ({ pontos, titulo, cor, faixa, marcadores = [], rotuloX, altura = 320 }) => {
  const { ref, L } = useLargura();
  if (pontos.length < 2) return null;
  const xs = pontos.map((p) => p.x);
  const ys = pontos.map((p) => p.y);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const ticksY = marcas(minY - (maxY - minY) * 0.05, maxY + (maxY - minY) * 0.08);
  const ticksX = marcas(Math.min(...xs), Math.max(...xs), 7);
  const x0 = 70;
  const x1 = L - 16;
  const yA = 20;
  const yB = altura - 50;
  const x = escala(Math.min(...xs), Math.max(...xs), x0, x1);
  const y = escala(ticksY[0], ticksY[ticksY.length - 1], yB, yA);
  return (
    <div ref={ref} className="w-full">
      <svg viewBox={`0 0 ${L} ${altura}`} width="100%" role="img" aria-label={titulo} className="block">
      <EixoY ticks={ticksY} y={y} x0={x0} x1={x1} />
      {faixa ? (
        <g>
          <rect x={x(faixa[0])} width={Math.max(2, x(faixa[1]) - x(faixa[0]))} y={yA} height={yB - yA} fill={COR.verde} opacity={0.09} />
          <text x={(x(faixa[0]) + x(faixa[1])) / 2} y={yA + 14} textAnchor="middle" fontSize="12" fontWeight={600} fill={COR.verde}>
            faixa boa (até +0,5%)
          </text>
        </g>
      ) : null}
      <path d={`M ${pontos.map((p) => `${x(p.x)},${y(p.y)}`).join(' L ')}`} fill="none" stroke={cor} strokeWidth={2.5} />
      {pontos.map((p) => (
        <circle key={p.x} cx={x(p.x)} cy={y(p.y)} r={3} fill={cor}>
          <title>{`${numero(p.x)} kW: ${compacto(p.y)}`}</title>
        </circle>
      ))}
      {marcadores.map((m) => (
        <g key={m.rotulo}>
          <line x1={x(m.x)} x2={x(m.x)} y1={y(m.y)} y2={yB} stroke={m.cor} strokeDasharray="3 3" />
          <circle cx={x(m.x)} cy={y(m.y)} r={6} fill={m.cor} stroke="#fff" strokeWidth={2} />
          <text
            x={x(m.x)}
            y={y(m.y) - 12}
            textAnchor={x(m.x) > L - 160 ? 'end' : x(m.x) < 160 ? 'start' : 'middle'}
            fontSize="12"
            fontWeight={700}
            fill={COR.tinta}
          >
            {m.rotulo}
          </text>
        </g>
      ))}
      <line x1={x0} x2={x1} y1={yB} y2={yB} stroke={COR.tinta} />
      {ticksX.map((t) => (
        <text key={t} x={x(t)} y={yB + 18} textAnchor="middle" fontSize="12" fill={COR.texto2} className="num">
          {numero(t)}
        </text>
      ))}
      <text x={(x0 + x1) / 2} y={altura - 8} textAnchor="middle" fontSize="12" fill={COR.texto2}>
        {rotuloX}
      </text>
    </svg>
    </div>
  );
};

/** Reta de economia × preço (E-PI): positivo = migrar economiza. */
export const GraficoEconomiaPreco: React.FC<{
  epi: number;
  base: number;
  titulo: string;
  proposta?: number | null;
  altura?: number;
  rotuloEpi: string;
}> = ({ epi, base, titulo, proposta, altura = 280, rotuloEpi }) => {
  const { ref, L } = useLargura();
  const pMin = Math.max(0, Math.floor((epi * 0.65) / 10) * 10);
  const pMax = Math.ceil((epi * 1.35) / 10) * 10;
  const f = (p: number) => (epi - p) * base;
  const vMax = Math.max(Math.abs(f(pMin)), Math.abs(f(pMax)));
  const ticksY = marcas(-vMax, vMax, 6);
  const ticksX = marcas(pMin, pMax, 6);
  const x0 = 70;
  const x1 = L - 16;
  const yA = 16;
  const yB = altura - 46;
  const x = escala(pMin, pMax, x0, x1);
  const y = escala(ticksY[0], ticksY[ticksY.length - 1], yB, yA);
  const yZero = y(0);
  return (
    <div ref={ref} className="w-full">
      <svg viewBox={`0 0 ${L} ${altura}`} width="100%" role="img" aria-label={titulo} className="block">
      <EixoY ticks={ticksY} y={y} x0={x0} x1={x1} />
      <path d={`M ${x(pMin)},${yZero} L ${x(pMin)},${y(f(pMin))} L ${x(epi)},${yZero} Z`} fill={COR.verde} opacity={0.12} />
      <path d={`M ${x(epi)},${yZero} L ${x(pMax)},${y(f(pMax))} L ${x(pMax)},${yZero} Z`} fill={COR.alerta} opacity={0.1} />
      <line x1={x0} x2={x1} y1={yZero} y2={yZero} stroke={COR.texto2} />
      <line x1={x(pMin)} x2={x(pMax)} y1={y(f(pMin))} y2={y(f(pMax))} stroke={COR.tinta} strokeWidth={2.5} />
      <text x={x0 + 10} y={yZero - 10} fontSize="12" fontWeight={600} fill={COR.verde}>
        migrar economiza
      </text>
      <text x={x1 - 10} y={yZero + 20} textAnchor="end" fontSize="12" fontWeight={600} fill={COR.alerta}>
        migrar custa mais
      </text>
      <circle cx={x(epi)} cy={yZero} r={6} fill={COR.acl} stroke="#fff" strokeWidth={2} />
      <text x={x(epi) + 10} y={yZero - 12} fontSize="13" fontWeight={700} fill={COR.tinta}>
        {rotuloEpi}
      </text>
      {proposta && proposta >= pMin && proposta <= pMax ? (
        <g>
          <circle cx={x(proposta)} cy={y(f(proposta))} r={6} fill={COR.acento} stroke={COR.tinta} strokeWidth={1.5} />
          <text x={x(proposta)} y={y(f(proposta)) - 12} textAnchor="middle" fontSize="12" fontWeight={700} fill={COR.tinta}>
            proposta
          </text>
        </g>
      ) : null}
      {ticksX.map((t) => (
        <text key={t} x={x(t)} y={yB + 18} textAnchor="middle" fontSize="12" fill={COR.texto2} className="num">
          {numero(t)}
        </text>
      ))}
      <text x={(x0 + x1) / 2} y={altura - 6} textAnchor="middle" fontSize="12" fill={COR.texto2}>
        Preço da energia ofertado no mercado livre (R$/MWh)
      </text>
    </svg>
    </div>
  );
};
