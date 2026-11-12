#!/usr/bin/env python3
"""Idempotent GitHub-private workspace bootstrap for existing Conde animal roster.

No network or mutation by default. --apply requires explicit owner confirmation
and a repository-scoped GITHUB_TOKEN or GH_TOKEN in the environment. Never
commit credentials or transfer them into the workspaces.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "config" / "agent-roster.json"
API = "https://api.github.com"
USER_AGENT = "conde-agent-workspace-provisioner/1"


class ProvisionError(RuntimeError):
    pass


def read_roster(path: Path = ROSTER) -> tuple[str, list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    owner = data["owner"]
    agents = data["agents"]
    if not re.fullmatch(r"[A-Za-z0-9-]+", owner):
        raise ProvisionError("Invalid owner slug")
    if not agents or len({a["slug"] for a in agents}) != len(agents):
        raise ProvisionError("Empty or duplicate animal roster")
    for animal in agents:
        slug = animal["slug"]
        if not re.fullmatch(r"[a-z]+", slug):
            raise ProvisionError(f"Invalid lowercase Portuguese animal slug {slug!r}")
        if animal["workspace"] != f"{owner}/{slug}" or animal["expected_visibility"] != "private":
            raise ProvisionError(f"Workspace owner/privacy mismatch: {slug}")
    return owner, agents


def gitignore() -> str:
    return """.env
.env.*
*.pem
*.key
*.p12
*.pfx
.secrets/
.auth/
.venv/
node_modules/
__pycache__/
*.pyc
*.token
tokens.json
"""


def okf_doc(kind: str, title: str, description: str, body: str, **extra: str) -> str:
    """Make generated Markdown valid OKF, including GitHub issue templates."""
    fields = {"type": kind, "title": title, "description": description, **extra}
    header = "\n".join(
        f"{key}: {json.dumps(value, ensure_ascii=False)}"
        for key, value in fields.items()
    )
    return f"---\n{header}\n---\n\n{body.strip()}\n"


def bootstrap_files(owner: str, animal: dict) -> dict[str, str]:
    slug, role, emoji = animal["slug"], animal["role"], animal["emoji"]
    skill_path = ROOT / ".agents" / "skills" / f"conde-{slug}" / "SKILL.md"
    if not skill_path.is_file():
        raise ProvisionError(f"Project skill missing for {slug}: {skill_path}")
    display = slug.title() if slug != "gaviao" else "Gavião"
    readme = f"""# {emoji} {display} · workspace pessoal privado

Agente: {role}

Este repositório é a casa permanente do agente, **separada dos projetos**.
O dono pode escrever, experimentar, organizar arquivos e fazer push diretamente,
sem PR ou aprovação dos demais agentes. Código compartilhado ou científico
entra nos repositórios de projeto por PRs pequenas, CI e merge seguro.

Projeto atual: https://github.com/{owner}/conde-incident .
**Caixa de entrada:** Issues deste repositório. Outros animais pedem ajuda
abrindo uma issue aqui; responder e fechar quando concluído.
"""
    contract = f"""# {emoji} {display} · contrato do espaço pessoal

Este é o repositório **privado de trabalho permanente** de {display}.
- Responsável: {emoji} {display}; propósito: {role}.
- Pode instalar ferramentas, guardar notas, scripts, experimentos, skills,
  memórias OKF e fazer **push direto** sem pedir aprovação prévia.
- No início de cada sessão, verificar Issues abertas, skill e memória anterior.
- Em cada sessão, manter um registro conciso em memory/: decisões,
  evidências, resultados negativos, links para commits/PRs e próximo passo.
- Para comunicar-se com outro animal: abrir Issue no repositório privado
  {owner}/<destinatario> e incluir remetente, projeto, evidências e pedido.
  Não escrever em repositório de colega apenas para enviar recado.
- Código destinado a projetos deve ir para PR no repositório de projeto.
- Não colocar segredos, tokens, chaves ou dados pessoais sensíveis no Git,
  mesmo quando privado.
