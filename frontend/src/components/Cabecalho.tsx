import React from 'react';

export type Etapa = 1 | 2 | 3;

/** Logo A (Logos.dc.html): fatura com barras Verde/Azul, linha do E-PI e selo de energia. */
export const Logo: React.FC<{ tamanho?: number }> = ({ tamanho = 36 }) => (
  <svg width={tamanho} height={tamanho} viewBox="0 0 42 42" aria-hidden="true">
    <path
      d="M10 6h13l6 6v21a1 1 0 0 1-1 1H10a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1z"
      fill="#FFFFFF"
      stroke="#13232E"
      strokeWidth="2"
      strokeLinejoin="round"
    />
    <path d="M23 6v6h6" fill="none" stroke="#13232E" strokeWidth="2" strokeLinejoin="round" />
    <rect x="12.5" y="21" width="4" height="9" rx="1" fill="#1F8A4C" />
    <rect x="18.5" y="16" width="4" height="14" rx="1" fill="#2B59C3" />
    <path d="M11.5 18.5h13" stroke="#C2410C" strokeWidth="1.6" strokeDasharray="2 1.6" />
    <circle cx="31" cy="31" r="8.5" fill="#F2A900" stroke="#FFFFFF" strokeWidth="2.5" />
    <path d="M32.6 24.8l-5.2 7.2h3.6l-1.6 5.2 5.4-7.4h-3.6z" fill="#13232E" />
  </svg>
);

const ETAPAS: { n: Etapa; rotulo: string }[] = [
  { n: 1, rotulo: 'Dados' },
  { n: 2, rotulo: 'Fatura simulada' },
  { n: 3, rotulo: 'Análise e E-PI' },
];

export const Cabecalho: React.FC<{
  etapa: Etapa;
  /** Etapas que já podem ser abertas (2 e 3 só depois do cálculo). */
  liberadas: Etapa[];
  aoIr: (e: Etapa) => void;
}> = ({ etapa, liberadas, aoIr }) => (
  <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-borda no-print">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-x-6 gap-y-3">
      <div className="flex items-center gap-3 min-w-0">
        <Logo />
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-bold text-lg leading-none">Simulador</span>
            <span className="num text-[11px] font-semibold rounded-md bg-acento/20 text-[#8a5a00] px-1.5 py-0.5">
              ACR × ACL
            </span>
          </div>
          <div className="text-xs text-texto2 mt-1">Tarifas e mercado livre · Grupo A</div>
        </div>
      </div>
      <nav aria-label="Etapas" className="w-full sm:w-auto">
        <ol className="flex items-center gap-1 sm:gap-2">
          {ETAPAS.map((e, i) => {
            const ativa = e.n === etapa;
            const livre = liberadas.includes(e.n);
            return (
              <li key={e.n} className="flex items-center gap-1 sm:gap-2 min-w-0">
                {i > 0 ? <span aria-hidden className="hidden sm:block w-6 h-px bg-borda" /> : null}
                <button
                  type="button"
                  disabled={!livre}
                  aria-current={ativa ? 'step' : undefined}
                  onClick={() => aoIr(e.n)}
                  className={`flex items-center gap-2 rounded-full pl-1.5 pr-3 py-1.5 text-sm font-semibold transition ${
                    ativa ? 'bg-tinta text-white' : livre ? 'text-tinta hover:bg-fundo cursor-pointer' : 'text-texto2 cursor-not-allowed'
                  }`}
                >
                  <span
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      ativa ? 'bg-acento text-tinta' : 'bg-fundo text-tinta'
                    }`}
                  >
                    {e.n}
                  </span>
                  <span className={ativa ? '' : 'hidden md:inline'}>{e.rotulo}</span>
                </button>
              </li>
            );
          })}
        </ol>
      </nav>
    </div>
  </header>
);
