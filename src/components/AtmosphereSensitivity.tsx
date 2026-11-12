import React, { useMemo, useState } from 'react';
import { Activity, AlertTriangle, ExternalLink, Layers, Wind } from 'lucide-react';
import { getThermosphericDensity } from '../lib/astrodynamics';

type Language = 'pt' | 'en';
interface AtmosphereSensitivityProps { lang: Language }

const matrix = 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md';
const lean = 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/formal/Conde1963/Core.lean';
const nasa = 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10';
const altitudesKm = [120, 160, 200, 240, 280, 320] as const;
const labels = {
  pt: {
    badge: 'DEMONSTRAÇÃO ALGÉBRICA · NÃO CALIBRADA',
    heading: 'Sensibilidade atmosférica: o que o modelo permite mostrar',
    intro: 'O decaimento de NORAD 528 depende de condições e parâmetros ainda não identificados. Esta tela compara apenas o formato de uma lei exponencial de densidade já presente no código. Não integra uma trajetória, não prevê a chegada a 120 km e não ajusta a data do boletim NASA.',
    control: 'Altura de escala hipotética (H)',
    help: '35–65 km são limites do controle didático, não um intervalo de confiança, uma medição de novembro de 1963 ou um domínio admissível calculado.',
    figure: 'Perfil relativo do modelo exponencial',
    ratio: 'Razão em relação à densidade do próprio modelo a 200 km',
    altitude: 'Altitude de exemplo',
    visual: 'Barra relativa ao maior valor nesta tabela',
    caveat: 'As barras e as razões são saídas algébricas de uma função parametrizada, não medições históricas. A amplitude gráfica depende das altitudes escolhidas.',
    sourceTitle: 'Cadeia de evidências e restrições',
    sourceIntro: 'Os identificadores abaixo remetem a ocorrências da matriz em revisão. Registros derivados da mesma cadeia não constituem observações independentes.',
    chain: [
      ['C191', 'Parâmetros derivados de TLE: não são medições diretas de arrasto.', matrix + '#L846-L872'],
      ['C192', 'H = 44,8–48,9 km é uma faixa hipotética de um modelo anterior, NÃO um intervalo físico validado.', matrix + '#L846-L872'],
      ['C193', 'Explorer XVII: medidas de abril a junho de 1963, não condições termoesféricas de novembro.', matrix + '#L846-L872'],
      ['C194', 'NASA e NORAD podem compartilhar rastreamento; não duplicar peso estatístico.', matrix + '#L846-L872'],
      ['C197–C202', 'Boletim NASA: dia de decaimento 08/11, sem horário, altitude terminal ou local.', matrix + '#L899-L912'],
    ],
    limitsTitle: 'Limites do fluxo científico',
    limits: 'Não existe nesta interface um conjunto não vazio e reduzido de parâmetros, ajuste orbital com custódia RAAN reconciliada, propagação calibrada ou holdout físico que permita usar estas curvas para localizar o objeto.',
    bst: 'BSTAR = 0 em uma linha de elementos não é medição de arrasto nulo. Tampouco autoriza afirmar por si só qual procedimento histórico produziu o campo.',
    unknown: 'Resultado científico para o local e a hora: indeterminado.',
    evidence: 'Abrir Evidence · dia NASA',
    raan: 'Abrir Evidence · conflito RAAN',
    premise: 'Premissas Lean (condicionais)',
    domain: 'Contraprovas de domínio (#37)',
    scenario: 'Cenários TLE alternativos (#43)',
    map: 'Mapa exploratório',
    provenance: 'Verificação: leitura da matriz e do código; perfil calculado apenas pelo código. Condições termoesféricas, TLEs primários e valores físicos de novembro não foram aqui verificados.',
  },
  en: {
    badge: 'ALGEBRAIC DEMONSTRATION · NOT CALIBRATED',
    heading: 'Atmospheric sensitivity: what this model can show',
    intro: 'NORAD 528 decay depends on environmental conditions and parameters that have not been established. This view only compares the shape of an exponential density law already in the code. It does not integrate a trajectory, predict crossing 120 km, or fit the NASA bulletin date.',
    control: 'Hypothetical scale height (H)',
    help: '35–65 km is the range of this teaching control, not a confidence interval, a November 1963 measurement, or a calculated admissible domain.',
    figure: 'Relative exponential-model profile',
    ratio: 'Ratio to this same model’s density at 200 km',
    altitude: 'Example altitude',
    visual: 'Bar relative to the highest entry in this table',
    caveat: 'The bars and ratios are algebraic outputs of a parameterized function, not historical measurements. The visual range depends on the chosen altitudes.',
    sourceTitle: 'Evidence and constraint chain',
    sourceIntro: 'These identifiers link to occurrences in the matrix under review. Derivatives of a shared source must not count as independent observations.',
    chain: [
      ['C191', 'TLE-derived parameters: not direct drag measurements.', matrix + '#L846-L872'],
      ['C192', 'H = 44.8–48.9 km is a hypothetical range from a previous model, NOT a validated physical interval.', matrix + '#L846-L872'],
      ['C193', 'Explorer XVII measurements: April–June 1963, not November thermospheric conditions.', matrix + '#L846-L872'],
      ['C194', 'NASA and NORAD can share tracking provenance; do not double count.', matrix + '#L846-L872'],
      ['C197–C202', 'NASA bulletin: decay day November 8, without a terminal time, altitude or location.', matrix + '#L899-L912'],
    ],
    limitsTitle: 'Scientific pipeline limits',
    limits: 'This view contains no certified nonempty reduced parameter domain, reconciled RAAN custody, calibrated orbit propagation or physical holdout that could use these curves to locate the object.',
    bst: 'BSTAR = 0 in an element line does not measure zero physical drag. Nor does it alone identify the historical recording procedure.',
    unknown: 'Scientific outcome for place and time: undetermined.',
    evidence: 'Open Evidence · NASA day',
    raan: 'Open Evidence · RAAN conflict',
    premise: 'Lean premises (conditional)',
    domain: 'Domain counterexamples (#37)',
    scenario: 'Alternative TLE scenarios (#43)',
    map: 'Exploratory map',
    provenance: 'Verification: matrix and code examined; profile computed from code only. November atmospheric conditions, primary TLEs and physical values have not been independently verified here.',
  },
} as const;

