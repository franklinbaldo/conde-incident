import React from 'react';
import { tabHref, type LabTab } from '../lib/tabRoutes';
import {
  Satellite,
  Compass,
  Layers,
  Activity,
  Wind,
  FileText,
  Code,
  ShieldCheck,
  MapPin,
  Calendar,
  Binary,
} from 'lucide-react';

export type TabId = LabTab;

interface NavigationProps {
  activeTab: TabId;
  lang: 'pt' | 'en';
  setLang: (lang: 'pt' | 'en') => void;
  onOpenPython: () => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  activeTab,
  lang,
  setLang,
  onOpenPython,
}) => {
  const tabs = [
    {
      id: 'summary' as TabId,
      labelPt: 'Síntese e limites',
      labelEn: 'Summary & limits',
      icon: ShieldCheck,
      badgePt: 'Fontes', badgeEn: 'Sources',
    },
    {
      id: 'map' as TabId,
      labelPt: 'Rastreamento & Mapa',
      labelEn: 'Tracking & Map',
      icon: Compass,
      badgePt: '2D / 3D', badgeEn: '2D / 3D',
    },
    {
      id: 'inverse' as TabId,
      labelPt: 'Cenários inversos',
      labelEn: 'Inverse scenarios',
      icon: MapPin,
      badgePt: '08/11/1963', badgeEn: '08 Nov 1963',
    },
    {
      id: 'triangulation' as TabId,
      labelPt: 'Comparação (527–529)',
      labelEn: 'Comparison (527–529)',
      icon: Layers,
    },
    {
      id: 'sensitivity' as TabId,
      labelPt: 'Arrasto & Termosfera',
      labelEn: 'Drag & Thermosphere',
      icon: Wind,
    },
    {
      id: 'montecarlo' as TabId,
      labelPt: 'Amostragem exploratória',
      labelEn: 'Exploratory sampling',
      icon: Activity,
      badgePt: 'Sintético', badgeEn: 'Synthetic',
    },
    {
      id: 'tles' as TabId,
      labelPt: 'Auditoria de TLEs',
      labelEn: 'TLEs & Checksums',
      icon: Binary,
      badgePt: 'Sintaxe ≠ origem', badgeEn: 'Syntax ≠ origin',
    },
    {
      id: 'documents' as TabId,
      labelPt: 'Arquivo e proveniência',
      labelEn: 'Archive & provenance',
      icon: FileText,
      badgePt: 'Documental', badgeEn: 'Documents',
    },
  ];

  return (
    <header className="border-b border-zinc-800 bg-zinc-950/90 backdrop-blur sticky top-0 z-50">
      {/* Top Banner */}
      <div className="max-w-7xl mx-auto px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 text-xs border-b border-zinc-900">
        <div className="flex items-center gap-2 text-zinc-300">
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/80 text-cyan-300 font-mono font-medium">
            <Satellite className="w-3.5 h-3.5 animate-pulse" />
            <span>NORAD 528 (1963-003B)</span>
          </div>
          <span className="text-zinc-600">|</span>
          <span className="text-zinc-400 hidden sm:inline">
            {lang === 'pt' ? 'Missão NRO 7153 (Thor-Agena D / OPS 0180)' : 'NRO mission 7153 (Thor-Agena D / OPS 0180)'}
          </span>
          <span className="text-zinc-600 hidden sm:inline">|</span>
          <div className="flex items-center gap-1 text-amber-400/90 font-mono">
            <Calendar className="w-3.5 h-3.5" />
            <span>{lang === 'pt' ? 'NASA: dia catalogado 08/11/1963' : 'NASA: catalogued day 08 Nov 1963'}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Python Export Button */}
          <button
            onClick={onOpenPython}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 border border-zinc-700/80 text-zinc-300 hover:text-cyan-400 transition-colors font-mono cursor-pointer"
            title={lang === 'pt' ? 'Exportar código Python reprodutível' : 'Export reproducible Python code'}
          >
            <Code className="w-3.5 h-3.5 text-cyan-400" />
            <span>{lang === 'pt' ? 'Script Python' : 'Python Script'}</span>
          </button>

          {/* Language Toggle */}
          <div className="flex items-center bg-zinc-900 rounded border border-zinc-800 p-0.5">
            <button
              onClick={() => setLang('pt')}
              type="button"
              aria-pressed={lang === 'pt'}
              aria-label="Português (Brasil)"
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                lang === 'pt' ? 'bg-cyan-600 text-white' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              PT-BR
            </button>
            <button
              onClick={() => setLang('en')}
              type="button"
              aria-pressed={lang === 'en'}
              aria-label="English"
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                lang === 'en' ? 'bg-cyan-600 text-white' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              EN
            </button>
          </div>
        </div>
      </div>

      {/* Main Navigation Tabs */}
      <nav aria-label={lang === 'pt' ? 'Seções do laboratório' : 'Laboratory sections'} className="max-w-7xl mx-auto px-4 flex space-x-1 overflow-x-auto py-1.5 scrollbar-thin">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <a
              key={tab.id}
              href={tabHref(tab.id)}
              aria-current={isActive ? 'page' : undefined}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-xs font-medium whitespace-nowrap transition-all cursor-pointer ${
                isActive
                  ? 'bg-zinc-800 text-cyan-300 border border-cyan-800/60 shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/80 border border-transparent'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-zinc-500'}`} />
              <span>{lang === 'pt' ? tab.labelPt : tab.labelEn}</span>
              {tab.badgePt && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded font-mono font-semibold ${
                    isActive
                      ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                      : 'bg-zinc-900 text-zinc-400 border border-zinc-800'
                  }`}
                >
                  {lang === 'pt' ? tab.badgePt : tab.badgeEn}
                </span>
              )}
            </a>
          );
        })}
      </nav>
    </header>
  );
};
