import React from 'react';
import { tabHref, type LabTab } from '../lib/tabRoutes';
import { EDITORIAL_ROUTES } from '../lib/editorialRoutes';
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
  ArrowLeft,
  ChevronDown,
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
  const navRef = React.useRef<HTMLDivElement>(null);
  const mobileMenuRef = React.useRef<HTMLDetailsElement>(null);
  const editorialContext = EDITORIAL_ROUTES[activeTab];

  // On narrow screens the tab strip scrolls horizontally. Deep links and
  // Back/Forward must reveal the active tab without scrolling the page itself.
  React.useLayoutEffect(() => {
    const revealActiveTab = () => {
      const nav = navRef.current;
      const active = nav?.querySelector<HTMLElement>('[aria-current="page"]');
      if (!nav || !active || !nav.offsetWidth) return;
      const strip = nav.getBoundingClientRect();
      const tab = active.getBoundingClientRect();
      const left = strip.left + 16;
      const right = strip.right - 16;
      if (tab.left < left) nav.scrollLeft -= left - tab.left;
      else if (tab.right > right) nav.scrollLeft += tab.right - right;
    };
    revealActiveTab();
    window.addEventListener('resize', revealActiveTab);
    return () => window.removeEventListener('resize', revealActiveTab);
  }, [activeTab, lang]);

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

  const currentTab = tabs.find(tab => tab.id === activeTab);

  // A hash route is a distinct destination: announce it in browser tabs,
  // history entries and assistive technology, in the selected language.
  React.useEffect(() => {
    const section = lang === 'pt' ? currentTab?.labelPt : currentTab?.labelEn;
    if (!section) return;
    document.title = `${section} | NORAD 528 · ${lang === 'pt' ? 'Caso Conde (1963)' : 'Conde case (1963)'}`;
  }, [activeTab, lang]);


  return (
    <header className="border-b border-zinc-800 bg-zinc-950/90 backdrop-blur md:sticky md:top-0 z-50">
      {/* Top Banner */}
      <div className="max-w-7xl mx-auto px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 text-xs border-b border-zinc-900">
        <div className="flex flex-wrap items-center gap-2 text-zinc-300">
          <a
            href={EDITORIAL_ROUTES.summary.href}
            aria-label={lang === 'pt' ? 'Voltar ao Caderno' : 'Back to the Notebook'}
            className="inline-flex shrink-0 items-center gap-1 rounded px-1 py-1 text-cyan-300 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300"
          >
            <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
            <span>{lang === 'pt' ? 'Caderno' : 'Notebook'}</span>
          </a>
          {activeTab !== 'summary' && (
            <>
              <a
                href={editorialContext.href}
                aria-label={lang === 'pt' ? 'Abrir no Caderno: ' + editorialContext.pt : 'Open in Notebook: ' + editorialContext.en}
                className="inline-flex min-w-0 max-w-full items-center break-words rounded px-1 py-1 text-cyan-300 underline underline-offset-2 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300"
              >
                {lang === 'pt' ? editorialContext.pt : editorialContext.en}
              </a>
            </>
          )}
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/80 text-cyan-300 font-mono font-medium">
            <Satellite className="w-3.5 h-3.5 animate-pulse" />
            <span>NORAD 528 (1963-003B)</span>
          </div>
          <span className="text-zinc-400 hidden sm:inline">
            {lang === 'pt' ? 'Missão NRO 7153 (Thor-Agena D / OPS 0180)' : 'NRO mission 7153 (Thor-Agena D / OPS 0180)'}
          </span>
          <div className="flex items-center gap-1 text-amber-400/90 font-mono">
            <Calendar className="w-3.5 h-3.5" />
            <span>{lang === 'pt' ? 'NASA: dia catalogado 08/11/1963' : 'NASA: catalogued day 08 Nov 1963'}</span>
          </div>
        </div>

        <div className="flex flex-wrap min-w-0 items-center gap-3">
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
              className={`min-h-8 min-w-12 px-2 py-1 rounded text-[11px] font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 ${
                lang === 'pt' ? 'bg-cyan-700 text-white' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              PT-BR
            </button>
            <button
              onClick={() => setLang('en')}
              type="button"
              aria-pressed={lang === 'en'}
              aria-label="English"
              className={`min-h-8 min-w-12 px-2 py-1 rounded text-[11px] font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 ${
                lang === 'en' ? 'bg-cyan-700 text-white' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              EN
            </button>
          </div>
        </div>
      </div>

      {/* Main Navigation Tabs */}
      <nav aria-label={lang === 'pt' ? 'Seções do laboratório' : 'Laboratory sections'} className="max-w-7xl mx-auto px-4 py-1.5">
        {/* A native, fully labelled list replaces the undiscoverable horizontal
            strip at mobile/reflow widths. Desktop retains the compact tabs. */}
        <details ref={mobileMenuRef} className="group md:hidden">
          <summary className="grid min-h-11 list-none cursor-pointer grid-cols-[minmax(0,1fr)_auto] items-center gap-x-1 gap-y-1 rounded-md border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 [&::-webkit-details-marker]:hidden focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
            <span className="min-w-0 break-words font-semibold">{lang === 'pt' ? 'Explorar 8 seções' : 'Explore 8 sections'}</span>
            <span className="col-span-2 min-w-0 break-words text-cyan-300">{lang === 'pt' ? currentTab?.labelPt : currentTab?.labelEn}</span>
            <ChevronDown className="col-start-2 row-start-1 h-4 w-4 shrink-0 justify-self-end transition-transform group-open:rotate-180" aria-hidden="true" />
          </summary>
          <div data-mobile-tabs className="hidden min-w-0 group-open:grid gap-1 pt-2 pb-1">
            {tabs.map(tab => {
              const isActive = activeTab === tab.id;
              const Icon = tab.icon;
              return (
                <a
                  key={tab.id}
                  href={tabHref(tab.id)}
                  aria-current={isActive ? 'page' : undefined}
                  onClick={() => {
                    const menu = mobileMenuRef.current;
                    if (menu) {
                      menu.open = false;
                      menu.querySelector<HTMLElement>('summary')?.focus();
                    }
                  }}
                  className={`flex min-h-11 min-w-0 items-center gap-3 rounded-md border px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 ${
                    isActive
                      ? 'border-cyan-800 bg-zinc-800 text-cyan-300'
                      : 'border-zinc-800 bg-zinc-950 text-zinc-200 hover:bg-zinc-800'
                  }`}
                >
                  <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <span className="min-w-0 break-words">{lang === 'pt' ? tab.labelPt : tab.labelEn}</span>
                </a>
              );
            })}
          </div>
        </details>
        <div ref={navRef} data-desktop-tabs className="hidden md:flex space-x-1 overflow-x-auto scrollbar-thin">
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
        </div>
      </nav>
      {/* Announce SPA route changes without moving keyboard focus or reading the entire main region. */}
      <p className="sr-only" role="status" aria-live="polite" aria-atomic="true">
        {lang === 'pt' ? 'Seção ativa: ' : 'Active section: '}
        {lang === 'pt' ? currentTab?.labelPt : currentTab?.labelEn}
      </p>
    </header>
  );
};
