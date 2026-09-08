import fs from 'node:fs/promises';
import validator from 'gltf-validator';
for (const device of ['switch','switch2']) {
  const bytes = new Uint8Array(await fs.readFile(new URL(`../site/public/models/${device}.glb`,import.meta.url)));
  const report = await validator.validateBytes(bytes,{uri:`${device}.glb`,maxIssues:30});
  console.log(`${device}: ${report.issues.numErrors} errors, ${report.issues.numWarnings} warnings`);
  if (report.issues.numErrors) { console.error(report.issues.messages); process.exitCode = 1; }
}
