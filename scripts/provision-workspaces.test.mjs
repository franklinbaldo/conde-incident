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


test('every provisioned Markdown is normative OKF with a matching type spec', () => {
  const py = [
    'import json,sys',
    'sys.path.insert(0, sys.argv[1])',
    'import provision_agent_workspaces as p',
    'owner, agents = p.read_roster()',
    'print(json.dumps({a["slug"]: p.bootstrap_files(owner, a) for a in agents}, ensure_ascii=False))'
  ].join('\n');
  const result = spawnSync('python3', ['-c', py, new URL('../tools/', import.meta.url).pathname], {
    encoding: 'utf8', timeout: 10000, maxBuffer: 4 * 1024 * 1024
  });
  assert.equal(result.status, 0, result.stderr);
  const workspaces = JSON.parse(result.stdout);
  assert.equal(Object.keys(workspaces).length, roster.agents.length);
  for (const [slug, files] of Object.entries(workspaces)) {
    assert.ok(files['tools/README.md'] && files['experiments/README.md'], slug);
    assert.ok(files['.github/ISSUE_TEMPLATE/message.md'], slug);
    for (const [path, content] of Object.entries(files)) {
      assert.ok(Buffer.byteLength(content, 'utf8') <= 20_000, slug + '/' + path + ' too large');
      if (!path.endsWith('.md')) continue;
      assert.ok(content.startsWith('---\n'), slug + '/' + path + ' missing frontmatter');
      const front = content.split('---\n')[1];
      const type = front.match(/^type: "([^"]+)"$/m)?.[1];
      assert.ok(type, slug + '/' + path + ' missing OKF type');
      assert.match(front, /^title: ".+"$/m, slug + '/' + path + ' missing title');
      assert.match(front, /^description: ".+"$/m, slug + '/' + path + ' missing description');
      assert.ok(files['.okf/specs/' + type.toLowerCase() + '.md'],
        slug + '/' + path + ' missing spec for ' + type);
    }
    const issue = files['.github/ISSUE_TEMPLATE/message.md'];
    assert.match(issue, /^name: "Mensagem entre animais"$/m);
    assert.match(issue, /^about: /m);
    assert.match(issue, /^labels: /m);
    assert.match(files['.agents/skills/conde-' + slug + '/SKILL.md'], /^name: "conde-/m);
  }
});
