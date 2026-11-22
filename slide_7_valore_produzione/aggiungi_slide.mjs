import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);
const WORKSPACE = path.dirname(ROOT);
const SKILL = process.argv[2];
if (!SKILL) throw new Error('Indicare il percorso della skill presentations come primo argomento.');
const { importRuntimeModule } = await import(pathToFileURL(path.join(SKILL, 'container_tools/runtime_helpers.mjs')).href);
const { FileBlob, PresentationFile } = await importRuntimeModule('@oai/artifact-tool');
const { applyPresentationChartFont, finalizePresentation } = await import(pathToFileURL(path.join(SKILL, 'container_tools/artifact_tool_utils.mjs')).href);
const build = path.join(WORKSPACE, '.electrade-pptx-build/valore-orario/orari-chiari');
await fs.mkdir(build, { recursive: true });
const source = path.join(ROOT, 'Presentazione_Electrade_AGGIORNATA.pptx');
const data = JSON.parse(await fs.readFile(path.join(HERE, 'dati/risultati.json'), 'utf8'));
const result = data.riepilogo;
const ppt = await PresentationFile.importPptx(await FileBlob.load(source));
if (ppt.slides.count !== 18) throw new Error('La presentazione sorgente deve contenere 18 slide.');
const writeBlob = async (dest, blob) => fs.writeFile(dest, new Uint8Array(await blob.arrayBuffer()));
for (const i of [16, 17]) {
  await writeBlob(path.join(build, `prima-${i + 1}.png`), await ppt.export({ slide: ppt.slides.items[i], format: 'png', scale: 1 }));
}
const layoutInfo = await ppt.inspect({ kind: 'layout', maxChars: 25000 });
await fs.writeFile(path.join(build, 'source-layout.ndjson'), layoutInfo.ndjson);

const C = { ink: '#2B3F46', accent: '#2F8480', secondary: '#6E8A88', red: '#BA664F', grid: '#D5DEE2' };
function text(slide, name, value, x, y, w, h, size = 24, bold = false, color = C.ink, align = 'left') {
  const box = slide.shapes.add({ geometry: 'textbox', name, position: { left: x, top: y, width: w, height: h }, fill: 'none', line: { fill: 'none', width: 0 } });
  box.text = value;
  box.text.style = { fontFamily: 'Calibri', fontSize: size, color, bold, alignment: align, verticalAlignment: 'top', wrap: true };
  box.text.insets = 0;
  return box;
}
function page(slide, number) {
  text(slide, 'Numero slide', `${number}/20`, 1126.4, 670.08, 96, 26.88, 13.333, false, '#8A99A0', 'right');
}
function n(value, decimals = 2) { return value.toLocaleString('it-IT', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }); }
for (const [i, slide] of ppt.slides.items.entries()) {
  const before = `${i + 1}/18`;
  const targets = slide.shapes.items.filter(s => s.text?.toString().trim() === before);
  if (targets.length !== 1) throw new Error('Numero slide non univoco: ' + before);
  targets[0].text.replace(before, `${i + 1}/20`);
}

const method = ppt.slides.add({ background: { fill: '#FFFFFF' } });
text(method, 'Titolo', 'Il valore del profilo solare sul mercato spot', 57.6, 58, 1164.8, 58, 40, true);
text(method, 'Domanda', 'Quanto avrebbe valorizzato un impianto virtuale con questo profilo?', 57.6, 137, 1150, 42, 29, true, C.accent);
text(method, 'Caso', 'Zona Sud, 12 e 13 novembre 2026, 48 ore in ora italiana (CET).\nProfilo proporzionale alla produzione solare osservata nella zona.', 57.6, 201, 1164, 76, 25);
text(method, 'Ipotesi', 'Ipotesi: tutta l’energia del profilo viene valorizzata al prezzo medio orario MGP\ndella zona Sud. Il ridimensionamento del profilo non cambia il prezzo ponderato.', 57.6, 298, 1164, 76, 24);
text(method, 'Energia', 'Energia oraria (MWh) = somma delle 4 potenze quartorarie (MW) × 0,25 h', 57.6, 402, 1164, 42, 25, true, C.accent);
text(method, 'Prezzo ponderato', 'Prezzo ponderato (€/MWh) = Σ(prezzo orario × energia oraria) / Σ(energia oraria)', 57.6, 459, 1164, 42, 25, true, C.accent);
text(method, 'Confronto', 'Confronto con la media dei 48 prezzi zonali, comprese le ore notturne.\nMisuro anche la quota di energia prodotta nelle ore con prezzo medio pari a zero.', 57.6, 529, 1164, 74, 24);
text(method, 'Limite', 'Stima descrittiva a prezzi medi orari. L’aggregazione non ricostruisce la valorizzazione quartoraria.', 57.6, 632, 1135, 36, 16, false, C.secondary);
page(method, 19);

