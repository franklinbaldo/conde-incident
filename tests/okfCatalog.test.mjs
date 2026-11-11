import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const dir=path.join("knowledge","records");
const files=fs.readdirSync(dir).filter(x=>x.endsWith(".md"));
function field(text,key){const m=text.match(new RegExp("^"+key+":\\s*(.+)$","m"));if(!m)return undefined;try{return JSON.parse(m[1]);}catch{return m[1];}}
function data(file){const text=fs.readFileSync(path.join(dir,file),"utf8");return {text,id:field(text,"id"),type:field(text,"type"),verification:field(text,"verification"),source_url:field(text,"source_url"),rodada:field(text,"rodada")};}
const cards=Object.fromEntries(files.map(f=>[f,data(f)]));
test("todo conceito possui identidade, fonte e grau declarado",()=>{const ids=new Set();for(const [f,c] of Object.entries(cards)){for(const key of ["id","type","verification","source_url","rodada"])assert.ok(c[key],f+" falta "+key);assert.ok(!ids.has(c.id),"ID duplicado: "+c.id);ids.add(c.id);assert.ok(["VERIFIED_REPO","REPORTED_REPO","HYPOTHESIS","NOT_RUN"].includes(c.verification),f+" classe invalida");assert.ok(c.source_url.startsWith("https://"),f+" sem URL");}});
test("cada registro desta rodada aponta ao respectivo registro totalizante",()=>{const rounds=Object.values(cards).filter(c=>c.type==="Rodada");assert.equal(rounds.length,1);const round=rounds[0];for(const [file,c] of Object.entries(cards)){assert.equal(c.rodada,round.id);if(c.type!=="Rodada")assert.ok(round.text.includes("("+file+")"),"faltou na rodada: "+file);}});
test("c240 e c241 continuam conflito aberto sem inferir queda",()=>{const c=cards["conflito-c240-c241.md"].text;assert.ok(c.includes("ABERTO"));assert.ok(c.includes("colisao_de_identificadores"));const h=cards["hipotese-nexo-conde.md"];assert.equal(h.verification,"HYPOTHESIS");});
test("nao confundir declaracao de PR com replay comprovado",()=>{const e=cards["ensaio-matriz-colisao.md"];assert.equal(e.verification,"REPORTED_REPO");assert.ok(e.text.includes("PASS_REPORTED_BY_PR_NOT_RECHECKED"));});