export const AtmosphereSensitivity: React.FC<AtmosphereSensitivityProps> = ({ lang }) => {
  const t = labels[lang];
  const [scaleHeightKm, setScaleHeightKm] = useState(45);
  const profile = useMemo(() => {
    const reference = getThermosphericDensity(200, scaleHeightKm);
    return altitudesKm.map(altitude => ({
      altitude,
      ratio: getThermosphericDensity(altitude, scaleHeightKm) / reference,
    }));
  }, [scaleHeightKm]);
  const maximum = profile[0].ratio;

  return (
    <section className="space-y-6" aria-labelledby="atmosphere-heading">
      <header className="rounded-xl border border-amber-800/70 bg-zinc-900 p-5 sm:p-6">
        <p className="inline-flex items-center gap-2 text-xs font-semibold text-amber-300">
          <AlertTriangle size={16} aria-hidden="true" /> {t.badge}
        </p>
        <h1 id="atmosphere-heading" className="mt-3 text-xl font-semibold text-zinc-100">{t.heading}</h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-zinc-200">{t.intro}</p>
      </header>

      <div className="grid gap-5 lg:grid-cols-2">
        <section className="rounded-xl border border-zinc-700 bg-zinc-900 p-5 sm:p-6" aria-labelledby="atmosphere-control-heading">
          <h2 id="atmosphere-control-heading" className="flex items-center gap-2 text-base font-semibold text-zinc-100">
            <Wind size={18} aria-hidden="true" /> {t.control}
          </h2>
          <label htmlFor="atmosphere-height" className="mt-5 block text-sm text-cyan-200">
            H = <output htmlFor="atmosphere-height">{scaleHeightKm} km</output>
          </label>
          <input
            id="atmosphere-height"
            className="mt-3 w-full cursor-pointer accent-cyan-400 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-cyan-300"
            type="range"
            min={35}
            max={65}
            step={1}
            value={scaleHeightKm}
            onChange={event => setScaleHeightKm(Number(event.target.value))}
            aria-describedby="atmosphere-height-help"
            aria-valuetext={`${scaleHeightKm} km`}
          />
          <div className="mt-1 flex justify-between text-xs text-zinc-400"><span>35 km</span><span>65 km</span></div>
          <p id="atmosphere-height-help" className="mt-4 text-sm leading-6 text-zinc-300">{t.help}</p>
        </section>

        <aside className="rounded-xl border border-zinc-700 bg-zinc-900 p-5 sm:p-6" aria-labelledby="atmosphere-limits-heading">
          <h2 id="atmosphere-limits-heading" className="flex items-center gap-2 text-base font-semibold text-zinc-100">
            <Activity size={18} aria-hidden="true" /> {t.limitsTitle}
          </h2>
          <p className="mt-3 text-sm leading-6 text-zinc-300">{t.limits}</p>
          <p className="mt-3 text-sm leading-6 text-zinc-300">{t.bst}</p>
          <p className="mt-4 border-t border-zinc-700 pt-3 text-sm font-semibold text-amber-200">{t.unknown}</p>
        </aside>
      </div>

      <section className="rounded-xl border border-zinc-700 bg-zinc-900 p-5 sm:p-6" aria-labelledby="atmosphere-profile-heading">
        <h2 id="atmosphere-profile-heading" className="flex items-center gap-2 text-base font-semibold text-zinc-100">
          <Layers size={18} aria-hidden="true" /> {t.figure}
        </h2>
        <p className="mt-2 text-sm text-zinc-300">{t.ratio}</p>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[320px] border-collapse text-left text-sm">
            <caption className="sr-only">{t.figure} · H = {scaleHeightKm} km</caption>
            <thead><tr className="border-b border-zinc-700 text-zinc-300">
              <th scope="col" className="py-3 pr-4">{t.altitude}</th>
              <th scope="col" className="py-3 pr-4">{t.ratio}</th>
              <th scope="col" className="py-3">{t.visual}</th>
            </tr></thead>
            <tbody>{profile.map(point => (
              <tr key={point.altitude} className="border-b border-zinc-800">
                <th scope="row" className="py-3 pr-4 font-normal text-zinc-200">{point.altitude} km</th>
                <td className="py-3 pr-4 font-mono text-cyan-200">{point.ratio.toFixed(3)}×</td>
                <td className="w-2/5 py-3" aria-hidden="true">
                  <div className="h-2 rounded bg-zinc-800">
                    <div className="h-2 rounded bg-cyan-500" style={{ width: `${(point.ratio / maximum) * 100}%` }} />
                  </div>
                </td>
              </tr>
            ))}</tbody>
          </table>
        </div>
        <p className="mt-3 text-xs leading-5 text-zinc-400">{t.caveat}</p>
      </section>

      <section className="rounded-xl border border-zinc-700 bg-zinc-900 p-5 sm:p-6" aria-labelledby="atmosphere-evidence-heading">
        <h2 id="atmosphere-evidence-heading" className="text-base font-semibold text-zinc-100">{t.sourceTitle}</h2>
        <p className="mt-2 text-sm text-zinc-300">{t.sourceIntro}</p>
        <ul className="mt-4 space-y-3">
          {t.chain.map(([id, description, href]) => (
            <li key={id} className="border-l-2 border-cyan-800 pl-4 text-sm leading-6">
              <a href={href} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 font-mono font-semibold text-cyan-200 underline underline-offset-2 focus-visible:outline-2 focus-visible:outline-cyan-200">
                {id} <ExternalLink size={13} aria-hidden="true" />
              </a>
              <span className="ml-2 text-zinc-300">{description}</span>
            </li>
          ))}
        </ul>
        <nav aria-label={t.sourceTitle} className="mt-5 flex flex-wrap gap-3 text-sm">
          {[
            ['#/research/c197', t.evidence], ['#/research/raan', t.raan],
            [lean, t.premise], ['https://github.com/franklinbaldo/conde-incident/pull/37', t.domain],
            ['https://github.com/franklinbaldo/conde-incident/pull/43', t.scenario],
            ['#/map', t.map],
          ].map(([href, label]) => (
            <a key={href} href={href} className="rounded-md border border-cyan-800/70 px-3 py-2 text-cyan-200 underline underline-offset-2 hover:bg-cyan-950/40 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
              {label}
            </a>
          ))}
        </nav>
        <p className="mt-4 text-xs leading-5 text-zinc-400">
          {t.provenance}{' '}
          <a href={nasa} target="_blank" rel="noopener noreferrer" className="text-cyan-200 underline underline-offset-2">NASA SSR, 15/11/1963, p. 8</a>
        </p>
      </section>
    </section>
  );
};
