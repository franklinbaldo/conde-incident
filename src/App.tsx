/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Navigation, TabId } from './components/Navigation';
import { hashForLabTab, resolveLabHash } from './lib/labRoutes';
import { ExecutiveSummary } from './components/ExecutiveSummary';
import { ResearchLedger } from './components/ResearchLedger';
import { EvidenceTrace } from './components/EvidenceTrace';
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
  const [activeTab, setActiveTab] = useState<TabId | null>(() => resolveLabHash(window.location.hash));
  const [lang, setLang] = useState<'pt' | 'en'>('pt');
  const [sharedTimeMs, setSharedTimeMs] = useState<number>(
    new Date('1963-11-08T19:48:00Z').getTime()
  );
  const [isPythonModalOpen, setIsPythonModalOpen] = useState<boolean>(false);
  const [quotaExceeded, setQuotaExceeded] = useState<boolean>(false);

  React.useEffect(() => {
    const handleQuotaExceeded = () => setQuotaExceeded(true);
    window.addEventListener('gmp-quota-exceeded', handleQuotaExceeded);
    return () => window.removeEventListener('gmp-quota-exceeded', handleQuotaExceeded);
  }, []);

  React.useEffect(() => { document.documentElement.lang = lang === 'pt' ? 'pt-BR' : 'en'; }, [lang]);

  React.useEffect(() => {
    const syncRoute = () => setActiveTab(resolveLabHash(window.location.hash));
    window.addEventListener('hashchange', syncRoute);
    return () => window.removeEventListener('hashchange', syncRoute);
  }, []);

  const navigateTab = (tab: TabId) => {
    if (tab === 'python') { setIsPythonModalOpen(true); return; }
    const fragment = hashForLabTab(tab);
    if (window.location.hash !== fragment) window.location.hash = fragment;
    setActiveTab(tab);
  };

  // Choosing a simulated pass also updates the shareable map URL.
  const handleSelectPassFromInverse = (timeMs: number) => {
    setSharedTimeMs(timeMs);
    navigateTab('map');
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
      {/* Google Maps Demo Quota Notification Banner */}
      {quotaExceeded && (
        <div className="bg-amber-950/90 border-b border-amber-600/80 text-amber-200 px-4 py-2.5 text-xs text-center sticky top-0 z-50 backdrop-blur shadow-md">
          <span>
            Google Maps Platform quota reached. If you are the app owner, visit{' '}
            <a
              href="https://developers.google.com/maps/ai/ai-studio?utm_campaign=gmp_mcp_codeassist_v1_aistudio#quota_exceeded_errors"
              target="_blank"
              rel="noopener noreferrer"
              className="underline font-semibold text-amber-100 hover:text-amber-50"
            >
              maps developer site
            </a>{' '}
            for instructions to update your account.
          </span>
        </div>
      )}
      {/* Top Header & Navigation */}
      <Navigation
        activeTab={activeTab}
        setActiveTab={navigateTab}
        lang={lang}
        setLang={setLang}
        onOpenPython={() => setIsPythonModalOpen(true)}
      />

      {/* Main Content Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        {activeTab === null && (
          <section aria-labelledby="invalid-route" className="max-w-xl rounded-xl border border-amber-800/70 p-6">
            <h1 id="invalid-route" className="text-xl font-semibold">Página do laboratório não encontrada</h1>
            <p className="mt-3 text-zinc-300">Esta seção não está disponível nesta versão. Nenhuma observação ou evidência é inferida do endereço.</p>
            <a href="#/summary" onClick={() => navigateTab('summary')} className="mt-4 inline-block text-cyan-300 underline">Voltar ao resumo</a>
          </section>
        )}
        {activeTab === 'research' && (
          <>
            <ResearchLedger lang={lang} />
            <EvidenceTrace lang={lang} />
          </>
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
              NORAD 528 (1963-003B) &amp; Caso Conde (1963) — Reconstrução Astrodinâmica
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
