import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';

const script=new URL('../tools/provision_agent_workspaces.py',import.meta.url);
const roster=JSON.parse(readFileSync(new URL('../config/agent-roster.json',import.meta.url),'utf8'));

test('bootstrap defaults to an inert 13-repo plan, with no auth or network',()=>{
  const result=spawnSync('python3',[script.pathname],{encoding:'utf8',timeout:10000});
  assert.equal(result.status,0,result.stderr);
  const data=JSON.parse(result.stdout);
  assert.equal(data.status,'DRY_RUN_NO_NETWORK_NO_MUTATION');
  assert.equal(data.total,13);
  assert.equal(data.owner,'franklinbaldo');
  assert.deepEqual(data.requested_repos,roster.agents.map(a=>a.workspace));
  assert.equal(data.private,true);
});

test('apply needs owner confirmation and a token, never defaults to mutation',()=>{
  const result=spawnSync('python3',[script.pathname,'--apply'],{encoding:'utf8',timeout:10000,
    env:{PATH:process.env.PATH||'/usr/bin:/bin'}});
  assert.notEqual(result.status,0);
  assert.match(result.stdout,/--confirm-owner/);
});

test('private workspace scaffold is present and bounded in the provisioner',()=>{
  const source=readFileSync(script,'utf8');
  assert.match(source,/"private": True/);
  assert.match(source,/"has_issues": True/);
  assert.match(source,/EXISTS_UNCHANGED/);
  assert.match(source,/GitHubAPI\(token or ""\)/);
  assert.doesNotMatch(source,/print\(token\)/);
  assert.match(source,/expected_visibility/);
});
