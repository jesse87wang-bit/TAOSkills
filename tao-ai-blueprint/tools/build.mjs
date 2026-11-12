// 用法：node tools/build.mjs configs/<公司>.js [输出目录]
// 输出：<输出目录>/<简称>AI运转全景.html、<简称>AI全貌蓝图.html（单文件，可离线双击打开）
import { build } from 'esbuild';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const cfgPath = resolve(process.argv[2] || '');
if (!existsSync(cfgPath)) { console.error('找不到配置文件：' + cfgPath); process.exit(1); }
const out = resolve(process.argv[3] || 'out');
mkdirSync(out, { recursive: true });
const CFG = (await import(pathToFileURL(cfgPath).href + '?t=' + Date.now())).default;

async function bundle(entrySrc) {
  const r = await build({
    stdin: { contents: entrySrc, resolveDir: root, loader: 'js' },
    bundle: true, minify: true, format: 'iife', write: false, logLevel: 'warning',
    nodePaths: [resolve(root, 'node_modules')],
  });
  return r.outputFiles[0].text.replace(/<\/script/g, '<\\/script');
}
const cfgImport = JSON.stringify(cfgPath);

// 1) 3D AI 运转全景
const js3d = await bundle(`import CFG from ${cfgImport}; import { run } from './engine/engine3d.js'; run(CFG);`);
const tpl3d = readFileSync(resolve(root, 'engine/template3d.html'), 'utf8');
const f3d = resolve(out, `${CFG.shortName}AI运转全景.html`);
writeFileSync(f3d, tpl3d.replace('<title>AI 运转全景</title>', `<title>${CFG.shortName} AI 运转全景</title>`).replace('<script>/*BUNDLE*/</script>', `<script>${js3d}</script>`));

// 2) AI 全貌蓝图
if (CFG.blueprint) {
  const jsbp = await bundle(`import CFG from ${cfgImport}; import { render } from './engine/blueprint.js'; render(CFG);`);
  const tplbp = readFileSync(resolve(root, 'engine/template-blueprint.html'), 'utf8');
  const fbp = resolve(out, `${CFG.shortName}AI全貌蓝图.html`);
  writeFileSync(fbp, tplbp.replace('<title>AI 全貌</title>', `<title>${CFG.shortName} AI 全貌</title>`).replace('<script>/*BUNDLE*/</script>', `<script>${jsbp}</script>`));
  console.log('已生成：', fbp);
}
console.log('已生成：', f3d);
