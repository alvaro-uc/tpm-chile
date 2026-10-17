import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const ROOT = path.resolve(process.cwd());
const RUNTIME = 'C:/Users/56974/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES = `${RUNTIME}/node/node_modules`;
const SKILL = 'C:/Users/56974/.codex/plugins/cache/openai-primary-runtime/presentations/26.1013.11914/skills/presentations';
const { Presentation, PresentationFile } = await import(pathToFileURL(`${RUNTIME}/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs`).href);
const { applyPresentationChartFont, finalizePresentation } = await import(pathToFileURL(`${SKILL}/container_tools/artifact_tool_utils.mjs`).href);
const build = path.join(ROOT, '.build/presentacion');
const out = path.join(ROOT, 'output/presentacion');
await fs.mkdir(out, {recursive:true});
const data = JSON.parse(await fs.readFile(path.join(build,'datos.json'),'utf8'));
const content = JSON.parse(await fs.readFile(path.join(ROOT,'src/presentation/contenido_video.json'),'utf8'));
const deck = Presentation.create({slideSize:{width:1280,height:720}});
const C = {ink:'#172B42', blue:'#2364AA', green:'#16765B', red:'#B63F45', gray:'#64748B', grid:'#DCE3EC', pale:'#F4F7FB', white:'#FFFFFF'};
const font='Arial';
function text(slide,value,x,y,w,h,size=28,color=C.ink,bold=false){
  const sh=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  sh.text=value; sh.text.style={typeface:font,fontSize:size,color,bold};sh.text.insets=0; return sh;
}
function line(slide,x,y,w,h,color=C.grid,width=1){
  return slide.shapes.add({geometry:'line',position:{left:x,top:y,width:Math.max(w,1),height:Math.max(h,1)},fill:'none',line:{fill:color,width,style:'solid'}});
}
function arrow(slide,x,y,w,color=C.blue){
  return slide.shapes.add({geometry:'rightArrow',position:{left:x,top:y,width:w,height:18},fill:color,line:{fill:'none',width:0}});
}
function slideFor(index,title,subtitle){
  const s=deck.slides.add();s.background.fill=C.white;
  text(s,title,64,46,1150,110,44,C.ink,true);
  if(subtitle)text(s,subtitle,66,157,1140,52,24,C.gray);
  text(s,`${index+1} / 8`,1158,680,65,25,17,C.gray);
  const v=content.slides[index];
  s.speakerNotes.text=`DIAPOSITIVA ${index+1}. ${v.titulo}\nVoz propuesta: ${v.voz}. Tiempo: ${v.segundos} segundos.\n\nTEXTO PARA ENSAYAR\n${v.hablado}\n\nPUNTERO\n${v.puntero}\n\nFUENTES\n${v.fuentes.join('\n')}`;
  return s;
}
function foot(s,value){text(s,value,66,652,1080,26,16,C.gray);}
function table(s,values,x,y,w,h,widths,fsz=24){
  const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});
  t.borders.assign({fill:C.white,width:0,style:'solid'});
  for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
    const cell=t.getCell(r,c);cell.fill=r===0?C.ink:(r%2===0?C.pale:C.white);
    cell.text.style={typeface:font,fontSize:fsz,color:r===0?C.white:C.ink,bold:r===0};
  }
  t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({margins:{top:3,bottom:3,left:8,right:8}});
  return t;
}
function nativeChart(s,type,config){
  const c=s.charts.add(type,{chartFill:C.white,plotAreaFill:C.white,chartLine:{fill:'none',width:0},...config});
  applyPresentationChartFont(c,{fontFamily:font});return c;
}

