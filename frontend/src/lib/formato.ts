/** Formatação pt-BR e cores fixas (mesma cor = mesma modalidade em todos os gráficos). */

/**
 * Paleta em dois grupos, para não competirem:
 * - MARCA: tinta/texto2/fundo/borda/acento (interface, não significa dado);
 * - DADO: te/fio/demanda/tributos/outros (composição do custo) e
 *   verde/azul (modalidade), acl (mercado livre), alerta (erro/ultrapassagem).
 *
 * Nenhuma cor de dado repete a da marca: antes `acl` e `te` eram o mesmo
 * `#D99A00` do `acento`, e TE/ACL ficavam indistinguíveis no gráfico.
 */
export const COR = {
  // marca / interface
  tinta: '#13232E',
  texto2: '#5B6B76',
  fundo: '#F3F5F7',
  borda: '#DCE3E8',
  borda2: '#EDF1F4',
  acento: '#F2A900',
  // dado
  verde: '#1F8A4C',
  azul: '#2B59C3',
  acl: '#51607A',
  alerta: '#C2410C',
  te: '#B47600',
  demanda: '#8A5CC2',
  fio: '#2A9DB0',
  tributos: '#9AA5AE',
  outros: '#C9D2D8',
} as const;

/** Cores da composição do custo, na ordem em que aparecem nos gráficos. */
export const FATIAS_CUSTO = [
  { chave: 'TE', nome: 'Energia (TE)', cor: COR.te },
  { chave: 'Fio', nome: 'Fio (TUSD energia)', cor: COR.fio },
  { chave: 'Demanda', nome: 'Demanda (TUSD)', cor: COR.demanda },
  { chave: 'Tributos', nome: 'Tributos', cor: COR.tributos },
  { chave: 'Outros', nome: 'Outros', cor: COR.outros },
] as const;

/** Cor por modalidade (nome da API). */
export const COR_MODALIDADE: Record<string, string> = {
  Verde: COR.verde,
  Azul: COR.azul,
  'Optante B': '#7A8792',
  Branca: '#7A8792',
  'Convencional Monômia': '#7A8792',
};

export const corModalidade = (m: string): string => COR_MODALIDADE[m] ?? COR.texto2;

const nf = (min: number, max: number) =>
  new Intl.NumberFormat('pt-BR', { minimumFractionDigits: min, maximumFractionDigits: max });

/** R$ 1.234,56 */
export function brl(v: number, casas = 2): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  }).format(v);
}

/** 1.234,5 com casas fixas. */
export function numero(v: number, casas = 0): string {
  return nf(casas, casas).format(v);
}

/** Valor compacto para eixos: 623,0k / 1,2 mi. */
export function compacto(v: number): string {
  const a = Math.abs(v);
  if (a >= 1e6) return `${nf(1, 1).format(v / 1e6)} mi`;
  if (a >= 1e3) return `${nf(0, 1).format(v / 1e3)}k`;
  return nf(0, 0).format(v);
}

/** R$ 12,4 mil (títulos). */
export function brlCurto(v: number): string {
  const a = Math.abs(v);
  if (a >= 1e6) return `R$ ${nf(1, 1).format(v / 1e6)} mi`;
  if (a >= 1e4) return `R$ ${nf(1, 1).format(v / 1e3)} mil`;
  return brl(v, 2);
}

export function pct(v: number, casas = 1): string {
  return `${nf(casas, casas).format(v * 100)}%`;
}

/** Tarifa: até 6 casas, como a fatura imprime. */
export function tarifa(v: number): string {
  return nf(2, 6).format(v);
}
