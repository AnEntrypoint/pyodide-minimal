import { createHash } from 'node:crypto';
import { brotliCompressSync, constants } from 'node:zlib';
import { readFileSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const [dist] = process.argv.slice(2);
const files = [];
for (const name of readdirSync(dist).sort()) {
  const path = join(dist, name);
  if (!statSync(path).isFile()) continue;
  const raw = readFileSync(path);
  const packed = brotliCompressSync(raw, {
    params: {
      [constants.BROTLI_PARAM_QUALITY]: constants.BROTLI_MAX_QUALITY,
      [constants.BROTLI_PARAM_SIZE_HINT]: raw.length,
    },
  });
  writeFileSync(path + '.br', packed);
  rmSync(path);
  files.push({ name, sha256: createHash('sha256').update(raw).digest('hex'), bytes: raw.length, brotli_bytes: packed.length });
}
writeFileSync(join(dist, 'manifest.json'), JSON.stringify({ files }, null, 2) + '\n');
