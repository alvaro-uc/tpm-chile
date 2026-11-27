import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = fileURLToPath(new URL('../../', import.meta.url));
const build = path.join(root, '.build/entrega_final');
const out = path.join(root, 'output/entrega_final');
const sdk = process.env.RUNTIME_NODE_MODULES;
const skill = process.env.PRESENTATIONS_SKILL;
const python = process.env.RUNTIME_PYTHON;
if (!sdk || !skill || !python) throw new Error('Configurar el runtime según src/presentation/README.md');
const chartModule = path.join(skill, 'container_tools/artifact_tool_utils.mjs');
const { applyPresentationChartFont, finalizePresentation } = await import(pathToFileURL(chartModule).href);
const { FileBlob, Presentation, PresentationFile } = await import(pathToFileURL(path.join(sdk, '@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const data = JSON.parse(await fs.readFile(path.join(build, 'datos.json'), 'utf8'));
const contenido = JSON.parse(await fs.readFile(new URL('contenido_final.json', import.meta.url), 'utf8'));
const deck = Presentation.create({slideSize:{width:1280,height:720}});
const C = {ink:'#172B42', blue:'#2364AA', green:'#16765B', red:'#B63F45', gray:'#526478',
  light:'#E4EBF3', pale:'#F1F6FB', white:'#FFFFFF', slate:'#74879A'};
const labels = ['Baja','Mantiene','Sube'];
const keys = ['baja','mantiene','sube'];
const colors = [C.green, C.blue, C.red];
const font = 'Arial';
const num = (v, digits=2) => Number(v).toFixed(digits).replace('.', ',');
const round = (v, digits=3) => Number(Number(v).toFixed(digits));
const fechaCorta = v => `${v.slice(8,10)}/${v.slice(5,7)}/${v.slice(0,4)}`;

function text(s,v,x,y,w,h,size=29,color=C.ink,bold=false){
  const box=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  box.text=v;
  box.text.style={typeface:font,fontSize:size,color,bold};
  box.text.insets=0;
  return box;
}
function start(i, sub=''){
  const s=deck.slides.add();
  const item=contenido[i];
  s.background.fill=C.white;
  if(i>0) text(s,item.titulo,62,53,1156,66,47,C.ink,true);
  if(sub) text(s,sub,64,129,1154,46,25,C.gray);
  const notas=item.nota_expositor ? ['Apoyo para el expositor',...item.nota_expositor] : [];
  s.speakerNotes.text=[item.voz+' · '+item.segundos+' s',item.hablado,...notas,
    'Indicación de edición',item.tecnico,'Fuentes',...item.fuentes].join('\n\n');
  return s;
}
function foot(s,v){text(s,v,64,664,1154,30,17,C.gray);}
function table(s, values, x, y, widths, height, options={}){
  const t=s.tables.add({rows:values.length,columns:widths.length,left:x,top:y,
    width:widths.reduce((a,b)=>a+b,0),height,columnWidths:widths,values});
  t.cells.block({row:0,column:0,rowCount:values.length,columnCount:widths.length})
    .assign({margins:{left:11,right:6,top:5,bottom:5}});
  t.borders.assign({fill:C.white,width:0,style:'solid'});
  values.forEach((row,r)=>row.forEach((_,c)=>{
    const cell=t.getCell(r,c);
    const etiqueta=options.etiqueta && c===widths.length-1;
    cell.fill=r===0?(etiqueta?C.blue:C.ink):(etiqueta||options.diagonal&&r===c?C.light:r%2===0?C.pale:C.white);
    cell.text.style={typeface:font,fontSize:options.size??22,color:r===0?C.white:C.ink,
      bold:r===0||c===0||etiqueta||(options.diagonal&&r===c)};
  }));
}
function chart(s,type, config){
  const ch=s.charts.add(type,{chartFill:C.white,plotAreaFill:C.white,chartLine:{fill:'none',width:0},...config});
  applyPresentationChartFont(ch,{fontFamily:font});
  return ch;
}
const axisText={fontSize:20,fill:C.ink};
const grids={fill:C.light,width:1};

// Portada
{
  const s=start(0);
  text(s,'¿Podemos anticipar\nal Banco Central?',62,117,1150,192,74,C.ink,true);
  text(s,'Decisiones de TPM en Chile, 2010–2025',66,339,1150,62,34,C.gray);
  [[64,'Baja',C.green],[260,'Mantiene',C.blue],[545,'Sube',C.red]].forEach(([x,l,c])=>text(s,l,x,449,255,56,35,c,true));
  text(s,'Loreto Cornejo, Fernando Osses, Macarena Pérez y Álvaro Recabarren',66,590,1120,38,25,C.ink);
  foot(s,'IMT2200   Grupo 9   Entrega final');
}

// Distribución por ciclo, escala porcentual
{
  const s=start(1,'Cada anuncio oficial cuenta, incluso cuando la tasa queda en el mismo nivel.');
  const periodos=data.decisiones_por_periodo;
  const n=p=>keys.reduce((sum,k)=>sum+Number(p[k]),0);
  chart(s,'bar',{
    position:{left:64,top:208,width:820,height:402},
    categories:periodos.map(p=>p.periodo),
    series:keys.map((k,i)=>({name:labels[i],fill:colors[i],values:periodos.map(p=>round(Number(p[k])/n(p),5))})),
    hasLegend:true,legend:{position:'bottom',textStyle:axisText},
    barOptions:{direction:'column',grouping:'stacked',overlap:100,gapWidth:55},
    xAxis:{textStyle:axisText},yAxis:{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',textStyle:axisText,majorGridlines:grids},
  });
  text(s,'161',932,232,245,96,72,C.ink,true);
  text(s,'anuncios oficiales',930,318,270,42,27,C.gray);
  text(s,'103 mantenciones\n31 bajas\n27 subidas',930,390,268,132,28,C.ink,true);
  foot(s,'Número de anuncios por bloque de izquierda a derecha: 48, 48, 33 y 32.');
}

// Calendario, ejemplo y cobertura
{
  const s=start(2,'Corte del pronóstico: cierre del día hábil anterior al anuncio.');
  table(s,[
    ['Publicación o anuncio','Fecha','Al corte del 16/10'],
    ['IPC de septiembre','08/10/2024','Disponible · 0,1 %'],
    ['Decisión de TPM','17/10/2024','Resultado de la reunión'],
    ['IPC de octubre','08/11/2024','Posterior al corte'],
  ],66,222,[480,270,398],221,{size:24});
  text(s,'Al cierre del 16 ya se conocía el IPC de septiembre.',66,493,1100,47,30,C.ink,true);
  text(s,'El IPC de octubre apareció después de la decisión.',66,548,1110,48,27,C.gray);
  foot(s,'Fuente: INE, boletines del IPC de septiembre y octubre de 2024.');
}

// Reconstrucción de la información disponible para cada anuncio.
{
  const s=start(3,'¿Cuándo salió cada dato y qué valor se conocía ese día?');
  const respaldo = variable => data.cobertura.find(fila=>fila.variable===variable).n_con_respaldo;
  table(s,[
    ['Indicador','Disponibilidad en el momento del corte'],
    ['IPC (precios)',`${respaldo('ipc_general_mensual')} reuniones con fecha y valor del boletín original`],
    ['IMACEC y desempleo','Las series descargadas pueden incluir correcciones posteriores.'],
    ['Cobre','Serie 2010–2025 de Cochilco. Falta verificar la hora de publicación.'],
    ['Encuesta de expectativas','Faltó cotejar cuándo se publicó cada encuesta.'],
    ['Dólar observado',`Fecha de vigencia oficial. Dato al corte respaldado en ${respaldo('clp_usd')} de 161 anuncios.`],
  ],66,190,[357,791],355,{size:24});
  text(s,'Prueba principal  ·  Historial de la TPM, con y sin dólar',66,576,1145,50,30,C.blue,true);
  foot(s,'Los demás indicadores se usaron en la exploración o en análisis de sensibilidad.');
}

// Tres filas reales del primer bloque, con los cuatro campos del modelo ampliado.
{
  const s=start(4,'Una fila por reunión. A la izquierda, datos al corte. En azul, lo que se busca predecir.');
  const filas=data.muestra_entrenamiento.map(f=>[
    fechaCorta(f.fecha_decision),fechaCorta(f.fecha_corte),num(f.tpm_previa_pct),
    num(f.pb_ultima,0),num(f.pb_ultimas_3,0),num(f.dolar_ret_20),labels[keys.indexOf(f.decision)],
  ]);
  table(s,[['Reunión','Corte','TPM vigente\n(%)','Último cambio\n(p.b.)','Últimos 3\n(suma en p.b.)','Dólar: variación\na 20 cotiz. (%)','Decisión\nreal'],...filas],
    66,212,[139,139,146,171,176,201,176],261,{size:21,etiqueta:true});
  text(s,'Datos de entrada  ·  TPM vigente y cambios pasados',66,514,1149,42,28,C.ink,true);
  text(s,'El segundo modelo también recibe la variación del dólar.',66,562,1149,40,26,C.gray);
  foot(s,'50 puntos base (p.b.) = 0,50 puntos porcentuales. Las fechas identifican cada fila.');
}

// Medianas e intervalo intercuartílico como gráficos de dispersión editables.
{
  const s=start(5,'El punto es la mediana y la línea abarca el 50 % central de cada grupo.');
  const specs=[
    ['dolar_ret_20','Variación del dólar a 20 cotizaciones (%)',64,-4,4,2],
    ['imacec_12m','Actividad económica (IMACEC, cambio anual %)',650,0,10,2],
  ];
  for(const [varId,t,x,min,max,step] of specs){
    const rows=keys.map(k=>data.eda_por_clase.find(r=>r.variable===varId&&r.decision===k));
    const cero=varId==='dolar_ret_20' ? [{name:'0 % · Sin cambio',xValues:[.55,3.45],values:[0,0],
      line:{fill:C.slate,width:2},marker:{symbol:'none'}}] : [];
    text(s,t,x,208,563,35,23,C.ink,true);
    chart(s,'scatter',{
      position:{left:x,top:247,width:558,height:260},hasLegend:false,
      scatterOptions:{style:'lineWithMarkers'},
      xAxis:{min:.55,max:3.45,majorUnit:1,tickLabelPosition:'none',line:{fill:C.slate,width:1}},
      yAxis:{min,max,majorUnit:step,textStyle:axisText,numberFormatCode:'0',majorGridlines:grids},
      series:[...cero,...rows.flatMap((r,i)=>[
        {name:labels[i]+' 50 % central',xValues:[i+1,i+1],values:[round(r.q25),round(r.q75)],
          line:{fill:colors[i],width:4},marker:{symbol:'none'}},
        {name:labels[i]+' mediana',xValues:[i+1],values:[round(r.mediana)],line:{fill:'none',width:0},
          marker:{symbol:'circle',size:12,fill:colors[i]}},
      ])],
    });
    rows.forEach((r,i)=>{
      const left=x+42+i*176;
      text(s,labels[i]+'  '+num(r.mediana),left,519,146,32,20,colors[i],true).text.alignment='center';
      text(s,'n = '+r.n,left,552,146,27,18,C.gray).text.alignment='center';
    });
  }
  text(s,'Los tres intervalos incluyen el cero.',64,609,556,35,23,C.ink,true);
  text(s,'Mayor crecimiento en el grupo de alzas.',650,609,560,35,23,C.ink,true);
  foot(s,'Primeras 60 reuniones ordinarias. El IMACEC descargado puede incluir revisiones publicadas después.');
}

// Evaluación
{
  const s=start(6,'Después de conocer una decisión, la agregamos para entrenar el siguiente pronóstico.');
  const [primero,segundo]=data.inicio_prueba;
  text(s,'60',65,210,440,98,73,C.ink,true);
  text(s,'reuniones iniciales',67,310,500,46,30,C.ink,true);
  text(s,'Enero 2010 – diciembre 2014',68,369,510,41,24,C.gray);
  text(s,`${fechaCorta(primero.fecha_decision)} con ${primero.n_train}  ·  ${fechaCorta(segundo.fecha_decision)} con ${segundo.n_train}`,
    68,420,550,43,24,C.ink,true);
  text(s,'100',660,210,520,98,73,C.blue,true);
  text(s,'pronósticos de una reunión',661,310,535,46,30,C.ink,true);
  text(s,'Enero 2015 – diciembre 2025',662,369,510,41,24,C.gray);
  text(s,'21 bajas    64 mantenciones    15 subidas',662,420,525,43,25,C.ink,true);
  text(s,'Mayoría  ·  Elige la decisión más frecuente',67,512,560,39,24,C.ink,true);
  text(s,'Persistencia  ·  Repite la última decisión',67,561,560,39,24,C.ink,true);
  text(s,'Logística  ·  Elige la clase más probable',662,512,550,39,24,C.ink,true);
  text(s,'Dos versiones: historial de la TPM, con y sin dólar',662,561,544,39,23,C.gray);
  foot(s,'Se evalúan reuniones ordinarias. La reunión extraordinaria de 2020 se conserva en el historial.');
}

// Métrica principal
{
  const s=start(7,'Puntaje de 0 a 1 · Bajas, mantenciones y alzas cuentan por igual');
  const rows=data.metricas.slice(0,4);
  chart(s,'bar',{
    position:{left:65,top:186,width:1148,height:359},
    categories:rows.map(r=>r.modelo),
    series:[{name:'F1 macro',values:rows.map(r=>round(r.f1_macro)),valuesFormatCode:'0.000',
      fill:C.blue,points:[{idx:0,fill:'#9DADBD'},{idx:1,fill:C.slate},{idx:2,fill:'#7EADD2'},{idx:3,fill:C.blue}]}],
    barOptions:{direction:'column',grouping:'clustered',gapWidth:110},
    hasLegend:false,xAxis:{textStyle:{...axisText,fontSize:25}},
    yAxis:{min:0,max:1,majorUnit:.25,numberFormatCode:'0.00',textStyle:axisText,majorGridlines:grids},
    dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:26,fill:C.ink,bold:true}},
  });
  text(s,'F1 macro  ·  Promedio del F1 de bajas, mantenciones y alzas',65,555,1154,40,25,C.ink,true);
  text(s,'Mayoría histórica: 64 % de aciertos, todos en mantenciones.',65,607,1154,36,24,C.gray);
  foot(s,'Cuatro métodos evaluados sobre las mismas 100 reuniones.');
}

// Matrices
{
  const s=start(8,'Filas: lo que ocurrió · Columnas: lo que se pronosticó · Sombreado: aciertos');
  const nombres=['Persistencia','Logística TPM + dólar'];
  nombres.forEach((nombre,i)=>{
    const x=i===0?66:652;
    text(s,nombre,x,210,550,51,30,C.ink,true);
    const m=data.matrices[nombre];
    table(s,[['Real / pronóstico',...labels],...m.map((fila,i)=>[labels[i],...fila.map(String)])],
      x,284,[168,117,146,115],210,{size:21,diagonal:true});
    text(s,'Bajas '+m[0][0]+'/21     Subidas '+m[2][2]+'/15',x,538,546,45,26,C.ink,true);
  });
  foot(s,'De las 21 bajas reales, la logística con dólar pronosticó baja en 10 y mantención en 11.');
}

// Sensibilidad EEE
{
  const s=start(9,'Regla aparte: si la tasa esperada a fin de mes es menor que la vigente, pronostica baja.');
  const eee=data.sensibilidad_eee;
  text(s,'Ejemplo  ·  4,75 % esperado frente a 5,00 % vigente da un pronóstico de baja.',66,205,1148,49,26,C.ink,true);
  table(s,[
    ['Encuesta utilizada','F1 macro','Disponibilidad asumida'],
    ['Mes anterior en todos los cortes',num(eee[0].f1_macro,3),'Referencia con un mes de rezago'],
    ['Mes actual si el corte es el 13 o después',num(eee[1].f1_macro,3),'Antes del día 13 se usa el mes anterior.'],
  ],66,276,[467,153,528],189,{size:23});
  text(s,'Misma regla y mismas 100 reuniones. Cambia la encuesta que se usa.',68,507,1120,46,27,C.ink,true);
  text(s,'La EEE quedó fuera del modelo principal. Faltó cotejar las fechas reales.',68,570,1110,46,24,C.gray);
  foot(s,'Encuesta de Expectativas Económicas del Banco Central, serie F089.TPM.TAS.11.M.');
}

// Cierre
{
  const s=start(10,'F1 macro sobre las mismas 100 reuniones ordinarias');
  data.metricas.slice(1,4).forEach((fila,i)=>{
    const x=66+i*386;
    text(s,num(fila.f1_macro,3),x,224,360,100,72,i===2?C.blue:C.ink,true);
    text(s,fila.modelo,x+3,325,365,55,28,C.ink);
  });
  text(s,'Repetir la última decisión fue difícil de superar.',67,456,1148,53,35,C.ink,true);
  text(s,'Para evaluar otros indicadores faltan sus publicaciones originales y sus fechas.',67,542,1148,58,27,C.gray);
  foot(s,'Una fila por reunión y una evaluación que respeta el corte de cada anuncio.');
}

await fs.mkdir(out,{recursive:true});
const candidatePath=path.join(build,'candidato.pptx');
const filename=process.argv[2]||'presentacion_tpm_final.pptx';
if(!/^[a-z0-9_]+\.pptx$/i.test(filename)) throw new Error('El nombre debe ser un archivo PPTX en output/entrega_final');
const finalPath=path.join(out,filename);
await (await PresentationFile.exportPptx(deck)).save(candidatePath);
const tableOwners=[3,4,5,9,10];
const report=await finalizePresentation({
  workspaceDir:root,candidatePath,finalPath,pythonExecutable:python,
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',
    ...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],
  explicitTotalSlideCount:contenido.length,
  requiredNativeTableOwnerSlides:tableOwners,requiredNativeChartOwnerSlides:[2,6,8],
  materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[font]},
  verifyArtifactToolImport:true,receiptPath:path.join(build,path.parse(filename).name+'.validacion.json'),
});
console.log(report.finalPath);

const finalDeck=await PresentationFile.importPptx(await FileBlob.load(finalPath));
for(const [i,s] of finalDeck.slides.items.entries()){
  const blob=await finalDeck.export({slide:s,format:'png',scale:1.5});
  const name='slide-'+String(i+1).padStart(2,'0')+'.png';
  await fs.writeFile(path.join(build,name),new Uint8Array(await blob.arrayBuffer()));
}