const slide = ppt.slides.add({ background: { fill: '#FFFFFF' } });
text(slide, 'Titolo', `Il profilo solare valorizza ${n(result.prezzo_ponderato_produzione_eur_mwh)} €/MWh nelle 48 ore`, 57.6, 51, 1164.8, 58, 38, true);
text(slide, 'Contesto', 'Zona Sud, 12 e 13 novembre 2026. Confronto su base oraria, ora italiana (CET).', 57.6, 114, 1164, 32, 21, false, C.secondary);
text(slide, 'Ore esatte a zero', 'Prezzo zero il 13/11: ore 10, 11, 12, 13, 14 CET = ore 9, 10, 11, 12, 13 UTC (inizio ora)', 57.6, 146, 1164, 24, 17, true, C.red);
const categories = data.ore.map(r => `${r.ora_inizio_cet.slice(8, 10)}/11 ${r.ora_inizio_cet.slice(11, 13)}`);
const axisStyle = { fontFamily: 'Calibri', fontSize: 14, fill: C.secondary };
const transparent = { fill: 'none', width: 0 };
const common = {
  categories,
  hasLegend: false,
  chartFill: '#FFFFFF', chartLine: transparent, plotAreaFill: '#FFFFFF', plotAreaLine: transparent,
  titleTextStyle: { fontFamily: 'Calibri', fontSize: 18, fill: C.ink, bold: true },
  xAxis: { textStyle: axisStyle, line: { fill: C.grid, width: 1 }, majorGridlines: null },
  yAxis: { min: 0, numberFormatCode: '0', textStyle: axisStyle, line: transparent, majorGridlines: { fill: C.grid, width: 0.7 } },
};
const priceChart = slide.charts.add('line', {
  ...common,
  title: 'Prezzo medio orario (€/MWh)',
  lineOptions: { smooth: false },
  position: { left: 57.6, top: 161, width: 748, height: 190 },
  displayBlanksAs: 'gap',
  series: [
    { name: 'Prezzo medio orario Sud', values: data.ore.map(r => r.prezzo_medio_orario_eur_mwh), smooth: false, line: { fill: C.ink, width: 2.4 }, marker: { symbol: 'circle', size: 4, fill: C.ink }, points: data.ore.flatMap((r, idx) => r.prezzo_zero ? [{ idx, fill: C.red }] : []) },
  ],
});
text(slide, 'Prezzo quasi zero', 'Alle 09:00 CET il prezzo è 0,0025 €/MWh, indistinguibile da zero su questa scala.', 100, 348, 706, 22, 14, false, C.secondary);
const energyChart = slide.charts.add('bar', {
  ...common,
  title: 'Energia solare aggregata (MWh per ora)',
  position: { left: 57.6, top: 366, width: 748, height: 200 },
  series: [{ name: 'Energia solare', values: data.ore.map(r => r.energia_solare_mwh), fill: C.accent,
    points: data.ore.flatMap((r, idx) => r.prezzo_zero ? [{ idx, fill: C.red }] : []) }],
  barOptions: { direction: 'column', grouping: 'clustered', gapWidth: 20 },
});
for (const chart of [priceChart, energyChart]) applyPresentationChartFont(chart, { fontFamily: 'Calibri' });
text(slide, 'Legenda zero', 'Punti e colonne arancioni: le 5 ore con prezzo esattamente zero', 102, 559, 690, 25, 15, false, C.red);
text(slide, 'Etichetta media', 'Prezzo medio della zona', 855, 171, 360, 28, 22);
text(slide, 'Valore media', `${n(result.prezzo_medio_zonale_eur_mwh)} €/MWh`, 855, 204, 360, 48, 38, true);
text(slide, 'Etichetta ponderato', 'Prezzo ponderato sul solare', 855, 275, 360, 28, 22);
text(slide, 'Valore ponderato', `${n(result.prezzo_ponderato_produzione_eur_mwh)} €/MWh`, 855, 308, 360, 48, 38, true, C.accent);
text(slide, 'Etichetta differenza', 'Scarto rispetto alla media', 855, 378, 360, 28, 22);
text(slide, 'Valore differenza', `${n(result.differenza_eur_mwh)} €/MWh`, 855, 411, 360, 43, 33, true);
text(slide, 'Scarto percentuale', `${n(result.differenza_percento)}% rispetto alla media`, 855, 454, 360, 30, 21);
text(slide, 'Quota zero', `${n(result.quota_energia_a_prezzo_zero_percento)}%`, 855, 500, 360, 44, 36, true, C.red);
text(slide, 'Etichetta quota', 'dell’energia nelle ore a prezzo zero', 855, 544, 360, 30, 20);
text(slide, 'Conclusione', 'In questo caso, metà della produzione solare coincide con le ore a prezzo zero.\nPer valorizzare la produzione contano le ore e la zona in cui si produce.', 57.6, 600, 1164, 63, 23, true, C.accent);
text(slide, 'Limiti', 'Caso selezionato di 48 ore. Stima spot oraria, distinta dai ricavi contrattuali e dalla redditività annua.', 57.6, 674, 1035, 25, 14, false, C.secondary);
page(slide, 20);

