import React from 'react';

interface FallbackProps {
  lang: 'pt' | 'en';
  onClose: () => void;
  status: 'loading' | 'failed';
}

/** A working, keyboard-accessible exit even if the deferred Python module never arrives. */
export function PythonExportFallback({ lang, onClose, status }: FallbackProps) {
  const titleId = React.useId();
  const dialogRef = React.useRef<HTMLDivElement>(null);
  const closeRef = React.useRef<HTMLButtonElement>(null);
  const latestClose = React.useRef(onClose);
  latestClose.current = onClose;

  React.useEffect(() => {
    const opener = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    closeRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        latestClose.current();
      } else if (event.key === 'Tab') {
        const controls = Array.from(dialogRef.current?.querySelectorAll<HTMLButtonElement>('button:not([disabled])') ?? []);
        if (!controls.length) return;
        const first = controls[0];
        const last = controls[controls.length - 1];
        if (event.shiftKey && (document.activeElement === first || !dialogRef.current?.contains(document.activeElement))) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && (document.activeElement === last || !dialogRef.current?.contains(document.activeElement))) {
          event.preventDefault();
          first.focus();
        }
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      if (opener?.isConnected) opener.focus();
    };
  }, []);

  const isPt = lang === 'pt';
  const failed = status === 'failed';
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4">
      <div ref={dialogRef} role="dialog" aria-modal="true" aria-labelledby={titleId}
        className="w-full max-w-md rounded-xl border border-zinc-700 bg-zinc-950 p-5 text-zinc-100 shadow-2xl">
        <div className="flex items-start justify-between gap-3">
          <h2 id={titleId} className="font-semibold">
            {isPt ? 'Exportação Python' : 'Python export'}
          </h2>
          <button ref={closeRef} type="button" onClick={onClose}
            className="min-h-11 min-w-11 rounded-md border border-zinc-600 px-2 text-sm hover:bg-zinc-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300"
            aria-label={isPt ? 'Fechar exportação' : 'Close export'}>
            {isPt ? 'Fechar' : 'Close'}
          </button>
        </div>
        <p role={failed ? 'alert' : 'status'} className="mt-4 text-sm text-zinc-200">
          {failed
            ? (isPt ? 'Não foi possível carregar a ferramenta de exportação. Você pode fechar esta janela ou recarregar a página.'
              : 'The export tool could not be loaded. You can close this dialog or reload the page.')
            : (isPt ? 'Preparando a ferramenta de exportação…' : 'Preparing the export tool…')}
        </p>
        {failed && <button type="button" onClick={() => window.location.reload()}
          className="mt-4 min-h-11 rounded-md border border-cyan-500 px-4 py-2 text-sm text-cyan-200 hover:bg-zinc-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
          {isPt ? 'Recarregar página' : 'Reload page'}
        </button>}
      </div>
    </div>
  );
}

/** React.lazy rejects on a failed chunk: Suspense alone cannot catch that error. */
export class PythonExportBoundary extends React.Component<
  React.PropsWithChildren<Pick<FallbackProps, 'lang' | 'onClose'>>,
  { failed: boolean }
> {
  state = { failed: false };

  static getDerivedStateFromError(): { failed: boolean } {
    return { failed: true };
  }

  render() {
    if (this.state.failed) {
      return <PythonExportFallback lang={this.props.lang} onClose={this.props.onClose} status="failed" />;
    }
    return this.props.children;
  }
}
