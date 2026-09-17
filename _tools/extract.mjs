// Extract text from a PDF using pdfjs-dist (legacy build, Node).
// Usage: node _tools/extract.mjs <file.pdf> <out.txt>
import { getDocument } from 'pdfjs-dist/legacy/build/pdf.mjs';
import fs from 'node:fs';

const [, , inPath, outPath] = process.argv;

const data = new Uint8Array(fs.readFileSync(inPath));
const doc = await getDocument({ data, useSystemFonts: true, isEvalSupported: false }).promise;
const chunks = [];
for (let p = 1; p <= doc.numPages; p++) {
  const page = await doc.getPage(p);
  const content = await page.getTextContent();
  let lastY = null;
  let line = '';
  const lines = [];
  for (const item of content.items) {
    if (!('str' in item)) continue;
    const y = item.transform[5];
    if (lastY === null || Math.abs(y - lastY) > 2.5) {
      if (line.trim()) lines.push(line.replace(/\s+$/, ''));
      line = '';
      lastY = y;
    }
    line += item.str;
    if (item.hasEOL) { lines.push(line.replace(/\s+$/, '')); line = ''; lastY = null; }
  }
  if (line.trim()) lines.push(line.replace(/\s+$/, ''));
  chunks.push(`===== PAGE ${p} =====\n` + lines.join('\n'));
}
await doc.destroy();
fs.writeFileSync(outPath, chunks.join('\n\n'), 'utf8');
console.log('pages:', doc.numPages ?? 'done', '→', outPath);
