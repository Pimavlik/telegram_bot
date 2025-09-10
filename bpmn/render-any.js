const fs = require('fs');
const path = require('path');
const { layoutProcess } = require('bpmn-auto-layout');
const { convert } = require('bpmn-to-image');

async function main() {
  const inputArg = process.argv[2];
  if (!inputArg) {
    console.error('Usage: node bpmn/render-any.js <input.bpmn>');
    process.exit(2);
  }

  const inputPath = path.resolve(process.cwd(), inputArg);
  const xml = fs.readFileSync(inputPath, 'utf8');
  const laidOutXml = await layoutProcess(xml);

  const parsed = path.parse(inputPath);
  const laidOutPath = path.join(parsed.dir, parsed.name + '.laidout.bpmn');
  const outputPath = path.join(parsed.dir, parsed.name + '.png');

  fs.writeFileSync(laidOutPath, laidOutXml, 'utf8');
  await convert(laidOutPath, outputPath);
  console.log('PNG written to:', outputPath);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

