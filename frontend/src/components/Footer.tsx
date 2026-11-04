import React, { useState } from 'react';
import { BookOpen, Calculator, HelpCircle, X, Shield } from 'lucide-react';

export const Footer: React.FC = () => {
  const [modalType, setModalType] = useState<'normas' | 'metodologia' | 'suporte' | null>(null);

  return (
    <>
      <footer className="w-full bg-white border-t border-slate-200/80 py-5 mt-auto no-print">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span>© 2026 ACR × ACL • Simulador &amp; Reenquadramento Tarifário</span>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setModalType('normas')}
              className="hover:text-amber-700 transition-colors cursor-pointer"
            >
              Normas ANEEL
            </button>
            <button
              onClick={() => setModalType('metodologia')}
              className="hover:text-amber-700 transition-colors cursor-pointer"
            >
              Metodologia
            </button>
            <button
              onClick={() => setModalType('suporte')}
              className="hover:text-amber-700 transition-colors cursor-pointer"
            >
              Suporte Técnico
            </button>
          </div>
        </div>
      </footer>

      {/* Modal Institucional */}
      {modalType && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                {modalType === 'normas' && <BookOpen className="w-5 h-5 text-amber-600" />}
                {modalType === 'metodologia' && <Calculator className="w-5 h-5 text-amber-600" />}
                {modalType === 'suporte' && <HelpCircle className="w-5 h-5 text-amber-600" />}
                <h3 className="text-base font-bold text-slate-900">
                  {modalType === 'normas' && 'Normas Regulatórias ANEEL'}
                  {modalType === 'metodologia' && 'Metodologia de Auditoria Tarifária'}
                  {modalType === 'suporte' && 'Suporte Técnico e Especialistas'}
                </h3>
              </div>
              <button
                onClick={() => setModalType(null)}
                className="w-8 h-8 rounded-lg text-slate-400 hover:text-slate-700 flex items-center justify-center cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="text-xs sm:text-sm text-slate-600 space-y-3 leading-relaxed">
              {modalType === 'normas' && (
                <>
                  <p>
                    O simulador ACR × ACL opera estritamente em conformidade com as resoluções
                    homologadas da <strong>Agência Nacional de Energia Elétrica (ANEEL)</strong>,
                    em especial a <strong>Resolução Normativa nº 1.000/2021</strong>, que estabelece
                    as Regras de Prestação do Serviço Público de Distribuição de Energia Elétrica.
                  </p>
                  <p>
                    Consumidores do <strong>Grupo A (Alta e Média Tensão)</strong> têm o direito de
                    solicitar a qualquer momento a alteração entre modalidades tarifárias (Azul,
                    Verde ou Convencional) sem custos pela concessionária, respeitado o limite de
                    permanência regulatório.
                  </p>
                </>
              )}

              {modalType === 'metodologia' && (
                <>
                  <p>
                    A modelagem computacional separa os custos em <strong>TE (Tarifa de Energia)</strong>,{' '}
                    <strong>TUSD (Tarifa de Uso do Sistema de Distribuição)</strong> e encargos
                    setoriais, aplicando os gross-ups tributários de <strong>ICMS, PIS e COFINS</strong> calculados
                    por dentro.
                  </p>
                  <p>
                    A Tarifa Horária Verde unifica a cobrança de demanda de potência, tornando-se
                    vantajosa para consumidores cujo consumo diurno ou noturno fora de ponta supera
                    75% do volume global.
                  </p>
                </>
              )}

              {modalType === 'suporte' && (
                <>
                  <p>
                    Nossa equipe de engenheiros eletricistas e especialistas regulatórios está à
                    disposição para auditorias aprofundadas, adequação de contratos de demanda e
                    estudos de migração para o Mercado Livre de Energia (ACL).
                  </p>
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
                    <div>
                      <strong>E-mail Técnico:</strong> suporte@acracl.com.br
                    </div>
                    <div>
                      <strong>Plantão Regulatório:</strong> 0800 948 2000
                    </div>
                    <div>
                      <strong>Horário:</strong> Segunda a Sexta, das 8h às 18h (Horário de Brasília)
                    </div>
                  </div>
                </>
              )}
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setModalType(null)}
                className="px-4 py-2 rounded-xl bg-slate-900 text-white text-xs font-bold hover:bg-slate-800 transition-colors cursor-pointer"
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
