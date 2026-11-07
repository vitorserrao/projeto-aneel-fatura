/** Peças de interface compartilhadas pelas três etapas (visual do protótipo). */
import React from 'react';

export const Cartao: React.FC<{ className?: string; id?: string; children: React.ReactNode }> = ({
  className = '',
  id,
  children,
}) => (
  <section
    id={id}
    className={`bg-white border border-borda rounded-2xl p-5 sm:p-6 scroll-mt-24 min-w-0 ${className}`}
  >
    {children}
  </section>
);

export const TituloSecao: React.FC<{
  titulo: React.ReactNode;
  sub?: React.ReactNode;
  acao?: React.ReactNode;
  nivel?: 'h2' | 'h3';
}> = ({ titulo, sub, acao, nivel = 'h2' }) => {
  const H = nivel;
  return (
    <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
      <div className="min-w-0">
        <H className="tela-secao">{titulo}</H>
        {sub ? <p className="tela-apoio mt-1 max-w-3xl">{sub}</p> : null}
      </div>
      {acao}
    </div>
  );
};

/** Bloco "Leitura": frase tirada dos números. */
export const Leitura: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="mt-4 flex gap-3 border-l-4 border-tinta bg-fundo/70 rounded-r-lg px-4 py-3 text-sm">
    <strong className="shrink-0">Leitura</strong>
    <div className="min-w-0">{children}</div>
  </div>
);

export const Aviso: React.FC<{ tom?: 'alerta' | 'info' | 'erro'; children: React.ReactNode }> = ({
  tom = 'alerta',
  children,
}) => {
  const cls =
    tom === 'erro'
      ? 'bg-red-50 border-red-300 text-red-900'
      : tom === 'info'
        ? 'bg-fundo border-borda text-texto2'
        : 'bg-amber-50 border-amber-200 text-amber-900';
  return (
    <div className={`rounded-xl border px-4 py-3 text-sm ${cls}`} role={tom === 'erro' ? 'alert' : undefined}>
      {children}
    </div>
  );
};

export const Selo: React.FC<{ cor?: string; children: React.ReactNode; className?: string }> = ({
  cor,
  children,
  className = '',
}) => (
  <span
    className={`inline-flex items-center rounded-md px-1.5 py-0.5 text-[11px] font-semibold ${className}`}
    style={cor ? { color: cor, background: `${cor}18` } : undefined}
  >
    {children}
  </span>
);

/** Rótulo de campo com marca de obrigatório. */
export const Rotulo: React.FC<{ htmlFor?: string; obrigatorio?: boolean; extra?: React.ReactNode; children: React.ReactNode }> = ({
  htmlFor,
  obrigatorio,
  extra,
  children,
}) => (
  <label htmlFor={htmlFor} className="flex flex-wrap items-center gap-1.5 text-sm font-semibold mb-1.5">
    <span>
      {children}
      {obrigatorio ? (
        <span className="text-alerta ml-0.5" title="obrigatório" aria-label="obrigatório">
          *
        </span>
      ) : null}
    </span>
    {extra}
  </label>
);

export const Dica: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <p className="text-xs text-texto2 mt-1.5">{children}</p>
);

/**
 * Ajuda em tooltip: para a regra que o usuário consulta só quando tem dúvida.
 * Substitui a `Dica` quando o texto é longo e não muda a cada digitação — o
 * formulário deixa de ter 19 parágrafos de explicação abertos.
 */
export const Ajuda: React.FC<{ texto: string; rotulo?: string }> = ({ texto, rotulo = 'Ajuda' }) => (
  <span
    role="note"
    tabIndex={0}
    title={texto}
    aria-label={`${rotulo}: ${texto}`}
    className="inline-flex items-center justify-center w-4 h-4 ml-1 align-middle rounded-full border border-borda text-[10px] font-bold text-texto2 cursor-help select-none"
  >
    ?
  </span>
);

const baseInput =
  'w-full h-11 rounded-xl border border-borda bg-white px-3.5 text-[15px] outline-none transition focus:border-tinta focus:ring-2 focus:ring-acento/40 disabled:bg-fundo disabled:text-texto2';

/**
 * Campo numérico: vazio = null (nunca vira 0); aceita vírgula decimal.
 * Mantém o texto digitado enquanto o usuário edita.
 */
