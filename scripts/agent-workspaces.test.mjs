import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const root=new URL('../',import.meta.url);
const read=(p)=>readFileSync(new URL(p,root),'utf8');
const roster=JSON.parse(read('config/agent-roster.json'));
test('13 unique Portuguese-lowercase private-workspace slugs',()=>{
 assert.equal(roster.agents.length,13);
 assert.equal(new Set(roster.agents.map(a=>a.slug)).size,13);
 for(const a of roster.agents){
  assert.match(a.slug,/^[a-z]+$/);
  assert.equal(a.workspace,`franklinbaldo/${a.slug}`);
  assert.equal(a.expected_visibility,'private');
  assert.equal(a.workspace_status,'PENDING_PROVISIONING');
 }
 assert.equal(roster.workspace_provisioning,'BLOCKED_NOT_CREATED');
});
test('new agents have explicit cards and skills',()=>{
 for(const a of roster.agents.slice(8)){
  assert.match(read(`team/${a.slug}.md`), /Repositório pessoal privado/);
  assert.match(read(`.agents/skills/conde-${a.slug}/SKILL.md`), /repositório privado/);
 }
});
test('protocol does not silently promote pending private repos to reality',()=>{
 const s=read('docs/AGENT_WORKSPACES.md');
 assert.match(s,/NENHUM novo repositório é declarado criado/);
 assert.match(s,/GitHub Issues/);
 assert.match(s,/private=true/);
 assert.match(s,/push diretamente/);
});