// 1. Portada con la pregunta y el resultado que se quiere clasificar.
{
  const s=slideFor(0,'','');
  text(s,'¿Podemos anticipar\nal Banco Central?',64,100,1148,186,68,C.ink,true);
  text(s,'Decisiones de TPM en Chile, 2010–2025',68,320,1100,55,32,C.gray);
  text(s,'Sube',68,440,260,66,42,C.red,true);
  text(s,'Mantiene',440,440,360,66,42,C.blue,true);
  text(s,'Baja',900,440,260,66,42,C.green,true);
  text(s,'Video de avance del proyecto',68,560,1100,40,26,C.ink);
  text(s,'IMT2200   Grupo 9   17 de octubre de 2026',68,608,1100,30,21,C.gray);
  text(s,'Loreto Cornejo, Fernando Osses, Macarena Perez y Álvaro Recabarren',68,649,1060,28,18,C.gray);
}
// 2. Inventario con frecuencias y fuente, en tabla editable.
{
  const s=slideFor(1,content.slides[1].titulo,'Ocho series disponibles con distintas frecuencias de actualización');
  table(s,[['Serie','Frecuencia','Fuente'],['TPM previa','Diaria','Banco Central'],['Dólar observado','Diaria','Banco Central'],['Cobre spot BML/LME','Diaria','Cochilco'],['Desocupación','Mensual, trimestre móvil','INE, vía BCCh'],['Expectativa de TPM','Mensual','EEE, Banco Central'],['IMACEC original','Mensual','Banco Central'],['IPC, variación mensual','Mensual','INE, vía BCCh'],['IPC anual de diciembre','Anual','INE, vía BCCh']],66,222,1148,365,[410,420,318],24);
  text(s,'Ventana 2010–2025. Antecedentes de 2009 separados.',66,606,1148,36,24,C.ink);
  foot(s,'Cobre: 4.042 cotizaciones. IPC anual: pertinencia como predictor en revisión.');
}
// 3. Distribución de categorías. Un gráfico de barras, no un histograma continuo.
{
  const s=slideFor(2,content.slides[2].titulo,'161 anuncios oficiales: una observación por decisión de política monetaria');
  nativeChart(s,'bar',{
    position:{left:65,top:225,width:840,height:385},categories:['Mantiene','Baja','Sube'],
    series:[{name:'Decisiones',values:[data.counts.mantiene,data.counts.baja,data.counts.sube],fill:C.blue,
      points:[{idx:0,fill:C.blue},{idx:1,fill:C.green},{idx:2,fill:C.red}]}],
    barOptions:{direction:'column',grouping:'clustered',gapWidth:100},hasLegend:false,
    xAxis:{textStyle:{fontSize:26,fill:C.ink},line:{fill:C.gray,width:1}},
    yAxis:{min:0,max:120,majorUnit:30,title:{text:'Número de decisiones',textStyle:{fontSize:22,fill:C.gray}},textStyle:{fontSize:20,fill:C.gray},majorGridlines:{fill:C.grid,width:1}},
    dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:30,fill:C.ink,bold:true}},
  });
  text(s,'64%',947,280,245,100,70,C.blue,true);
  text(s,'de mantenciones\nen el registro',948,390,245,100,28,C.ink);
  text(s,'La evaluación debe\nconsiderar cada clase',948,525,245,80,25,C.gray);
  foot(s,'Fuente: historial TPM 2010–2025. El 64% describe la muestra completa, no rendimiento fuera de muestra.');
}
// 4. Serie completa con escalones diarios y marcadores en anuncios.
{
  const s=slideFor(3,content.slides[3].titulo,'Línea diaria y fechas de anuncio de las 27 subidas y 31 bajas');
  const series=[{name:'TPM diaria',xValues:data.daily.map(p=>p[0]),values:data.daily.map(p=>p[1]),line:{fill:C.blue,width:2.7},marker:{symbol:'none'}}];
  for(const [key,name,color,shape] of [['sube','Sube',C.red,'triangle'],['baja','Baja',C.green,'diamond']]){
    series.push({name,xValues:data.decision_points[key].map(p=>p[0]),values:data.decision_points[key].map(p=>p[1]),line:{fill:'none',width:0},marker:{symbol:shape,size:8,fill:color}});
  }
  nativeChart(s,'scatter',{position:{left:65,top:225,width:1150,height:385},series,scatterOptions:{style:'lineWithMarkers'},hasLegend:true,
    legend:{position:'bottom',overlay:false,textStyle:{fontSize:23,fill:C.ink}},
    xAxis:{min:2010,max:2025.99,majorUnit:2,numberFormatCode:'0',textStyle:{fontSize:22,fill:C.gray},majorGridlines:null},
    yAxis:{min:0,max:12,majorUnit:3,title:{text:'TPM (%)',textStyle:{fontSize:23,fill:C.gray}},textStyle:{fontSize:22,fill:C.gray},majorGridlines:{fill:C.grid,width:1}}});
  text(s,'La trayectoria describe ciclos de la tasa. La evaluación conservará el orden temporal.',66,615,1148,36,24,C.ink);
  foot(s,'Fuente: BCCh e historial de reuniones. Marcadores: fecha de anuncio y nivel posterior de la serie.');
}
// 5. Acercamiento en la serie diaria: mantenciones y fecha de anuncio.
{
  const s=slideFor(4,content.slides[4].titulo,'Abril–junio de 2010: el registro de anuncios permite recuperar esas reuniones');
  nativeChart(s,'scatter',{position:{left:65,top:240,width:1148,height:340},
    scatterOptions:{style:'lineWithMarkers'},hasLegend:false,
    series:[{name:'TPM diaria',xValues:data.sample.map(p=>p[0]),values:data.sample.map(p=>p[1]),line:{fill:C.blue,width:3},marker:{symbol:'none'}},
      {name:'Mantiene',xValues:[105,133],values:[.5,.5],line:{fill:'none',width:0},marker:{symbol:'circle',size:13,fill:C.green}},
      {name:'Anuncia subida',xValues:[166],values:[.5],line:{fill:'none',width:0},marker:{symbol:'triangle',size:14,fill:C.red}}],
    xAxis:{min:91,max:181,majorUnit:15,numberFormatCode:'0',tickLabelPosition:'none',majorGridlines:null},
    yAxis:{min:0,max:1.5,majorUnit:.5,numberFormatCode:'0.0',title:{text:'TPM (%)',textStyle:{fontSize:23,fill:C.gray}},textStyle:{fontSize:22,fill:C.gray},majorGridlines:{fill:C.grid,width:1}}});
  text(s,'15/04\nMantiene 0,50%',205,225,270,85,25,C.ink,true);
  text(s,'13/05\nMantiene 0,50%',548,225,270,85,25,C.ink,true);
  text(s,'15/06\nAnuncia 1,00%',922,225,280,85,25,C.ink,true);
  text(s,'Abril',210,575,230,35,24,C.gray);text(s,'Mayo',530,575,230,35,24,C.gray);text(s,'Junio',930,575,230,35,24,C.gray);
  text(s,'Nuevo nivel en la serie diaria desde el 16/06. Anuncio oficial el 15/06.',66,614,1148,35,25,C.ink);
  foot(s,'Fuente: tabla de reuniones y serie diaria BCCh. Los tramos planos también contienen decisiones.');
}
// 6. Diagrama temporal editable del caso real de publicaciones IPC.
{
  const s=slideFor(5,content.slides[5].titulo,'Decisión: 17/10/2024. Corte de información: cierre del 16/10/2024.');
  const begin=Date.UTC(2024,7,1),end=Date.UTC(2024,10,15);
  const xx=d=>116+(Date.parse(`${d}T00:00:00Z`)-begin)/(end-begin)*1030;
  const cut=xx('2024-10-16');
  line(s,cut,265,1,298,C.ink,2);
  text(s,'Corte 16/10',cut-70,212,175,42,23,C.ink,true);
  const rows=[['IPC de agosto','2024-08-01','2024-08-31','2024-09-06','06/09   0,3%',285,C.green],
    ['IPC de septiembre','2024-09-01','2024-09-30','2024-10-08','08/10   0,1%',395,C.green],
    ['IPC de octubre','2024-10-01','2024-10-31','2024-11-08','08/11   1,0%',505,C.red]];
  for(const [name,start,finish,release,label,y,color] of rows){
    const a=xx(start),b=xx(finish),r=xx(release);
    text(s,name,name==='IPC de octubre'?a-40:a,y-40,340,36,24,C.ink,true);
    line(s,a,y,b-a,1,C.grid,12);
    arrow(s,b+4,y-8,r-b-8,color);
    s.shapes.add({geometry:'ellipse',position:{left:r-7,top:y-7,width:14,height:14},fill:color,line:{fill:'none',width:0}});
    text(s,label,r-90,y+18,210,38,24,color,true);
  }
  text(s,'Agosto',116,578,200,35,22,C.gray);text(s,'Septiembre',xx('2024-09-01'),578,200,35,22,C.gray);
  text(s,'Octubre',xx('2024-10-01'),578,200,35,22,C.gray);text(s,'Noviembre',xx('2024-11-01'),578,200,35,22,C.gray);
  text(s,'Para esta reunión se usa septiembre: 0,1%. Octubre queda fuera del corte.',66,616,1148,35,25,C.ink);
  foot(s,'Fuentes: boletines INE 310–312 y comunicado BCCh del 17/10/2024. Barra: período. Punto: publicación.');
}
// 7. Relación editable y fila final.
{
  const s=slideFor(6,content.slides[6].titulo,'Los identificadores conservan la relación con la observación publicada');
  text(s,'REUNIÓN',66,245,310,40,26,C.gray,true);
  text(s,'RPM_20241017',66,305,340,48,32,C.blue,true);
  text(s,'Anuncio 17/10/2024\nCorte 16/10/2024',66,370,340,90,26,C.ink);
  text(s,'VÍNCULO',490,245,300,40,26,C.gray,true);
  text(s,'Reunión + variable',490,305,340,48,30,C.blue,true);
  text(s,'Publicación 08/10/2024\nFuente y versión histórica',490,370,350,90,25,C.ink);
  text(s,'OBSERVACIÓN',920,245,310,40,26,C.gray,true);
  text(s,'IPC de septiembre',920,305,330,48,29,C.green,true);
  text(s,'Valor publicado\n0,1%',920,370,300,100,30,C.ink);
  arrow(s,410,323,55);arrow(s,840,323,55);
  table(s,[['Reunión','Corte','IPC mensual (X)','Decisión (y)'],['RPM_20241017','16/10/2024','0,1%','Baja']],66,500,1148,104,[330,255,290,273],24);
  text(s,'Una medición puede corresponder a varias reuniones.',66,620,1148,35,25,C.ink);
  foot(s,'ID del dato: ipc_general_mensual_20240901. La respuesta y se obtiene después del anuncio.');
}
// 8. Estado comprobado y trabajo siguiente, sin métricas inventadas.
{
  const s=slideFor(7,content.slides[7].titulo,'El avance actual corresponde a preparación, análisis descriptivo e integración');
  text(s,'Construido',66,235,500,45,32,C.green,true);
  text(s,'161 decisiones y ocho series limpias\nDistribución y trayectoria de la TPM\nVínculos con un caso IPC verificado',66,310,555,170,28,C.ink);
  text(s,'En desarrollo',690,235,500,45,32,C.blue,true);
  text(s,'Calendarios completos y revisiones\nCalendario bancario independiente\nSelección final de predictores',690,310,530,170,28,C.ink);
  text(s,'Evaluación prevista',66,520,1148,45,29,C.ink,true);
  text(s,'Entrenamiento anterior',66,582,460,48,29,C.blue,true);
  arrow(s,535,590,70,C.gray);
  text(s,'Prueba posterior',640,582,510,48,29,C.blue,true);
  foot(s,'Línea base y regresión logística previstas. Todavía no hay métricas de modelos.');
}

