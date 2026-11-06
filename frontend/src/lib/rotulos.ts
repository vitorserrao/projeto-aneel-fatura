/**
 * Mapa único: descrição da linha da API → rótulo legível, grupo e unidade.
 *
 * As descrições vêm do motor (core/motor_calculo.py):
 *   "{TE|TUSD} {ENERGIA|DEMANDA} {posto}[ ISENTA ICMS][ (mês anterior|mês atual)][ (com tributos)]"
 * e linhas avulsas (ultrapassagem, reativos, bandeira, CIP, outros).
 * Nada aqui converte tarifa: só nomeia e diz a unidade da QUANTIDADE que a
 * API devolve (energia em MWh quando a tarifa é R$/MWh, demanda em kW).
 */

export type GrupoLinha = 'Energia' | 'Demanda' | 'Reativos' | 'Bandeira' | 'Outros';

/** Componente para a composição do custo (cores fixas do protótipo). */
export type ComponenteCusto = 'TE' | 'Demanda' | 'Fio' | 'Outros';

export interface RotuloLinha {
  rotulo: string;
  grupo: GrupoLinha;
  /** Unidade da quantidade (MWh, kW, …) ou '' para valores fixos em R$. */
  unidade: string;
  componente: ComponenteCusto;
  /** Linha isenta de ICMS (parcela de demanda). */
  isentaIcms: boolean;
  /** Descrição da API sem o sufixo " (com tributos)" — chave para casar linhas. */
  chave: string;
}

const SUFIXO_TRIBUTOS = ' (com tributos)';

/** Descrição sem o sufixo de tributos (casa a linha com/sem tributos). */
export function chaveLinha(descricao: string): string {
  return descricao.endsWith(SUFIXO_TRIBUTOS) ? descricao.slice(0, -SUFIXO_TRIBUTOS.length) : descricao;
}

const POSTO: Record<string, string> = {
  PONTA: 'ponta',
  'FORA PONTA': 'fora de ponta',
  INTERMEDIARIO: 'intermediário',
};

function nomePosto(posto: string): string {
  const p = posto.trim().toUpperCase();
  if (POSTO[p]) return POSTO[p];
  return posto.trim().toLowerCase();
}

const RE_TARIFA =
  /^(TE|TUSD) (ENERGIA|DEMANDA) (.+?)( ISENTA ICMS)?( \((mês anterior|mês atual)\))?$/;

/**
 * Rótulo da linha. `modalidade` é o nome da API ("Verde", "Azul", "Optante B"…):
 * na Verde a demanda é única ("Demanda (única)"), não "TUSD DEMANDA PONTA".
 */
export function rotuloLinha(descricao: string, modalidade: string, categoria = ''): RotuloLinha {
  const chave = chaveLinha(descricao);
  const verde = modalidade.trim().toLowerCase() === 'verde';
  const m = RE_TARIFA.exec(chave);
  if (m) {
    const [, comp, grandeza, posto, isenta, , rateio] = m;
    const sufixoRateio = rateio ? ` — ${rateio}` : '';
    if (grandeza === 'DEMANDA') {
      const base = verde ? 'Demanda (única)' : `Demanda ${nomePosto(posto)}`;
      const rotulo = isenta
        ? verde
          ? 'Demanda isenta de ICMS'
          : `${base} — isenta de ICMS`
        : base;
      return {
        rotulo: rotulo + sufixoRateio,
        grupo: 'Demanda',
        unidade: 'kW',
        componente: 'Demanda',
        isentaIcms: Boolean(isenta),
        chave,
      };
    }
    const nome = comp === 'TE' ? 'Energia (TE)' : 'Uso do sistema (TUSD)';
    return {
      rotulo: `${nome} ${nomePosto(posto)}${sufixoRateio}`,
      grupo: 'Energia',
      unidade: 'MWh',
      componente: comp === 'TE' ? 'TE' : 'Fio',
      isentaIcms: false,
      chave,
    };
  }
  const c = categoria.toUpperCase();
  if (c === 'ULTRAPASSAGEM' || chave.startsWith('Ultrapassagem')) {
    const posto = chave.replace('Ultrapassagem de demanda', '').trim();
    return {
      rotulo: posto ? `Ultrapassagem de demanda ${nomePosto(posto)}` : 'Ultrapassagem de demanda',
      grupo: 'Demanda',
      unidade: 'kW',
      componente: 'Demanda',
      isentaIcms: false,
      chave,
    };
  }
  if (c === 'REATIVOS' || /reativ/i.test(chave)) {
    const energia = /energia|consumo/i.test(chave);
    return {
      rotulo: chave,
      grupo: 'Reativos',
      unidade: energia ? 'MVArh' : 'kVAr',
      componente: 'Outros',
      isentaIcms: false,
      chave,
    };
  }
  if (c === 'BANDEIRA' || /bandeira/i.test(chave)) {
    return { rotulo: 'Adicional de bandeira', grupo: 'Bandeira', unidade: 'kWh', componente: 'Outros', isentaIcms: false, chave };
  }
  if (/CIP|COSIP/i.test(chave)) {
    return { rotulo: 'Iluminação pública (CIP/COSIP)', grupo: 'Outros', unidade: '', componente: 'Outros', isentaIcms: false, chave };
  }
  return { rotulo: chave, grupo: 'Outros', unidade: '', componente: 'Outros', isentaIcms: false, chave };
}

/** Nome da modalidade para exibição. */
export const NOME_MODALIDADE: Record<string, string> = {
  Verde: 'Horária Verde',
  Azul: 'Horária Azul',
  'Optante B': 'Optante Grupo B',
  Branca: 'Branca',
  'Convencional Monômia': 'Convencional',
};

export const nomeModalidade = (m: string): string => NOME_MODALIDADE[m] ?? m;
