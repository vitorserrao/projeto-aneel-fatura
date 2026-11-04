import React from 'react';
import { Bolt } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="sticky top-0 w-full z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.03)] no-print">
      <div className="max-w-6xl mx-auto h-16 px-4 sm:px-6 flex items-center justify-between gap-4">
        {/* Logo ACR × ACL */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-amber-400 to-yellow-400 flex items-center justify-center text-slate-950 font-black shadow-xs ring-2 ring-amber-300/50 shrink-0">
            <Bolt className="w-5 h-5 text-slate-950 fill-slate-950" />
          </div>
          <div className="flex flex-col">
            <span className="font-display text-lg sm:text-xl font-bold tracking-tight text-slate-950 leading-none">
              ACR <span className="text-amber-600 font-extrabold">×</span> ACL
            </span>
            <span className="text-[11px] uppercase font-semibold tracking-wider text-slate-500 mt-1">
              Simulador &amp; Reenquadramento Tarifário
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