for(const [i,s] of deck.slides.items.entries()){
  const blob=await deck.export({slide:s,format:'png',scale:1.5});
  await fs.writeFile(path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
  console.log(`render ${i+1}`);
}
await fs.writeFile(path.join(build,'deck.inspect.ndjson'),(await deck.inspect({kind:'slide,textbox,chart,table,notes',maxChars:150000})).ndjson);
const candidatePath=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(deck)).save(candidatePath);
const revision=process.argv[2]||'v1';
if(!/^v\d+$/.test(revision))throw new Error('Usar una revisión como v1 o v2');
const finalPath=path.join(out,`avance_tpm_6_min_${revision}.pptx`);
const report=await finalizePresentation({
  workspaceDir:ROOT,candidatePath,finalPath,
  pythonExecutable:`${RUNTIME}/python/python.exe`,
  integrityValidatorPath:`${SKILL}/container_tools/inspect_presentation_package_integrity.py`,
  layoutValidatorPath:`${SKILL}/container_tools/inspect_presentation_layout_geometry.py`,
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',
    '--require-native-table-slide','2','--require-native-table-slide','7'],
  requiredNativeTableOwnerSlides:[2,7],requiredNativeChartOwnerSlides:[3,4,5],
  materializeLiteralChartWorkbooks:true,
  fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,
  receiptPath:path.join(build,`validation-${revision}.json`),
});
console.log(JSON.stringify({finalPath:report.finalPath,slides:8,layout:report.presentationLayout.findingCount,charts:report.nativeChartValidation.passed,import:report.firstPartyImport.passed}));
