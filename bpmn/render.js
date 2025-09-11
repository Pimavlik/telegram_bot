const fs = require('fs');
const path = require('path');
const { layoutProcess } = require('bpmn-auto-layout');
const { convert } = require('bpmn-to-image');

async function main() {
  const inputPath = path.resolve(__dirname, 'lenta-shopping.bpmn');
  const outputPath = path.resolve(__dirname, 'lenta-shopping.png');
  const xml = fs.readFileSync(inputPath, 'utf8');

  // Auto layout to ensure DI exists
  const laidOutXml = await layoutProcess(xml);
  const laidOutPath = path.resolve(__dirname, 'lenta-shopping.laidout.bpmn');
  fs.writeFileSync(laidOutPath, laidOutXml, 'utf8');

  // Render to PNG using headless Chromium
  await convert(laidOutPath, outputPath);

  console.log('PNG written to:', outputPath);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

