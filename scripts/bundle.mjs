import { createHash } from 'node:crypto';
import { brotliCompressSync, constants } from 'node:zlib';
import { readFileSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const [dist, out] = process.argv.slice(2);
const names = readdirSync(dist).filter((name) => statSync(join(dist, name)).isFile()).sort();
const payload = [];
const files = [];
let offset = 0;
for (const name of names) {
  const path = join(dist, name);
  const raw = readFileSync(path);
  files.push({ name, offset, bytes: raw.length, sha256: createHash('sha256').update(raw).digest('hex') });
  payload.push(raw);
  offset += raw.length;
  rmSync(path);
}
const header = Buffer.from(JSON.stringify({ format: 'pyodide-minimal/1', files }));
const length = Buffer.alloc(4);
length.writeUInt32LE(header.length);
const plain = Buffer.concat([length, header, ...payload]);
const packed = brotliCompressSync(plain, {
  params: {
    [constants.BROTLI_PARAM_QUALITY]: constants.BROTLI_MAX_QUALITY,
    [constants.BROTLI_PARAM_LGWIN]: 24,
    [constants.BROTLI_PARAM_SIZE_HINT]: plain.length,
  },
});
writeFileSync(out, packed);
console.log(JSON.stringify({ files: files.length, plain_bytes: plain.length, brotli_bytes: packed.length }));
