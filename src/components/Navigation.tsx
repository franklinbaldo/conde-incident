import React from 'react';
import { hashForLabTab } from '../lib/labRoutes';
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

export type TabId =
  | 'research'
  | 'summary'
  | 'map'
  | 'inverse'
  | 'triangulation'
  | 'sensitivity'
  | 'montecarlo'
  | 'tles'
  | 'documents'
  | 'python';

interface NavigationProps {
  activeTab: TabId | null;
  setActiveTab: (tab: TabId) => void;
  lang: 'pt' | 'en';
  setLang: (lang: 'pt' | 'en') => void;
  onOpenPython: () => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  activeTab,
  setActiveTab,
  lang,
  setLang,
  onOpenPython,
}) => {
  const storiesHref = `${import.meta.env.BASE_URL.replace(/lab\/$/, '')}stories/`;
  const tabs = [
    {
      id: 'research' as TabId,
      labelPt: 'Evidências & restrições',
      labelEn: 'Evidence & constraints',
      icon: FileText,
    },
    {
      id: 'summary' as TabId,
      labelPt: 'Síntese & limites',
      labelEn: 'Summary & limits',
      icon: ShieldCheck,
    },
    {
      id: 'map' as TabId,
      labelPt: 'Mapa exploratório',
      labelEn: 'Exploratory map',
      icon: Compass,
      badge: '2D / 3D',
    },
    {
      id: 'inverse' as TabId,
      labelPt: 'Teste inverso (hipótese)',
      labelEn: 'Inverse test (hypothesis)',
      icon: MapPin,
      badge: '08/11/1963',
    },
    {
      id: 'triangulation' as TabId,
      labelPt: 'Triangulação (527-529)',
      labelEn: 'Triangulation (527-529)',
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
      labelPt: 'Monte Carlo & Falsificação',
      labelEn: 'Monte Carlo & Falsification',
      icon: Activity,
    },
    {
      id: 'tles' as TabId,
      labelPt: 'Auditoria de TLEs',
      labelEn: 'TLEs & Checksums',
      icon: Binary,
    },
    {
      id: 'documents' as TabId,
      labelPt: 'Arquivo & Epistemologia',
      labelEn: 'Archive & Epistemology',
      icon: FileText,
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
            Missão NRO 7153 (Thor-Agena D / OPS 0180)
          </span>
          <span className="text-zinc-600 hidden sm:inline">|</span>
          <div className="flex items-center gap-1 text-amber-400/90 font-mono">
            <Calendar className="w-3.5 h-3.5" />
            <span>{lang === 'pt' ? 'Dia catalogado: 08/11/1963' : 'Catalogued day: 8 Nov 1963'}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Target Reference */}
          <div className="hidden md:flex items-center gap-1.5 px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 font-mono">
            <MapPin className="w-3 h-3 text-rose-400" />
            <span>{lang === 'pt' ? 'Sede aproximada de Conde: 11,81° S · 37,61° O' : 'Approximate Conde town center: 11.81° S · 37.61° W'}</span>
          </div>

          {/* Python Export Button */}
          <button
            onClick={onOpenPython}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 border border-zinc-700/80 text-zinc-300 hover:text-cyan-400 transition-colors font-mono cursor-pointer"
            title="Exportar código Python reprodutível"
          >
            <Code className="w-3.5 h-3.5 text-cyan-400" />
            <span>Python Script</span>
          </button>

          {/* Language Toggle */}
          <div role="group" aria-label={lang === 'pt' ? 'Idioma do laboratório' : 'Laboratory language'} className="flex items-center bg-zinc-900 rounded border border-zinc-800 p-0.5">
            <button
              onClick={() => setLang('pt')}
              aria-pressed={lang === 'pt'}
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                lang === 'pt' ? 'bg-cyan-600 text-white' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              PT-BR
            </button>
            <button
              onClick={() => setLang('en')}
              aria-pressed={lang === 'en'}
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
        <a href={storiesHref} className="flex items-center gap-2 px-3 py-2 rounded-md text-xs font-medium whitespace-nowrap text-cyan-300 hover:bg-zinc-900 border border-cyan-900/60"><FileText className="w-4 h-4"/> {lang === 'pt' ? 'Caderno de histórias' : 'Investigative journal'}</a>
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <a
              key={tab.id}
              href={hashForLabTab(tab.id)}
              onClick={() => setActiveTab(tab.id)}
              aria-current={isActive ? 'page' : undefined}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-xs font-medium whitespace-nowrap transition-all cursor-pointer ${
                isActive
                  ? 'bg-zinc-800 text-cyan-300 border border-cyan-800/60 shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/80 border border-transparent'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-zinc-500'}`} />
              <span>{lang === 'pt' ? tab.labelPt : tab.labelEn}</span>
              {tab.badge && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded font-mono font-semibold ${
                    isActive
                      ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                      : 'bg-zinc-900 text-zinc-400 border border-zinc-800'
                  }`}
                >
                  {tab.badge}
                </span>
              )}
            </a>
          );
        })}
      </nav>
    </header>
  );
};
