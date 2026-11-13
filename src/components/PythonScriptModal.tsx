import React, { useState } from 'react';
import {
  X,
  Copy,
  Check,
  Download,
  Terminal,
  Code,
} from 'lucide-react';
import { PYTHON_REPRODUCIBILITY_SCRIPT } from '../lib/pythonScriptExport';
import { copyTextToClipboard } from '../lib/clipboardCopy';

interface PythonScriptModalProps {
  isOpen: boolean;
  onClose: () => void;
  lang: 'pt' | 'en';
}

export const PythonScriptModal: React.FC<PythonScriptModalProps> = ({
  isOpen,
  onClose,
  lang,
}) => {
  const isPt = lang === 'pt';
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'failed'>('idle');
  const titleId = React.useId();
  const dialogRef = React.useRef<HTMLDivElement>(null);
  const closeButtonRef = React.useRef<HTMLButtonElement>(null);
  // Parent callbacks may change between renders. Avoid resetting focus for that reason.
  const latestOnClose = React.useRef(onClose);
  latestOnClose.current = onClose;

  React.useEffect(() => {
    if (!isOpen) return;
    const opener = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    closeButtonRef.current?.focus();

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        latestOnClose.current();
        return;
      }
      if (event.key !== 'Tab') return;

      const dialog = dialogRef.current;
      if (!dialog) return;
      const controls = Array.from(dialog.querySelectorAll<HTMLElement>(
        'button:not([disabled]), a[href], input:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )).filter(element => element.getClientRects().length > 0);
      if (controls.length === 0) {
        event.preventDefault();
        dialog.focus();
        return;
      }
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && (document.activeElement === first || !dialog.contains(document.activeElement))) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && (document.activeElement === last || !dialog.contains(document.activeElement))) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      if (opener?.isConnected) opener.focus();
    };
  }, [isOpen]);

  React.useEffect(() => {
    if (!isOpen) setCopyState('idle');
  }, [isOpen]);

  if (!isOpen) return null;

  const handleCopy = async () => {
    const succeeded = await copyTextToClipboard(PYTHON_REPRODUCIBILITY_SCRIPT, navigator.clipboard);
    setCopyState(succeeded ? 'copied' : 'failed');
  };

  const handleDownload = () => {
    const blob = new Blob([PYTHON_REPRODUCIBILITY_SCRIPT], { type: 'text/x-python' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'norad528_reconstruction.py';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        className="bg-zinc-950 border border-zinc-800 rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden"
      >
        {/* Header */}
        <div className="p-4 border-b border-zinc-800 bg-zinc-900/60 flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex min-w-0 items-center gap-2 text-zinc-100">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <h3 id={titleId} className="min-w-0 break-words text-sm font-bold font-mono">
              norad528_reconstruction.py
            </h3>
            <span className="text-[11px] text-zinc-500 font-mono hidden lg:inline">
              {isPt ? '(Script reprodutível em Python 3)' : '(Reproducible Python 3 script)'}
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleCopy}
              className="min-h-11 px-3 py-2 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-mono flex items-center gap-1.5 transition-colors cursor-pointer focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300"
            >
              {copyState === 'copied' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copyState === 'copied' ? (isPt ? 'Copiado!' : 'Copied!') : (isPt ? 'Copiar código' : 'Copy code')}</span>
            </button>

            <button
              onClick={handleDownload}
              className="min-h-11 px-3 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-mono flex items-center gap-1.5 transition-colors cursor-pointer shadow focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{isPt ? 'Baixar .py' : 'Download .py'}</span>
            </button>

            <button
              ref={closeButtonRef}
              type="button"
              onClick={onClose}
              aria-label={isPt ? 'Fechar janela de exportação' : 'Close export dialog'}
              className="inline-flex min-h-11 min-w-11 items-center justify-center rounded hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors cursor-pointer focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Instructions banner */}
        <div className="bg-zinc-900/80 px-4 py-2 text-[11px] font-mono text-zinc-400 border-b border-zinc-800 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <span className="break-words">{isPt ? 'Como executar:' : 'Run:'} <code className="text-cyan-300">python3 norad528_reconstruction.py</code></span>
          <span className="text-zinc-500">{isPt ? 'Dependências:' : 'Dependencies:'} numpy, scipy</span>
        </div>

        {copyState === 'failed' && (
          <p role="alert" className="border-b border-rose-800 bg-rose-950/50 px-4 py-2 text-xs text-rose-100">
            {isPt
              ? 'Não foi possível copiar automaticamente. Selecione o código abaixo e copie manualmente.'
              : 'Automatic copying failed. Select the code below and copy it manually.'}
          </p>
        )}

        {/* Code View */}
        <div className="p-4 overflow-y-auto flex-1 font-mono text-xs text-zinc-300 bg-zinc-950 scrollbar-thin">
          <pre className="whitespace-pre-wrap leading-relaxed select-all">
            {PYTHON_REPRODUCIBILITY_SCRIPT}
          </pre>
        </div>
      </div>
    </div>
  );
};
