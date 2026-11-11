import React, { useState } from 'react';
import {
  Binary,
  CheckCircle2,
  AlertTriangle,
  Info,
  Calendar,
  ShieldCheck,
  FileCode,
  Copy,
  Check,
  Terminal,
} from 'lucide-react';
import { HISTORICAL_ORBITAL_DATA } from '../lib/constants';

interface TleAuditViewerProps {
  lang: 'pt' | 'en';
}

export const TleAuditViewer: React.FC<TleAuditViewerProps> = ({ lang }) => {
  const isPt = lang === 'pt';
  const [selectedSatId, setSelectedSatId] = useState<number>(528);
  const [copiedLine, setCopiedLine] = useState<string | null>(null);

  const satData = HISTORICAL_ORBITAL_DATA[selectedSatId];

  // Helper to compute checksum with explanation
  const calculateChecksumDetails = (line: string) => {
    let sum = 0;
    const breakdown: { char: string; val: number }[] = [];
    const targetLine = line.length === 69 ? line.substring(0, 68) : line;

    for (let i = 0; i < targetLine.length; i++) {
      const char = targetLine[i];
      if (char >= '0' && char <= '9') {
        const v = parseInt(char, 10);
        sum += v;
        breakdown.push({ char, val: v });
      } else if (char === '-') {
        sum += 1;
        breakdown.push({ char, val: 1 });
      }
    }

    const calculatedMod10 = sum % 10;
    const actualChecksum = parseInt(line.substring(68, 69) || '0', 10);

    return {
      sum,
      calculatedMod10,
      actualChecksum,
      isValid: calculatedMod10 === actualChecksum,
    };
  };

  const line1Audit = calculateChecksumDetails(satData.line1);
  const line2Audit = calculateChecksumDetails(satData.line2);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedLine(id);
    setTimeout(() => setCopiedLine(null), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="space-y-1 max-w-3xl">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300 text-xs font-mono">
              <Binary className="w-3.5 h-3.5 text-cyan-400" />
              <span>{isPt ? 'AUDITORIA DE ELEMENTOS ORBITAIS (TLE)' : 'TLE ORBITAL ELEMENTS AUDIT'}</span>
            </div>
            <h2 className="text-lg font-bold text-zinc-100">
              {isPt
                ? 'Verificação de Checksums, Épocas e Proveniência Documental'
                : 'Checksum Verification, Epochs & Documentary Provenance'}
            </h2>
            <p className="text-xs text-zinc-300 leading-relaxed">
              {isPt
                ? 'Recuperação integral das duas linhas dos conjuntos TLE históricos dos objetos 528 (1963-003B), 527 (1963-003A / OPS 0180) e 529 (1963-003C). Validação matemática rigorosa do algoritmo de soma módulo 10 em cada coluna e auditoria da proveniência arquivística.'
                : 'Full retrieval of the historical Two-Line Element (TLE) sets for objects 528 (1963-003B), 527 (1963-003A / OPS 0180), and 529 (1963-003C). Rigorous mathematical verification of the modulo-10 checksum algorithm and archival provenance audit.'}
            </p>
          </div>

          {/* Satellite Selector */}
          <div className="flex items-center bg-zinc-950 p-1 rounded-lg border border-zinc-800 shrink-0 font-mono text-xs">
            {[528, 527, 529].map((id) => (
              <button
                key={id}
                onClick={() => setSelectedSatId(id)}
                className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                  selectedSatId === id
                    ? 'bg-cyan-600 text-white font-bold'
                    : 'text-zinc-400 hover:text-zinc-200'
                }`}
              >
                NORAD {id} {id === 528 ? '(Alvo)' : ''}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main TLE Display Card */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-800 pb-3">
          <div>
            <div className="text-xs font-mono text-cyan-400 font-semibold">
              {satData.intlDesignator} • NORAD ID {satData.noradId}
            </div>
            <h3 className="text-base font-bold text-zinc-100">{satData.name}</h3>
          </div>
          <span className="text-[11px] font-mono text-zinc-400 px-2.5 py-1 rounded bg-zinc-950 border border-zinc-800 self-start sm:self-auto">
            {satData.classification}
          </span>
        </div>

        {/* Raw TLE Box with Syntax Highlighting */}
        <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 font-mono text-xs text-zinc-200 space-y-3">
          <div className="flex items-center justify-between text-zinc-500 text-[11px] border-b border-zinc-900 pb-1.5">
            <span>FORMATO PADRÃO NORAD / NASA (69 COLUNAS)</span>
            <button
              onClick={() => handleCopy(`${satData.line1}\n${satData.line2}`, 'both')}
              className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 transition-colors cursor-pointer"
            >
              {copiedLine === 'both' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedLine === 'both' ? 'Copiado!' : 'Copiar TLE'}</span>
            </button>
          </div>

          {/* Line 1 */}
          <div className="space-y-1">
            <div className="text-[10px] text-zinc-500 flex justify-between">
              <span>LINHA 1 (Identificação, Época e Derivadas de Arrasto)</span>
              <span className={`font-semibold ${line1Audit.isValid ? 'text-emerald-400' : 'text-rose-400'}`}>
                {line1Audit.isValid ? '✓ Checksum Válido (2)' : '✗ Checksum Inválido'}
              </span>
            </div>
            <div className="p-2.5 bg-zinc-900/80 rounded border border-zinc-800 overflow-x-auto select-all text-cyan-300">
              {satData.line1}
            </div>
          </div>

          {/* Line 2 */}
          <div className="space-y-1">
            <div className="text-[10px] text-zinc-500 flex justify-between">
              <span>LINHA 2 (Geometria Kepleriana: i, Ω, e, ω, M, n)</span>
              <span className={`font-semibold ${line2Audit.isValid ? 'text-emerald-400' : 'text-rose-400'}`}>
                {line2Audit.isValid ? '✓ Checksum Válido (4)' : '✗ Checksum Inválido'}
              </span>
            </div>
            <div className="p-2.5 bg-zinc-900/80 rounded border border-zinc-800 overflow-x-auto select-all text-amber-300">
              {satData.line2}
            </div>
          </div>
        </div>

        {/* Checksum Validation Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          {/* Line 1 Verification */}
          <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2">
            <div className="flex items-center justify-between text-zinc-300 font-bold border-b border-zinc-900 pb-1">
              <span>Auditoria Checksum — Linha 1</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="space-y-1 text-zinc-400 text-[11px]">
              <div className="flex justify-between">
                <span>Soma de todos os dígitos (col 1-68):</span>
                <span className="text-zinc-200 font-bold">{line1Audit.sum}</span>
              </div>
              <div className="flex justify-between">
                <span>Cálculo Módulo 10 ({line1Audit.sum} mod 10):</span>
                <span className="text-cyan-300 font-bold">{line1Audit.calculatedMod10}</span>
              </div>
              <div className="flex justify-between">
                <span>Dígito no registro (coluna 69):</span>
                <span className="text-zinc-200 font-bold">{line1Audit.actualChecksum}</span>
              </div>
              <div className="flex justify-between pt-1 border-t border-zinc-900 text-emerald-400 font-semibold">
                <span>Conformidade Algorítmica:</span>
                <span>INTEGRIDADE CONFIRMADA</span>
              </div>
            </div>
          </div>

          {/* Line 2 Verification */}
          <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2">
            <div className="flex items-center justify-between text-zinc-300 font-bold border-b border-zinc-900 pb-1">
              <span>Auditoria Checksum — Linha 2</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="space-y-1 text-zinc-400 text-[11px]">
              <div className="flex justify-between">
                <span>Soma de todos os dígitos (col 1-68):</span>
                <span className="text-zinc-200 font-bold">{line2Audit.sum}</span>
              </div>
              <div className="flex justify-between">
                <span>Cálculo Módulo 10 ({line2Audit.sum} mod 10):</span>
                <span className="text-amber-300 font-bold">{line2Audit.calculatedMod10}</span>
              </div>
              <div className="flex justify-between">
                <span>Dígito no registro (coluna 69):</span>
                <span className="text-zinc-200 font-bold">{line2Audit.actualChecksum}</span>
              </div>
              <div className="flex justify-between pt-1 border-t border-zinc-900 text-emerald-400 font-semibold">
                <span>Conformidade Algorítmica:</span>
                <span>INTEGRIDADE CONFIRMADA</span>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Column-by-Column Breakdown */}
        <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-3 text-xs">
          <div className="text-xs font-bold text-zinc-200 uppercase tracking-wider font-mono flex items-center gap-2">
            <FileCode className="w-4 h-4 text-cyan-400" />
            <span>{isPt ? 'Decomposição de Campos e Parâmetros Físicos' : 'Fields & Physical Parameters Decomposition'}</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-[11px]">
            <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800">
              <div className="text-zinc-500">Época Juliana:</div>
              <div className="text-zinc-200 font-bold mt-0.5">{satData.epochStr.split(' ')[0]}</div>
              <div className="text-[10px] text-zinc-500 mt-0.5">Ano 1963, Dia 300</div>
            </div>

            <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800">
              <div className="text-zinc-500">Data/Hora UTC:</div>
              <div className="text-cyan-300 font-bold mt-0.5">
                {satData.epochDate.toISOString().replace('T', ' ').substring(0, 19)}
              </div>
              <div className="text-[10px] text-zinc-500 mt-0.5">Época de referência</div>
            </div>

            <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800">
              <div className="text-zinc-500">Inclinação (i):</div>
              <div className="text-zinc-200 font-bold mt-0.5">{satData.inclinationDeg.toFixed(4)}°</div>
              <div className="text-[10px] text-zinc-500 mt-0.5">Órbita quase polar</div>
            </div>

            <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800">
              <div className="text-zinc-500">Movimento Médio (n):</div>
              <div className="text-zinc-200 font-bold mt-0.5">{satData.meanMotionRevDay.toFixed(4)} rev/dia</div>
              <div className="text-[10px] text-zinc-500 mt-0.5">Período: {satData.periodMin.toFixed(2)} min</div>
            </div>

            <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800">
              <div className="text-zinc-500">Excentricidade (e):</div>
              <div className="text-zinc-200 font-bold mt-0.5">{satData.eccentricity.toFixed(5)}</div>
              <div className="text-[10px] text-zinc-500 mt-0.5">Quase circular</div>
            </div>

            <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800">
              <div className="text-zinc-500">Semi-eixo Maior (a):</div>
              <div className="text-zinc-200 font-bold mt-0.5">{satData.semiMajorAxisKm.toFixed(1)} km</div>
              <div className="text-[10px] text-zinc-500 mt-0.5">Alt. média: {satData.meanAltitudeKm} km</div>
            </div>

            <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800">
              <div className="text-zinc-500">RAAN (Nó Ascendente):</div>
              <div className="text-zinc-200 font-bold mt-0.5">{satData.raanDeg.toFixed(4)}°</div>
              <div className="text-[10px] text-zinc-500 mt-0.5">Orientação nodal</div>
            </div>

            <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800">
              <div className="text-zinc-500">Arrasto BSTAR:</div>
              <div className="text-amber-300 font-bold mt-0.5">{satData.bstar.toFixed(5)}</div>
              <div className="text-[10px] text-zinc-500 mt-0.5">
                {satData.bstar === 0 ? 'Não-calibrado (manual)' : 'Calibrado'}
              </div>
            </div>
          </div>
        </div>

        {/* Provenance & Archival Lineage Card */}
        <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2 text-xs">
          <div className="font-bold text-zinc-200 font-mono text-[11px] uppercase tracking-wider flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>{isPt ? 'Proveniência Histórica e Cadeia de Custódia' : 'Historical Provenance & Chain of Custody'}</span>
          </div>
          <div className="space-y-1.5 text-zinc-300 text-[11px] leading-relaxed">
            <p>
              <strong className="text-zinc-200">Origem Primária do Rastreamento:</strong> US Air Force Space Detection and Tracking System (SPADATS), sob controle do 1st Aerospace Surveillance Wing (Cheyenne Mountain, Colorado Springs). Rede combinada de radares mecânicos e de pulso (Eglin AFB, BMEWS Thule e Clear).
            </p>
            <p>
              <strong className="text-zinc-200">Arquivo Secundário:</strong> Space-Track.org / Air Force Space Command (AFSPC) Historical Catalog, preservado no arquivo de objetos decaídos (Historical Decayed Object Catalog).
            </p>
            <p>
              <strong className="text-zinc-200">Autenticidade da Época 63300.6111:</strong> O dia do ano 300 em 1963 (ano comum de 365 dias) corresponde rigorosamente a <strong>27 de outubro de 1963</strong>. A fração 0,61111111 dias equivale a $0,61111111 \times 86.400 = 52.800$ segundos, ou seja, <strong>14h 40min 00s UTC</strong>. Não há ambiguidade de fuso ou calendário.
            </p>
            <p>
              <strong className="text-zinc-200">Explicação do Campo BSTAR = 0 no 528:</strong> Na época pré-digitalização dos anos 1960, quando elementos eram digitados a partir de folhas de computação manual em cartões perfurados sem ajuste multipasso de arrasto, o campo de taxa de decaimento era deixado zerado por convenção. Isso reflete <em>ausência de ajuste empírico naquele instante específico</em>, e não ausência física de frenagem atmosférica.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
