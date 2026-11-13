import React from 'react';

type Language = 'pt' | 'en';

interface Props {
  lang: Language;
  children: React.ReactNode;
}

interface State {
  failed: boolean;
}

// A rejected React.lazy import must not unmount the entire laboratory.
// The parent keys this boundary by route, allowing unaffected tabs to open.
export class LabLoadErrorBoundary extends React.Component<Props, State> {
  state: State = { failed: false };

  static getDerivedStateFromError(): State {
    return { failed: true };
  }

  render() {
    if (!this.state.failed) return this.props.children;
    const pt = this.props.lang === 'pt';
    return (
      <section
        role="alert"
        aria-labelledby="lab-load-error-title"
        className="rounded-lg border border-amber-700 bg-amber-950/40 p-5 text-amber-100"
      >
        <h1 id="lab-load-error-title" className="mb-3 text-xl font-bold">
          {pt ? 'Não foi possível carregar esta seção' : 'This section could not be loaded'}
        </h1>
        <p className="mb-4 text-sm">
          {pt
            ? 'O instrumento está temporariamente indisponível. O Caderno e as outras seções continuam acessíveis.'
            : 'This instrument is temporarily unavailable. The Notebook and other sections remain accessible.'}
        </p>
        <div className="flex flex-wrap items-center gap-3">
          <a
            href="#/summary"
            className="inline-flex min-h-11 items-center rounded-md bg-cyan-700 px-4 py-2 text-white underline underline-offset-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
          >
            {pt ? 'Voltar à síntese' : 'Back to summary'}
          </a>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="min-h-11 rounded-md border border-amber-400 px-4 py-2 text-sm font-semibold text-amber-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
          >
            {pt ? 'Recarregar a página' : 'Reload page'}
          </button>
        </div>
      </section>
    );
  }
}