export const CampoNumero: React.FC<{
  id: string;
  valor: number | null;
  aoMudar: (v: number | null) => void;
  unidade?: string;
  placeholder?: string;
  min?: number;
  inteiro?: boolean;
  invalido?: boolean;
}> = ({ id, valor, aoMudar, unidade, placeholder, min = 0, inteiro = false, invalido = false }) => {
  const formatar = (v: number | null) => (v === null || Number.isNaN(v) ? '' : String(v).replace('.', ','));
  const [texto, setTexto] = React.useState(formatar(valor));
  const ultimo = React.useRef(valor);
  React.useEffect(() => {
    if (valor !== ultimo.current) {
      setTexto(formatar(valor));
      ultimo.current = valor;
    }
  }, [valor]);
  return (
    <div className="relative">
      <input
        id={id}
        inputMode="decimal"
        value={texto}
        placeholder={placeholder}
        aria-invalid={invalido || undefined}
        onChange={(e) => {
          const t = e.target.value;
          setTexto(t);
          const s = t.trim();
          // "1.234,5" (pt-BR), "1.234" (milhar) ou "0.95" (ponto decimal).
          const limpo = s.includes(',')
            ? s.replace(/\./g, '').replace(',', '.')
            : /^\d{1,3}(\.\d{3})+$/.test(s)
              ? s.replace(/\./g, '')
              : s;
          let v: number | null = limpo === '' ? null : Number(limpo);
          if (v !== null && (Number.isNaN(v) || v < min)) v = null;
          if (v !== null && inteiro) v = Math.round(v);
          ultimo.current = v;
          aoMudar(v);
        }}
        className={`${baseInput} num ${unidade ? 'pr-16' : ''} ${invalido ? 'border-alerta' : ''}`}
      />
      {unidade ? (
        <span className="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-xs text-texto2">
          {unidade}
        </span>
      ) : null}
    </div>
  );
};

export const CampoTexto: React.FC<{
  id: string;
  valor: string;
  aoMudar: (v: string) => void;
  placeholder?: string;
  mono?: boolean;
}> = ({ id, valor, aoMudar, placeholder, mono }) => (
  <input
    id={id}
    value={valor}
    placeholder={placeholder}
    onChange={(e) => aoMudar(e.target.value)}
    className={`${baseInput} ${mono ? 'num' : ''}`}
  />
);

export const CampoSelecao: React.FC<{
  id: string;
  valor: string;
  aoMudar: (v: string) => void;
  opcoes: { valor: string; rotulo: string }[];
  vazio?: string;
}> = ({ id, valor, aoMudar, opcoes, vazio }) => (
  <select id={id} value={valor} onChange={(e) => aoMudar(e.target.value)} className={`${baseInput} pr-8 cursor-pointer`}>
    {vazio !== undefined ? <option value="">{vazio}</option> : null}
    {opcoes.map((o) => (
      <option key={o.valor} value={o.valor}>
        {o.rotulo}
      </option>
    ))}
  </select>
);

/** Campo calculado (somente leitura). */
export const Calculado: React.FC<{ rotulo: string; valor: string; dica?: string }> = ({ rotulo, valor, dica }) => (
  <div className="min-w-0">
    <div className="flex items-center gap-1.5 text-sm font-semibold mb-1.5">
      {rotulo}
      <Selo cor="#1F8A4C">calculado</Selo>
    </div>
    <div className="h-11 rounded-xl border border-dashed border-borda bg-fundo px-3.5 flex items-center num text-[15px] truncate">
      {valor}
    </div>
    {dica ? <Dica>{dica}</Dica> : null}
  </div>
);

export const Marcador: React.FC<{
  id: string;
  marcado: boolean;
  aoMudar: (v: boolean) => void;
  rotulo: React.ReactNode;
  dica?: React.ReactNode;
}> = ({ id, marcado, aoMudar, rotulo, dica }) => (
  <label htmlFor={id} className="flex items-start gap-3 cursor-pointer py-1">
    <input
      id={id}
      type="checkbox"
      checked={marcado}
      onChange={(e) => aoMudar(e.target.checked)}
      className="mt-0.5 h-5 w-5 shrink-0 accent-tinta cursor-pointer"
    />
    <span className="min-w-0">
      <span className="block text-sm font-semibold">{rotulo}</span>
      {dica ? <span className="block text-xs text-texto2 mt-0.5">{dica}</span> : null}
    </span>
  </label>
);

