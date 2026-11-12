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
  assert.equal(a.workspace_status,'PRIVATE_REPO_VERIFIED_BOOTSTRAP_PARTIAL');
 }
 assert.equal(roster.workspace_provisioning,'PRIVATE_REPOS_VERIFIED_BOOTSTRAP_PARTIAL');
 assert.equal(roster.workspace_verification_date,'2026-11-12');
 assert.match(roster.workspace_verification_scope,/Bootstrap completeness.*not yet established/);

});
test('new agents have explicit cards and skills',()=>{
 for(const a of roster.agents.slice(8)){
  assert.match(read(`team/${a.slug}.md`), /Repositório pessoal privado/);
  assert.match(read(`.agents/skills/conde-${a.slug}/SKILL.md`), /repositório privado/);
 }
});
test('verified private repos are distinguished from completed bootstrap',()=>{
 const s=read('docs/AGENT_WORKSPACES.md');
 const agents=read('AGENTS.md');
 assert.match(s,/13 repositórios passaram a existir/);
 assert.match(s,/bootstrap esteja completo/);
 assert.match(s,/private=true/);
 assert.match(s,/has_issues=true/);
 assert.match(s,/castor\/issues\/1/);
 assert.match(agents,/scaffold ainda está \*\*parcial\*\*/);
 assert.doesNotMatch(s,/NENHUM novo repositório é declarado criado/);
});
