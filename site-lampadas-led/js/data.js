/* =====================================================================
   RECUPERAÇÃO DE LÂMPADAS LED — DADOS DO PROJETO
   ---------------------------------------------------------------------
   Este é o ÚNICO arquivo de dados do site. Para atualizar números,
   pontos de coleta, metodologia ou dados do painel, edite somente aqui.

   Regra de verdade: nenhum dado foi inventado. Os valores em 0 são
   exibidos no site com o selo "Dado a inserir" até a equipe do projeto
   fornecer os números reais.
   ===================================================================== */

const PROJECT_DATA = {

  /* ── Contadores de impacto (seção "Nosso impacto") ───────────────── */
  counters: [
    { id: "lampsCollected",  icon: "💡", label: "Lâmpadas coletadas",                       value: 0, suffix: "",     decimals: 0 },
    { id: "lampsRecovered",  icon: "🔧", label: "Lâmpadas recuperadas",                     value: 0, suffix: "",     decimals: 0 },
    { id: "lampsReused",     icon: "♻️", label: "Lâmpadas que ganharam uma nova vida",      value: 0, suffix: "",     decimals: 0 },
    { id: "wasteAvoidedKg",  icon: "🗑️", label: "Resíduos potencialmente evitados",         value: 0, suffix: " kg",  decimals: 0 },
    { id: "energyImpactKwh", icon: "⚡", label: "Energia associada à extensão da vida útil", value: 0, suffix: " kWh", decimals: 0 }
  ],

  /* ── Fluxo do projeto (timeline "Como funciona") ────────────────────
     Textos baseados no material oficial (Folder.pptx) e na proposta
     do projeto de extensão. */
  timeline: [
    { n: "01", title: "Coleta",       desc: "A comunidade entrega lâmpadas LED que não funcionam mais, por doação ou descarte consciente." },
    { n: "02", title: "Triagem",      desc: "As lâmpadas recebidas são avaliadas e classificadas quanto à viabilidade técnica do reparo." },
    { n: "03", title: "Diagnóstico",  desc: "São identificados os componentes ou partes responsáveis pela falha: LED queimado, driver ou conexões." },
    { n: "04", title: "Reparo",       desc: "Quando tecnicamente viável, são realizados os procedimentos de recuperação, como a substituição do componente danificado (LEDs)." },
    { n: "05", title: "Teste",        desc: "A lâmpada recuperada passa por testes elétricos e de segurança." },
    { n: "06", title: "Recuperação",  desc: "A lâmpada volta a ter utilidade: é identificada e embalada para entrega ao usuário final." },
    { n: "07", title: "Destinação",   desc: "As lâmpadas que não podem ser recuperadas recebem a destinação adequada, evitando o descarte incorreto." }
  ],

  /* ── Pontos de coleta ──────────────────────────────────────────────
     Ainda não há pontos cadastrados nos materiais do projeto.
     Quando existirem, adicione objetos neste formato:
     { name: "...", institution: "...", address: "...", hours: "...",
       mapUrl: "https://...", note: "" }                                */
  collectionPoints: [],

  /* ── Metodologia (modal "Ver metodologia") ───────────────────────── */
  methodology: {
    title: "Metodologia de cálculo do impacto",
    intro: "Os números publicados no site seguem a metodologia definida pelo projeto. Cada indicador declara sua origem e, quando o valor é uma estimativa calculada, isso é indicado claramente no site.",
    items: [
      { k: "Lâmpadas coletadas",        v: "Quantidade registrada pelo projeto no recebimento de cada lâmpada. [DADO A INSERIR: critérios de registro]" },
      { k: "Lâmpadas recuperadas",      v: "Quantidade efetivamente reparada e aprovada nos testes elétricos e de segurança. [DADO A INSERIR: critérios de aprovação]" },
      { k: "Lâmpadas destinadas corretamente", v: "Quantidade de lâmpadas sem viabilidade de reparo encaminhadas à destinação adequada. [DADO A INSERIR: fluxo de destinação]" },
      { k: "Resíduos potencialmente evitados", v: "Estimativa calculada com base na massa média das lâmpadas recuperadas, conforme metodologia a ser definida pelo projeto. [DADO A INSERIR: massa média e fórmula]" },
      { k: "Energia associada à extensão da vida útil", v: "Estimativa calculada a partir da potência típica e das horas de uso estimadas para cada lâmpada recuperada. [DADO A INSERIR: premissas de uso e fórmula]" }
    ],
    disclaimer: "Nenhuma estimativa é apresentada como dado medido. Os valores reais serão publicados assim que a equipe do projeto registrar e validar as informações."
  },

  /* ── Painel do projeto — dados de EXEMPLO (demonstrativo) ──────────
     Não são dados reais. Serão substituídos pelos registros do projeto. */
  panel: {
    demo: true,
    demoLabel: "Dados de exemplo — demonstrativo até o registro dos dados reais do projeto",
    years: [2025, 2026],
    months: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
    locals: ["Ponto de coleta A", "Ponto de coleta B", "Ponto de coleta C"],
    situations: ["Recuperada", "Em análise", "Sem recuperação"],
    /* Linhas geradas de forma determinística (sem aleatoriedade). */
    rows: (function () {
      const rows = [];
      [2025, 2026].forEach(function (year) {
        for (let m = 0; m < 12; m++) {
          const base = 5 + m + (year === 2026 ? 10 : 0);
          rows.push({ year, month: m, local: 0, situation: "Recuperada",      qty: Math.round(base * 0.55) });
          rows.push({ year, month: m, local: 0, situation: "Em análise",      qty: Math.max(1, Math.round(base * 0.25)) });
          rows.push({ year, month: m, local: 0, situation: "Sem recuperação", qty: Math.max(0, Math.round(base * 0.15)) });
          rows.push({ year, month: m, local: 1, situation: "Recuperada",      qty: Math.round(base * 0.32) });
          rows.push({ year, month: m, local: 1, situation: "Em análise",      qty: Math.max(1, Math.round(base * 0.14)) });
          rows.push({ year, month: m, local: 1, situation: "Sem recuperação", qty: Math.max(0, Math.round(base * 0.08)) });
          rows.push({ year, month: m, local: 2, situation: "Recuperada",      qty: Math.round(base * 0.20) });
          rows.push({ year, month: m, local: 2, situation: "Em análise",      qty: Math.max(0, Math.round(base * 0.10)) });
          rows.push({ year, month: m, local: 2, situation: "Sem recuperação", qty: Math.max(0, Math.round(base * 0.06)) });
        }
      });
      return rows;
    })()
  },

  /* ── Contato e links institucionais ──────────────────────────────── */
  links: {
    padlet: "https://padlet.com/rafaelg09/painel-interativo-do-curso-de-tecnologia-em-sistemas-de-ener-i8drrg0xxs3nr8mk",
    contactEmail: "[DADO A INSERIR]",
    contactPhone: "[DADO A INSERIR]"
  },

  institutional: {
    project: "Recuperação de Lâmpadas LED",
    extension: "Projeto de Extensão II",
    course: "Tecnologia em Sistemas de Energia",
    institution: "Instituto Federal de Santa Catarina (IFSC) — Campus Florianópolis",
    teamTitle: "Equipe — autoria do guia “Reparo de Lâmpadas LED”",
    team: [
      "Prof. Gustavo Cardoso Orsi",
      "Thiago Francisco Lewis",
      "Vinicius França de Oliveira e Almeida",
      "Gustavo Bairrão Machado"
    ],
    warning: "As lâmpadas recuperadas não possuem garantia e não devem ser comercializadas. O objetivo deste projeto é exclusivamente educativo e ambiental."
  }
};