/** Botões segmentados (abas pequenas). */
export function Segmentos<T extends string>({
  valor,
  aoMudar,
  opcoes,
  rotuloAria,
}: {
  valor: T;
  aoMudar: (v: T) => void;
  opcoes: { valor: T; rotulo: React.ReactNode }[];
  rotuloAria: string;
}) {
  return (
    <div role="tablist" aria-label={rotuloAria} className="inline-flex flex-wrap rounded-xl bg-fundo p-1 gap-1">
      {opcoes.map((o) => (
        <button
          key={o.valor}
          type="button"
          role="tab"
          aria-selected={valor === o.valor}
          onClick={() => aoMudar(o.valor)}
          className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition cursor-pointer ${
            valor === o.valor ? 'bg-white shadow-sm text-tinta' : 'text-texto2 hover:text-tinta'
          }`}
        >
          {o.rotulo}
        </button>
      ))}
    </div>
  );
}

/** Seção sanfonada (abre só quando a fatura tem o item). */
export const Sanfona: React.FC<{
  id: string;
  letra: string;
  titulo: string;
  resumo: React.ReactNode;
  aberta: boolean;
  aoAlternar: () => void;
  children: React.ReactNode;
}> = ({ id, letra, titulo, resumo, aberta, aoAlternar, children }) => (
  <div className="border border-borda rounded-xl overflow-hidden">
    <button
      type="button"
      aria-expanded={aberta}
      aria-controls={`${id}-corpo`}
      onClick={aoAlternar}
      className="w-full flex items-center gap-3 px-4 py-3.5 text-left cursor-pointer hover:bg-fundo/60"
    >
      <span className="w-8 h-8 shrink-0 rounded-lg bg-fundo flex items-center justify-center text-sm font-bold">
        {letra}
      </span>
      <span className="min-w-0 flex-1">
        <span className="block font-bold">{titulo}</span>
        <span className="block text-xs text-texto2 truncate">{resumo}</span>
      </span>
      <span aria-hidden className={`transition-transform ${aberta ? 'rotate-180' : ''}`}>
        ⌄
      </span>
    </button>
    {aberta ? (
      <div id={`${id}-corpo`} className="border-t border-borda2 px-4 sm:pl-16 py-4 space-y-4">
        {children}
      </div>
    ) : null}
  </div>
);

export const Kpi: React.FC<{ rotulo: string; valor: React.ReactNode; sub?: React.ReactNode; cor?: string }> = ({
  rotulo,
  valor,
  sub,
  cor,
}) => (
  <div className="bg-white border border-borda rounded-xl px-4 py-3 min-w-0">
    <div className="tela-rotulo">{rotulo}</div>
    <div className="num text-xl sm:text-2xl font-semibold mt-1.5 break-words leading-none" style={cor ? { color: cor } : undefined}>
      {valor}
    </div>
    {sub ? <div className="tela-apoio mt-1.5">{sub}</div> : null}
  </div>
);

export const Progresso: React.FC<{ feitas: number; total: number; rotulo: string }> = ({ feitas, total, rotulo }) => (
  <div className="rounded-xl border border-borda bg-white px-4 py-3" role="status" aria-live="polite">
    <div className="flex justify-between text-sm mb-2">
      <span>{rotulo}</span>
      <span className="num text-texto2">
        {feitas}/{total}
      </span>
    </div>
    <div className="h-2 rounded-full bg-borda2 overflow-hidden">
      <div
        className="h-full bg-acento transition-all"
        style={{ width: `${total > 0 ? Math.round((feitas / total) * 100) : 0}%` }}
      />
    </div>
  </div>
);

export const Botao: React.FC<
  React.ButtonHTMLAttributes<HTMLButtonElement> & { variante?: 'primario' | 'escuro' | 'claro' }
> = ({ variante = 'claro', className = '', ...props }) => {
  const v =
    variante === 'primario'
      ? 'bg-acento hover:brightness-95 text-tinta'
      : variante === 'escuro'
        ? 'bg-tinta hover:brightness-125 text-white'
        : 'bg-white border border-borda hover:bg-fundo text-tinta';
  return (
    <button
      type="button"
      {...props}
      className={`inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 font-bold text-sm transition cursor-pointer disabled:opacity-60 disabled:cursor-wait ${v} ${className}`}
    />
  );
};