const sources = `Fonti locali del progetto: ${result.fonti.map(s => s.percorso).join('; ')}.\nPrezzi: GME, esportazione oraria prezzi zonali, colonna Southern-Italy. Produzione: ENTSO-E A75, IT Sud, solar.\nAllineamento: giorno e ora di inizio intervallo CET (UTC+1). L'ora GME 1 corrisponde a 00:00-01:00.\nAggregazione: quattro potenze medie quartorarie moltiplicate per 0,25 ore e sommate. Nessuna interpolazione o imputazione di dati mancanti.\nControlli: 192 quarti d'ora, 48 ore complete, nessuna chiave duplicata, conservazione dell'energia.\nIpotesi: valorizzazione teorica dell'intera energia al prezzo medio orario, senza contratti, incentivi, costi, commissioni o sbilanciamenti. L'aggregazione oraria perde la covariazione fra prezzo e produzione interna all'ora e non equivale a ricavi MGP quartorari.\nIl profilo aggregato e un impianto virtuale: la scala non modifica prezzo ponderato e quota energia a zero. Il riferimento e la media aritmetica dei prezzi di tutte le 48 ore, inclusa la notte. Lo scarto non e una perdita o un ricavo alternativo conseguibile.\nIl caso e selezionato per la presenza di prezzi zero e non rappresenta la redditivita annuale del solare.`;
method.speakerNotes.text = sources;
slide.speakerNotes.text = sources + `\nLettura degli orari: il 13/11/2026 i cinque prezzi medi orari esattamente zero iniziano alle 10, 11, 12, 13 e 14 CET, equivalenti alle 9, 10, 11, 12 e 13 UTC. Ciascun valore si riferisce all'ora che inizia in quell'istante. Le cinque ore coprono quindi l'intervallo 10:00-15:00 CET (09:00-14:00 UTC), estremo finale escluso. Alle 09:00 CET (08:00 UTC) il prezzo e invece 0,0025 euro/MWh, positivo ma visivamente indistinguibile da zero sulla scala 0-300. I marcatori arancioni identificano soltanto gli zeri esatti.\nRisultati non arrotondati: ${JSON.stringify(result)}\nChiusura orale: Questo caso mi ha portato a chiedermi quanto conta il profilo di produzione. Nelle 48 ore analizzate, il profilo solare avrebbe valorizzato 87,24 euro per MWh ai prezzi medi orari, contro un prezzo medio di zona di 194,46. Il 50,43 per cento dell'energia coincide con le cinque ore a zero. Questo rende concreto il collegamento con l'attivita di gestione e valorizzazione della produzione rinnovabile.`;

for (const [i, s] of ppt.slides.items.entries()) {
  await writeBlob(path.join(build, `slide-${i + 1}.png`), await ppt.export({ slide: s, format: 'png', scale: 1 }));
}
const candidate = path.join(build, 'candidate.pptx');
await (await PresentationFile.exportPptx(ppt)).save(candidate);
if (process.argv.includes('--draft-only')) {
  console.log(candidate);
  process.exit(0);
}
const outputDir = path.join(ROOT, 'output_valorizzazione');
await fs.mkdir(outputDir, { recursive: true });
const finalPath = path.join(outputDir, 'Presentazione_Electrade_valorizzazione_oraria_orari_chiari.pptx');
const pythonExecutable = process.argv[3];
if (!pythonExecutable) throw new Error('Indicare il percorso Python bundled come secondo argomento.');
const validated = await finalizePresentation({
  workspaceDir: WORKSPACE, candidatePath: candidate, finalPath, explicitTotalSlideCount: 20,
  pythonExecutable,
  integrityValidatorPath: path.join(SKILL, 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(SKILL, 'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs: ['--expected-slide-size-emu', '12192000,6858000', '--validate-bullet-geometry', '--validate-heading-fit'],
  requiredNativeChartOwnerSlides: [20], materializeLiteralChartWorkbooks: true,
  nativeChartTargetApplication: 'powerpoint', verifyArtifactToolImport: true,
  fontPolicy: { basis: 'reference', families: ['Calibri'], referencePath: source, referenceSha256: crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex') },
  receiptPath: path.join(build, 'validation.json'),
});
console.log(validated.finalPath);
