import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ShieldCheck,
  Radio,
  FileSearch,
  ExternalLink,
  Info,
} from 'lucide-react';
import { CONDE_COORDINATES } from '../lib/constants';

interface ExecutiveSummaryProps {
  lang: 'pt' | 'en';
  onJumpToTab: (tab: any) => void;
}

export const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({
  lang,
  onJumpToTab,
}) => {
  const isPt = lang === 'pt';

  const sevenQuestions = [
    {
      num: 1,
      qPt: 'A órbita do 528 podia cruzar a latitude de Conde?',
      qEn: 'Could 528’s orbit cross Conde’s latitude?',
      status: 'CONFIRMADO',
      statusColor: 'text-emerald-400 bg-emerald-950/60 border-emerald-800',
      ansPt: 'SIM. Com inclinação orbital i = 81,8615°, o satélite cobre todas as latitudes entre -81,86° e +81,86°. Como Conde está em -11,8139° S (|lat| < i), o plano orbital cruza necessariamente essa latitude duas vezes a cada revolução de 91,4 minutos (uma vez ascendente e uma descendente).',
      ansEn: 'YES. With orbital inclination i = 81.8615°, the satellite covers all latitudes between -81.86° and +81.86°. Because Conde is at -11.8139° S (|lat| < i), the orbital ground track crosses this parallel twice per 91.4-min revolution.',
    },
    {
      num: 2,
      qPt: 'Alguma trajetória ajustada passa sobre Conde em 08/11?',
      qEn: 'Does any adjusted trajectory pass over Conde on Nov 8?',
      status: 'CONFIRMADO',
      statusColor: 'text-emerald-400 bg-emerald-950/60 border-emerald-800',
      ansPt: 'SIM. No modelo nominal, a Revolução #14 (cruzamento às ~19:48 UTC / 16:48 hora da Bahia) passa a ~844 km de Conde. Uma variação diminuta no arrasto acumulado (ajuste de fase ΔM de apenas ~0,5° a 2° ao longo de 12 dias) desloca a linha de passagem diretamente sobre o município.',
      ansEn: 'YES. Nominally, Revolution #14 (crossing at ~19:48 UTC / 16:48 Bahia time) passes within ~844 km of Conde. A minute accumulated drag adjustment (orbital phase shift ΔM of only ~0.5° to 2° over 12 days) shifts the ground track directly over Conde.',
    },
    {
      num: 3,
      qPt: 'Quais horários de passagem seriam admissíveis?',
      qEn: 'Which pass times would be admissible?',
      status: 'DELIMITADO',
      statusColor: 'text-cyan-400 bg-cyan-950/60 border-cyan-800',
      ansPt: 'Em 08/11/1963, as janelas de proximidade regional (<1200 km) ocorrem principalmente às 18:17 UTC (~15:17 local), 19:48 UTC (~16:48 local, passagem ascendente mais próxima) e às 21:20 UTC (~18:20 local ao pôr do sol). Qualquer avistamento em horário muito discrepante (ex: madrugada profunda) exigiria um número de revoluções inviável.',
      ansEn: 'On 08/11/1963, regional encounter windows (<1200 km) occur at 18:17 UTC (~15:17 local), 19:48 UTC (~16:48 local, closest ascending pass) and 21:20 UTC (~18:20 local at sunset). Any visual pass at deeply divergent times would require an unfeasible revolution count.',
    },
    {
      num: 4,
      qPt: 'A reentrada sobre Conde exige parâmetros físicos excepcionais?',
      qEn: 'Does reentry over Conde require exceptional physical parameters?',
      status: 'NÃO EXCEPCIONAIS',
      statusColor: 'text-emerald-400 bg-emerald-950/60 border-emerald-800',
      ansPt: 'NÃO. O coeficiente balístico efetivo requerido (B ≈ 0,018 a 0,028 m²/kg) é plenamente típico para componentes estruturais de alumínio, adaptadores de estágio ou fragmentos do Thor-Agena D. Não requer propulsão exótica nem densidades anômalas.',
      ansEn: 'NO. The required effective ballistic coefficient (B ≈ 0.018 to 0.028 m²/kg) is typical for aluminum structural components, adapters, or fragments of Thor-Agena D. It requires neither exotic propulsion nor anomalous atmospheric densities.',
    },
    {
      num: 5,
      qPt: 'O 527 ou 529 restringem a fase do 528?',
      qEn: 'Do 527 or 529 constrain 528’s orbital phase?',
      status: 'RESTRINGEM PLANO, NÃO A FASE',
      statusColor: 'text-amber-400 bg-amber-950/60 border-amber-800',
      ansPt: 'RESTRIÇÃO PARCIAL. Os objetos irmãos restringem com alta precisão o plano orbital inicial (inclinação ~81,84° e nó ascendente comum). Porém, pequenas diferenças no movimento médio (Δn ~ 0,5 rev/dia) dispersaram a anomalia verdadeira em milhares de graus ao longo de 10 meses. Não é possível inferir a fase exata do 528 a partir do 527 ou 529 na data de reentrada.',
      ansEn: 'PARTIAL. Sister objects tightly constrain the shared orbital plane (inclination ~81.84° and common RAAN). However, slight differences in mean motion (Δn ~ 0.5 rev/day) dispersed the true anomaly by thousands of degrees over 10 months. They cannot pinpoint 528’s exact phase on reentry date.',
    },
    {
      num: 6,
      qPt: 'A hipótese Conde pode ser refutada?',
      qEn: 'Can the Conde hypothesis be refuted?',
      status: 'AUSÊNCIA DE CORROBORAÇÃO FÍSICA E NÃO-IDENTIFICABILIDADE ORBITAL',
      statusColor: 'text-amber-400 bg-amber-950/60 border-amber-800',
      ansPt: 'DOIS NÍVEIS DISTINTOS DE ANÁLISE: (1) Nível Astrodinâmico: A passagem sobre a região é geometricamente compatível (|lat| < 81,86°), porém a trajetória terminal exata permanece ESTATISTICAMENTE NÃO-IDENTIFICÁVEL devido à dispersão de fase ao longo da órbita após 12 dias sem dados de radar (probabilidade a priori de impacto local ~0,006%). (2) Nível Físico e Documental: As averiguações do Ministério da Aeronáutica e os despachos consulares de 20/11/1963 registraram ausência de vestígios materiais (cratera, esfera metálica ou fragmentos identificados) no município, indicando que os elementos sensacionalistas da notícia original não encontraram sustentação empírica de campo.',
      ansEn: 'TWO DISTINCT LEVELS OF ANALYSIS: (1) Astrodynamic level: The regional pass is geometrically compatible (|lat| < 81.86°), but the exact terminal trajectory remains STATISTICALLY NON-IDENTIFIABLE due to along-track phase dispersion over 12 days without radar tracking (a priori local encounter chance ~0.006%). (2) Physical and Documentary level: Brazilian Air Force field inquiries and US consular dispatches of 20/11/1963 found no material evidence (crater, metallic sphere, or debris) in the municipality, indicating that the sensational elements of the initial media report lacked on-site empirical support.',
    },
    {
      num: 7,
      qPt: 'Qual é a principal informação ainda ausente?',
      qEn: 'What is the primary missing piece of information?',
      status: 'RASTREAMENTO FINAL',
      statusColor: 'text-cyan-400 bg-cyan-950/60 border-cyan-800',
      ansPt: 'Observações de rastreamento do radar SPADATS/NORAD ou Baker-Nunn (SAO) entre 01/11 e 08/11/1963. Um único TLE ou observação óptica posterior a 27/10/1963 reduziria a incerteza de fase de 360° para menos de 5°, determinando a órbita terminal definitiva.',
      ansEn: 'Radar tracking observations from SPADATS/NORAD or optical Baker-Nunn (SAO) between 01/11 and 08/11/1963. A single TLE or sighting after 27/10/1963 would collapse phase uncertainty from 360° to <5°, fixing the definitive terminal groundtrack.',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner Verdict */}
      <div className="bg-gradient-to-r from-zinc-900 via-zinc-900 to-zinc-950 border border-zinc-800 rounded-xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl -z-10" />
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-cyan-950/70 border border-cyan-700/80 text-cyan-300 text-xs font-mono">
              <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
              <span>{isPt ? 'VEREDITO ASTRODINÂMICO & DOCUMENTAL' : 'ASTRODYNAMIC & DOCUMENTARY VERDICT'}</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-zinc-100">
              {isPt
                ? 'Critério B (Compatibilidade Restrita) + Critério E (Não-Identificabilidade de Fase Final)'
                : 'Criterion B (Restricted Compatibility) + Criterion E (Non-Identifiability of Final Phase)'}
            </h1>
            <p className="text-sm text-zinc-300 leading-relaxed">
              {isPt
                ? 'A geometria orbital do NORAD 528 (1963-003B) admite sobrevoo da região de Conde-BA em 08/11/1963 sob parâmetros físicos comuns. Todavia, sem rastreamento radar nas 72 horas finais, a incerteza de fase ao longo da órbita não permite individualizar Conde dentre milhares de regiões ao redor da Terra (probabilidade a priori de impacto local ~0,006%). No âmbito empírico e documental, inspeções oficiais conduzidas à época não encontraram evidências físicas de impacto em solo (esfera, cratera ou restos materiais), apontando para a descaracterização dos detalhes sensacionalistas veiculados pela imprensa.'
                : 'The orbital geometry of NORAD 528 (1963-003B) permits an overflight of the Conde-BA region on 08/11/1963 under standard physical parameters. However, without radar tracking in the final 72 hours, along-track phase uncertainty prevents distinguishing Conde from thousands of equivalent regions across Earth (~0.006% a priori chance). At the empirical and documentary level, official inquiries conducted at the time found no physical evidence of ground impact (sphere, crater, or material remnants), indicating that sensational details in the contemporary media reports lacked on-site confirmation.'}
            </p>
          </div>

          <div className="flex flex-col sm:flex-row lg:flex-col gap-2.5 w-full lg:w-72 shrink-0">
            <button
              onClick={() => onJumpToTab('inverse')}
              className="px-4 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-md shadow-cyan-950"
            >
              <span>{isPt ? 'Examinar Passagens em Conde' : 'Inspect Conde Passes'}</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onJumpToTab('montecarlo')}
              className="px-4 py-2.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 font-medium text-xs transition-colors flex items-center justify-center gap-2 cursor-pointer"
            >
              <span>{isPt ? 'Simulação Monte Carlo (N=5000)' : 'Monte Carlo Simulation (N=5000)'}</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Fast Metrics Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6 pt-5 border-t border-zinc-800/80 text-xs">
          <div className="bg-zinc-950/70 p-3 rounded-lg border border-zinc-800/80">
            <div className="text-zinc-500 font-mono">{isPt ? 'Inclinação Orbital' : 'Orbital Inclination'}</div>
            <div className="text-base font-bold text-zinc-100 font-mono mt-0.5">81,8615°</div>
            <div className="text-[11px] text-emerald-400 mt-1">✓ {isPt ? 'Cruza latitude de Conde' : 'Crosses Conde latitude'}</div>
          </div>
          <div className="bg-zinc-950/70 p-3 rounded-lg border border-zinc-800/80">
            <div className="text-zinc-500 font-mono">{isPt ? 'Passagem Nominal 08/11' : 'Nominal Pass Nov 8'}</div>
            <div className="text-base font-bold text-cyan-300 font-mono mt-0.5">19:48 UTC (Rev 14)</div>
            <div className="text-[11px] text-zinc-400 mt-1">{isPt ? '16:48 hora local (Bahia)' : '16:48 Bahia local time'}</div>
          </div>
          <div className="bg-zinc-950/70 p-3 rounded-lg border border-zinc-800/80">
            <div className="text-zinc-500 font-mono">{isPt ? 'Probabilidade a Priori' : 'A Priori Probability'}</div>
            <div className="text-base font-bold text-amber-300 font-mono mt-0.5">~0,0062%</div>
            <div className="text-[11px] text-zinc-400 mt-1">{isPt ? 'Raio de 100 km (1 em 16.000)' : '100 km radius (1 in 16,000)'}</div>
          </div>
          <div className="bg-zinc-950/70 p-3 rounded-lg border border-zinc-800/80">
            <div className="text-zinc-500 font-mono">{isPt ? 'Conclusão Consular' : 'Consular Finding'}</div>
            <div className="text-base font-bold text-rose-400 font-mono mt-0.5">{isPt ? 'Boato Fabricado' : 'Fabricated Hoax'}</div>
            <div className="text-[11px] text-zinc-400 mt-1">{isPt ? 'Dep. Estado (20/11/1963)' : 'State Dept (20/11/1963)'}</div>
          </div>
        </div>
      </div>

      {/* The 7 Core Questions Section (Section 11 Handoff) */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-zinc-100 flex items-center gap-2">
              <FileSearch className="w-5 h-5 text-cyan-400" />
              <span>{isPt ? 'Matriz dos 7 Quesitos de Investigação (Seção 11)' : '7 Investigation Questions Matrix (Section 11)'}</span>
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              {isPt
                ? 'Avaliação quantitativa direta das proposições estabelecidas no handoff de astrodinâmica.'
                : 'Direct quantitative evaluation of the propositions established in the astrodynamics handoff.'}
            </p>
          </div>
        </div>

        <div className="space-y-3">
          {sevenQuestions.map((q) => (
            <div
              key={q.num}
              className="p-4 rounded-lg bg-zinc-950/70 border border-zinc-800/90 hover:border-zinc-700 transition-colors"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2.5">
                  <span className="w-6 h-6 rounded-full bg-zinc-800 text-zinc-300 font-mono text-xs flex items-center justify-center font-bold">
                    {q.num}
                  </span>
                  <h3 className="text-sm font-semibold text-zinc-200">
                    {isPt ? q.qPt : q.qEn}
                  </h3>
                </div>
                <span
                  className={`text-[11px] px-2.5 py-0.5 rounded font-mono font-semibold border self-start sm:self-auto ${q.statusColor}`}
                >
                  {q.status}
                </span>
              </div>
              <p className="text-xs text-zinc-300 leading-relaxed pl-8">
                {isPt ? q.ansPt : q.ansEn}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Hypothesis Rival Comparison: H1 vs H0 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* H1 Card */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-semibold text-amber-400 px-2 py-0.5 rounded bg-amber-950/60 border border-amber-800/80">
                HIPÓTESE H1 (CASO CONDE)
              </span>
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            </div>
            <h3 className="text-sm font-bold text-zinc-100">
              {isPt
                ? 'Reentrada terminal do NORAD 528 próxima de Conde, Bahia'
                : 'Terminal reentry of NORAD 528 near Conde, Bahia'}
            </h3>
            <ul className="text-xs text-zinc-300 space-y-2 list-disc list-inside">
              <li>
                <strong className="text-zinc-200">{isPt ? 'Geometria orbital:' : 'Orbital geometry:'}</strong>{' '}
                {isPt ? 'Totalmente compatível (|lat| < 81,86°).' : 'Fully compatible (|lat| < 81.86°).'}
              </li>
              <li>
                <strong className="text-zinc-200">{isPt ? 'Parâmetros de arrasto:' : 'Drag parameters:'}</strong>{' '}
                {isPt ? 'Coeficiente balístico comum (B ≈ 0,022 m²/kg) permite o sobrevoo.' : 'Standard ballistic coeff (B ≈ 0.022 m²/kg) permits the pass.'}
              </li>
              <li>
                <strong className="text-zinc-200">{isPt ? 'Evidência de campo:' : 'Field evidence:'}</strong>{' '}
                {isPt
                  ? 'Nenhum vestígio material (cratera de 4m, esfera ou destroços) foi localizado pelas autoridades civis e militares que inspecionaram o local em novembro de 1963.'
                  : 'No physical wreckage (4m crater, sphere, or debris) was located by civil and military authorities who inspected the site in November 1963.'}
              </li>
              <li>
                <strong className="text-zinc-200">{isPt ? 'Probabilidade a priori:' : 'A priori probability:'}</strong>{' '}
                ~0,0062% {isPt ? 'em relação ao conjunto de reentradas possíveis na Terra.' : 'relative to the set of all possible global reentries.'}
              </li>
            </ul>
          </div>
          <div className="mt-4 pt-3 border-t border-zinc-800 text-[11px] text-amber-400/90 font-mono">
            {isPt
              ? 'Status: Sem confirmação material de campo / Fase orbital não-identificável.'
              : 'Status: Lacks field material confirmation / Orbital phase non-identifiable.'}
          </div>
        </div>

        {/* H0 Card */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-semibold text-cyan-400 px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/80">
                HIPÓTESE H0 (DECAIMENTO PADRÃO)
              </span>
              <CheckCircle2 className="w-4 h-4 text-cyan-400" />
            </div>
            <h3 className="text-sm font-bold text-zinc-100">
              {isPt
                ? 'Reentrada terminal em outra região (oceanos ou alta latitude)'
                : 'Terminal reentry elsewhere (oceans or high latitude)'}
            </h3>
            <ul className="text-xs text-zinc-300 space-y-2 list-disc list-inside">
              <li>
                <strong className="text-zinc-200">{isPt ? 'Distribuição estatística:' : 'Statistical distribution:'}</strong>{' '}
                {isPt
                  ? '70% da superfície terrestre é oceânica; órbitas polares de alta inclinação possuem maior densidade em latitudes elevadas (±81,8°).'
                  : '70% of Earth is oceanic; high-inclination polar orbits spend more groundtrack time at high latitudes (±81.8°).'}
              </li>
              <li>
                <strong className="text-zinc-200">{isPt ? 'Consistência documental:' : 'Documentary consistency:'}</strong>{' '}
                {isPt
                  ? 'Coerente com as conclusões dos relatórios consulares e da Aeronáutica, que atribuíram as versões mais fantásticas à proliferação de notícias não confirmadas.'
                  : 'Consistent with consular and Air Force reports, which attributed the more fantastic claims to unverified news reports.'}
              </li>
              <li>
                <strong className="text-zinc-200">{isPt ? 'Natureza do objeto:' : 'Object nature:'}</strong>{' '}
                {isPt
                  ? 'Fragmento de alumínio ou componente estrutural sujeito à ablação e desintegração mesosférica típica (entre 100 km e 60 km).'
                  : 'Aluminum structural debris subject to typical mesospheric ablation and disintegration (between 100 km and 60 km).'}
              </li>
            </ul>
          </div>
          <div className="mt-4 pt-3 border-t border-zinc-800 text-[11px] text-cyan-400/90 font-mono">
            {isPt
              ? 'Status: Hipótese nula padrão com suporte probabilístico predominante.'
              : 'Status: Standard null hypothesis with predominant probabilistic support.'}
          </div>
        </div>
      </div>

      {/* Before vs After Comparative Impact Analysis */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
        <div className="border-b border-zinc-800 pb-3">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300 text-xs font-mono mb-1">
            <span>{isPt ? 'ANÁLISE COMPARATIVA DE IMPACTO' : 'COMPARATIVE IMPACT ANALYSIS'}</span>
          </div>
          <h3 className="text-base font-bold text-zinc-100">
            {isPt
              ? 'Como os Novos Dados e a Auditoria dos TLEs Alteram as Simulações Anteriores'
              : 'How New Data & TLE Audit Alter Previous Simulations'}
          </h3>
          <p className="text-xs text-zinc-400 mt-0.5">
            {isPt
              ? 'Comparativo sistemático entre as premissas preliminares/simplificadas e os resultados com efemérides auditadas e arrasto calibrado.'
              : 'Systematic comparison between preliminary/simplified assumptions and results with audited ephemerides and calibrated drag.'}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          {/* Dimension 1 */}
          <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2">
            <div className="text-cyan-400 font-bold text-[11px] uppercase">
              1. Orientação do Plano Orbital (Nó e Inclinação)
            </div>
            <div className="text-zinc-400 text-[11px] space-y-1">
              <div><span className="text-rose-400 font-semibold">[Antes]:</span> Plano tratado como livre ou com precessão aproximada; incerteza de faixas longitudinais.</div>
              <div><span className="text-emerald-400 font-semibold">[Agora]:</span> Inclinação travada em 81,8615° e RAAN em 284,1520° em 27/10. Com a taxa J2 de -1,173°/dia, a orientação nodal em 08/11/1963 é estritamente determinística (erro &lt; 0,1°).</div>
            </div>
          </div>

          {/* Dimension 2 */}
          <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2">
            <div className="text-cyan-400 font-bold text-[11px] uppercase">
              2. Campo BSTAR = 0 e Decaimento Termoesférico
            </div>
            <div className="text-zinc-400 text-[11px] space-y-1">
              <div><span className="text-rose-400 font-semibold">[Antes]:</span> Propagadores que usavam BSTAR=0 mantinham o satélite a 345 km eternamente sem reentrada em 08/11.</div>
              <div><span className="text-emerald-400 font-semibold">[Agora]:</span> BSTAR=0 desmistificado como convenção de catálogo manual. Calibração física com B ≈ 0,022 m²/kg e H = 45 km reproduz a reentrada terminal a 120-80 km exatamente no dia 8 de novembro.</div>
            </div>
          </div>

          {/* Dimension 3 */}
          <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2">
            <div className="text-cyan-400 font-bold text-[11px] uppercase">
              3. Janelas Horárias de Sobrevoo em Conde-BA
            </div>
            <div className="text-zinc-400 text-[11px] space-y-1">
              <div><span className="text-rose-400 font-semibold">[Antes]:</span> Especulação aberta para qualquer horário (madrugada, noite, manhã).</div>
              <div><span className="text-emerald-400 font-semibold">[Agora]:</span> Delimitação estrita a 16 revoluções nominais em 08/11. Apenas a Revolução 14 (~19:48 UTC / 16:48 hora da Bahia) tem aproximação geográfica real (~844 km) em altitude de quebra (~91 km).</div>
            </div>
          </div>

          {/* Dimension 4 */}
          <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2">
            <div className="text-cyan-400 font-bold text-[11px] uppercase">
              4. Triangulação com Objetos Irmãos (527 e 529)
            </div>
            <div className="text-zinc-400 text-[11px] space-y-1">
              <div><span className="text-rose-400 font-semibold">[Antes]:</span> Esperança intuitiva de que 527 e 529 pudessem "travar" a posição instantânea do 528.</div>
              <div><span className="text-emerald-400 font-semibold">[Agora]:</span> Demonstração matemática de que a defasagem acumulou mais de 141 voltas completas. Eles validam o vetor de lançamento e o ambiente de 1963, mas não podem fixar a anomalia do 528.</div>
            </div>
          </div>
        </div>
      </div>

      {/* Historical Context Note */}
      <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 flex items-start gap-3">
        <Info className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
        <div className="text-xs text-zinc-300 space-y-1">
          <div className="font-semibold text-zinc-200">
            {isPt ? 'Contexto Histórico & O Lançamento Militar Thor-Agena D (Missão 7153)' : 'Historical Context & Thor-Agena D Launch (Mission 7153)'}
          </div>
          <p className="leading-relaxed">
            {isPt
              ? 'Em 16 de janeiro de 1963, o foguete militar Thor-Agena D lançou a missão secreta da NRO 7153 (OPS 0180 / SAMOS F2-3) para inteligência de sinais eletromagnéticos (ELINT). O satélite principal (NORAD 527) operou brevemente até sofrer falha de baterias, permanecendo em órbita até 1969. Os objetos 528 (1963-003B) e 529 (1963-003C) eram componentes auxiliares de menor massa/área. O 528 decaiu em 08 de novembro de 1963. A transmissão da Rádio Tupi ocorreu exatamente nesse mesmo dia, gerando uma das mais singulares coincidências documentais da corrida espacial.'
              : 'On 16 January 1963, the Thor-Agena D launched secret NRO Mission 7153 (OPS 0180 / SAMOS F2-3) for ELINT/SIGINT. The main satellite (NORAD 527) operated until battery failure, surviving until 1969. Objects 528 (1963-003B) and 529 (1963-003C) were secondary components. 528 decayed on 08 November 1963. The Rádio Tupi broadcast occurred on that very date, creating one of the most intriguing historical coincidences of the space race.'}
          </p>
        </div>
      </div>
    </div>
  );
};
