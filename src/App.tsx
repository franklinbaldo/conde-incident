/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Navigation, type TabId } from './components/Navigation';
import { mapTimeHref, parseLabRoute, tabHref } from './lib/tabRoutes';
import { skipToMain } from './lib/skipToMain';
import { ExecutiveSummary } from './components/ExecutiveSummary';
import { OrbitalMap } from './components/OrbitalMap';
import { InversePassInspector } from './components/InversePassInspector';
import { TriangulationDashboard } from './components/TriangulationDashboard';
import { AtmosphereSensitivity } from './components/AtmosphereSensitivity';
import { MonteCarloVisualizer } from './components/MonteCarloVisualizer';
import { DocumentArchive } from './components/DocumentArchive';
import { TleAuditViewer } from './components/TleAuditViewer';
import { PythonScriptModal } from './components/PythonScriptModal';
import { Satellite, Shield, Globe, Terminal, ExternalLink } from 'lucide-react';

export default function App() {
  const [route, setRoute] = useState(() => parseLabRoute(window.location.hash));
  const activeTab = route.tab;
  const [lang, setLang] = useState<'pt' | 'en'>('pt');
  const [sharedTimeMs, setSharedTimeMs] = useState<number>(
    route.timeMs ?? new Date('1963-10-27T14:40:16.132Z').getTime()
  );
  const [isPythonModalOpen, setIsPythonModalOpen] = useState<boolean>(false);

  // Hash URLs are stable even after reload and follow native Back/Forward navigation.
  // Only already-shipped lab tabs are recognized. Unavailable SSG routes remain explicit.
  React.useEffect(() => {
    const handleHashChange = () => {
      const next = parseLabRoute(window.location.hash);
      setRoute(next);
      if (next.timeMs !== undefined) setSharedTimeMs(next.timeMs);
    };
    window.addEventListener('hashchange', handleHashChange);
    handleHashChange();
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  React.useEffect(() => {
    document.documentElement.lang = lang === 'pt' ? 'pt-BR' : 'en';
  }, [lang]);

  const navigateTab = (tab: TabId) => {
    const target = tabHref(tab);
    if (window.location.hash !== target) window.location.hash = target;
    setRoute(parseLabRoute(target));
  };

  // When a pass is selected in the Inverse Inspector, jump directly to Map at that time
  const handleSelectPassFromInverse = (timeMs: number) => {
    setSharedTimeMs(timeMs);
    const target = mapTimeHref(timeMs);
    if (window.location.hash !== target) window.location.hash = target;
    setRoute(parseLabRoute(target));
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-black">

      {/* A hash link would replace #/map with #main-content and reset the SPA route.
          Keep its href accessible, but focus <main> without changing navigation. */}
      <a
        href="#main-content"
        onClick={event => skipToMain(event, document)}
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-md focus:bg-cyan-300 focus:px-4 focus:py-2 focus:font-semibold focus:text-zinc-950 focus:outline focus:outline-2 focus:outline-offset-2 focus:outline-white"
      >
        {lang === 'pt' ? 'Pular para o conteúdo' : 'Skip to main content'}
      </a>

      {/* Top Header & Navigation */}
      <Navigation
        activeTab={activeTab}
        lang={lang}
        setLang={setLang}
        onOpenPython={() => setIsPythonModalOpen(true)}
      />

      {/* Main Content Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 focus:outline-none" id="main-content" tabIndex={-1}>
        {route.invalidHash !== null && (
          <p role="status" aria-live="polite" className="mb-5 rounded-md border border-amber-700 bg-amber-950/40 p-3 text-sm text-amber-100">
            {lang === 'pt'
              ? 'Seção não disponível neste laboratório. Exibindo a síntese; escolha uma aba existente.'
              : 'This section is not available in the laboratory. Showing the summary; choose an existing tab.'}
          </p>
        )}
        {activeTab === 'summary' && (
          <ExecutiveSummary
            lang={lang}
            onJumpToTab={navigateTab}
          />
        )}

        {activeTab === 'map' && (
          <OrbitalMap
            lang={lang}
            selectedTimeMs={sharedTimeMs}
            onTimeChange={(t) => setSharedTimeMs(t)}
          />
        )}

        {activeTab === 'inverse' && (
          <InversePassInspector
            lang={lang}
            onSelectPassTime={handleSelectPassFromInverse}
          />
        )}

        {activeTab === 'triangulation' && (
          <TriangulationDashboard lang={lang} />
        )}

        {activeTab === 'sensitivity' && (
          <AtmosphereSensitivity lang={lang} />
        )}

        {activeTab === 'montecarlo' && (
          <MonteCarloVisualizer lang={lang} />
        )}

        {activeTab === 'tles' && (
          <TleAuditViewer lang={lang} />
        )}

        {activeTab === 'documents' && (
          <DocumentArchive lang={lang} />
        )}
      </main>

      {/* Python Script Modal */}
      <PythonScriptModal
        isOpen={isPythonModalOpen}
        onClose={() => setIsPythonModalOpen(false)}
        lang={lang}
      />

      {/* Scientific Footer */}
      <footer className="border-t border-zinc-900 bg-zinc-950 py-6 text-xs text-zinc-500 font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Satellite className="w-4 h-4 text-cyan-400" />
            <span>
              NORAD 528 (1963-003B) &amp; Caso Conde (1963) — Exploração Orbital Condicional
            </span>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <span>Modelos: SGP4, WGS84, J2, Termosfera Solar-Min 1963</span>
            <span className="text-zinc-700">|</span>
            <button
              onClick={() => setIsPythonModalOpen(true)}
              className="text-cyan-400 hover:underline cursor-pointer"
            >
              Exportar Python
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}
