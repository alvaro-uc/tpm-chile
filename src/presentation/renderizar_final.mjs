import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const runtime='C:/Users/56974/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const {PresentationFile,FileBlob}=await import(pathToFileURL(`${runtime}/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs`).href);
const revision=process.argv[2]||'v1';
const file=path.resolve(`output/presentacion/avance_tpm_6_min_${revision}.pptx`);
const p=await PresentationFile.importPptx(await FileBlob.load(file));
const out=path.resolve('.build/presentacion/final');await fs.mkdir(out,{recursive:true});
for(const [i,slide]of p.slides.items.entries()){
  const blob=await p.export({slide,format:'png',scale:1.5});
  await fs.writeFile(path.join(out,`slide-${i+1}.png`),new Uint8Array(await blob.arrayBuffer()));
}
console.log(`Render final: ${p.slides.items.length} diapositivas`);