- Uma nota ou hipótese nunca se transforma em observação por ter sido
  guardada aqui. Preserve proveniência e incertezas.
"""
    project_skill = skill_path.read_text(encoding="utf-8")
    skill_body = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", project_skill, count=1, flags=re.S)
    if skill_body == project_skill:
        raise ProvisionError(f"Project skill lacks frontmatter: {skill_path}")
    issue_body = """**De (animal):**

**Para (animal proprietário deste repositório):**

**Projeto / PR / issue relacionado:**

**Tipo:** colaboração | bloqueio | crítica | evidência | pergunta

**Contexto / fonte (ID, ocorrência, URL, SHA, unidade, erro):**

**Pedido ou sugestão concreta:**

**Resultado esperado:**
"""
    files = {
        "README.md": okf_doc("Workspace", f"{emoji} {display}", role, readme),
        "AGENTS.md": okf_doc(
            "AgentContract", f"{emoji} {display} · contrato pessoal",
            f"Governança e segurança do workspace privado de {display}.", contract
        ),
        ".gitignore": gitignore(),
        f".agents/skills/conde-{slug}/SKILL.md": okf_doc(
            "Skill", f"{emoji} {display} · skill pessoal",
            f"Método e especialidade de {display}: {role}.",
            skill_body, name=f"conde-{slug}"
        ),
        ".github/ISSUE_TEMPLATE/message.md": okf_doc(
            "IssueTemplate", "[recado] remetente → destinatário: ",
            "Pedido de colaboração, pergunta, bloqueio ou evidência.",
            issue_body, name="Mensagem entre animais",
            about="Pedido de colaboração, pergunta, bloqueio ou evidência.",
            labels="", assignees=""
        ),
        "memory/README.md": okf_doc(
            "WorkspaceNote", "Memórias OKF",
            "Registros cumulativos privados do agente.",
            "# Memórias OKF\n\nUm registro por sessão ou decisão, sem apagar história."
        ),
        "tools/README.md": okf_doc(
            "WorkspaceNote", "Ferramentas",
            "Scripts pessoais e experimentos privados do agente.",
            "# Ferramentas\n\nFerramentas pessoais, sem necessidade de PR."
        ),
        "experiments/README.md": okf_doc(
            "WorkspaceNote", "Experimentos",
            "Experimentos reproduzíveis e limites do conhecimento.",
            "# Experimentos\n\nSeparar simulações, resultados negativos e observações."
        ),
    }
    # Every generated Markdown, including hidden templates and the specs
    # themselves, must be covered by a normative .okf/specs/{slug}.md.
    for kind in ("Workspace", "AgentContract", "Skill", "IssueTemplate", "WorkspaceNote", "Spec"):
        files[f".okf/specs/{kind.lower()}.md"] = okf_doc(
            "Spec", f"Especificação {kind}", f"Contrato OKF de {kind}",
            f"# Tipo {kind}\n\nExige type, title e description; preservar chaves adicionais."
        )
    if any(len(content.encode("utf-8")) > 20_000 for content in files.values()):
        raise ProvisionError(f"Generated workspace file exceeds 20,000 bytes: {slug}")
    return files


class GitHubAPI:
    def __init__(self, token: str):
        if not token:
            raise ProvisionError("Missing GITHUB_TOKEN/GH_TOKEN; required only for --apply")
        self.headers = {
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
        }

    def request(self, method: str, path: str, payload: dict | None = None) -> tuple[int, Any]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = Request(API + path, headers=self.headers, data=body, method=method)
        try:
            with urlopen(req, timeout=25) as response:
                raw = response.read()
                return response.status, json.loads(raw) if raw else {}
        except HTTPError as err:
            raw = err.read()
            try:
                message = json.loads(raw).get("message", "GitHub request failed")
            except (ValueError, UnicodeDecodeError):
                message = "GitHub request failed"
            return err.code, {"message": str(message)[:180]}
        except URLError as err:
            raise ProvisionError(f"GitHub connection failure: {type(err.reason).__name__}") from err

    def ensure_repo(self, owner: str, animal: dict) -> str:
        slug = animal["slug"]
        name = f"{owner}/{slug}"
        status, repo = self.request("GET", "/repos/" + name)
        if status == 404:
            status, repo = self.request(
                "POST",
                "/user/repos",
                {
                    "name": slug,
                    "description": f"Workspace pessoal privado {animal['emoji']} {slug}: {animal['role']}",
                    "private": True,
                    "has_issues": True,
                    "has_wiki": False,
                    "has_projects": False,
                    "auto_init": True,
                },
            )
            if status != 201:
                raise ProvisionError(f"Cannot create {name}: HTTP {status}: {repo.get('message')}")
            action = "CREATED"
        elif status == 200:
            action = "REUSED"
        else:
            raise ProvisionError(f"Cannot inspect {name}: HTTP {status}: {repo.get('message')}")
        if repo.get("owner", {}).get("login") != owner:
            raise ProvisionError(f"Owner mismatch for {name}")
        if repo.get("private") is not True or repo.get("has_issues") is not True:
            raise ProvisionError(f"{name} exists but privacy or Issues requirement is not met")
        return action

    def ensure_file(self, owner: str, slug: str, path: str, text: str) -> str:
        uri = "/repos/" + owner + "/" + slug + "/contents/" + quote(path, safe="/")
        status, item = self.request("GET", uri)
        if status == 200:
            return "EXISTS_UNCHANGED"
        if status != 404:
            raise ProvisionError(f"Cannot inspect {slug}/{path}: HTTP {status}")
        payload = {
            "message": f"chore(workspace): bootstrap {path}",
            "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
        }
        status, response = self.request("PUT", uri, payload)
        if status not in (200, 201):
            raise ProvisionError(
                f"Cannot create {slug}/{path}: HTTP {status}: {response.get('message')}"
            )
        return "CREATED"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Create missing PRIVATE GitHub repos")
    parser.add_argument("--confirm-owner", default="", help="Must match roster owner on --apply")
    parser.add_argument("--roster", type=Path, default=ROSTER)
    args = parser.parse_args()
    owner, agents = read_roster(args.roster)
    if not args.apply:
        print(json.dumps({
            "status": "DRY_RUN_NO_NETWORK_NO_MUTATION",
            "owner": owner,
            "total": len(agents),
            "requested_repos": [a["workspace"] for a in agents],
            "private": True,
        }, ensure_ascii=False))
        return 0
    if args.confirm_owner != owner:
        raise ProvisionError("--confirm-owner must exactly match the roster owner")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    api = GitHubAPI(token or "")
    status, me = api.request("GET", "/user")
    if status != 200 or me.get("login") != owner:
        raise ProvisionError("Authenticated GitHub owner does not match roster owner")
    completed = []
    for animal in agents:
        slug = animal["slug"]
        repo_action = api.ensure_repo(owner, animal)
        files = bootstrap_files(owner, animal)
        created = []
        for path, content in files.items():
            result = api.ensure_file(owner, slug, path, content)
            if result == "CREATED":
                created.append(path)
        # Verify after writes; do not claim success from POST alone.
        code, state = api.request("GET", f"/repos/{owner}/{slug}")
        if code != 200 or state.get("private") is not True or not state.get("has_issues"):
            raise ProvisionError(f"Private/Issues re-verification failed: {owner}/{slug}")
        record = {"repository": state["full_name"], "private": state["private"],
                  "issues_enabled": state["has_issues"], "action": repo_action,
                  "created_files": created}
        completed.append(record)
        print(json.dumps(record, ensure_ascii=False))
    print(json.dumps({"status": "VERIFIED", "count": len(completed)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProvisionError as exc:
        print("ERROR:", exc)
        raise SystemExit(1)
