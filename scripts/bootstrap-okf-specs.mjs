import fs from "node:fs";
import path from "node:path";

const policies = {
  "Fonte": {
    "description": "Objeto documental ou conjunto de dados, com proveniencia e custodia; nao implica autenticacao do conteudo.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "categoria",
      "identificador",
      "custodia",
      "integridade"
    ]
  },
  "Extrato": {
    "description": "Transcricao ou recorte literal de uma fonte localizada; nao cria observacao independente.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "fonte",
      "localizador",
      "texto_literal"
    ]
  },
  "Afirmacao": {
    "description": "Proposicao atomica verificavel, separada de prova e de inferencia.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "proposicao",
      "classe_epistemica",
      "estado"
    ]
  },
  "Evidencia": {
    "description": "Relacao explicita de suporte, refutacao ou contexto entre fonte e afirmacao.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "afirmacao",
      "fonte",
      "relacao",
      "limite"
    ]
  },
  "Dependencia": {
    "description": "Relacao genealogica entre relatos, arquivos, calculos ou documentos.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "origem",
      "destino",
      "tipo_dependencia"
    ]
  },
  "Observacao": {
    "description": "Fato visto em arquivo, codigo ou execucao, com localizador e limite da observacao.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "objeto",
      "observado",
      "metodo",
      "limite"
    ]
  },
  "Medicao": {
    "description": "Valor numerico e unidade, com origem e incerteza documentadas.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "grandeza",
      "valor",
      "unidade",
      "origem",
      "incerteza"
    ]
  },
  "Modelo": {
    "description": "Modelo computacional ou formal e seus pressupostos, distinto de observacao empirica.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "metodo",
      "premissas",
      "insumos",
      "limite"
    ]
  },
  "Hipotese": {
    "description": "Proposicao ainda nao demonstrada com teste capaz de refuta-la.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "enunciado",
      "predicao_testavel",
      "criterio_refutacao"
    ]
  },
  "Ensaio": {
    "description": "Comando reproduzivel e resultados de teste associados a SHA e run, sem forjar PASS.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "comando",
      "head_sha",
      "run_url",
      "resultado",
      "escopo"
    ]
  },
  "Conflito": {
    "description": "Duas proposicoes ou identificacoes incompatíveis mantidas visiveis ate resolucao.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "lado_a",
      "lado_b",
      "natureza",
      "estado"
    ]
  },
  "ResultadoNegativo": {
    "description": "Busca ou teste sem confirmacao, limitado ao corpus e procedimento realmente consultados.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "escopo",
      "procedimento",
      "resultado",
      "limite"
    ]
  },
  "Decisao": {
    "description": "Decisao operacional ou epistemica, responsavel e justificativa; nao e evidencia.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "decisao",
      "fundamento",
      "responsavel"
    ]
  },
  "Capitulo": {
    "description": "Unidade editorial com referencias auditaveis e delta desde o anterior.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "arquivo",
      "anterior",
      "novidade",
      "estado"
    ]
  },
  "Questao": {
    "description": "Lacuna rastreavel, prova faltante e proximo teste falsificavel.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "pergunta",
      "prova_pendente",
      "proximo_teste",
      "estado"
    ]
  },
  "Artefato": {
    "description": "Codigo, matriz, relatorio, dataset ou commit com identidade versionada.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "caminho",
      "versao",
      "tipo_artefato"
    ]
  },
  "Rodada": {
    "description": "Registro totalizante de uma sessao: cada nova informacao deve ter um conceito tipado vinculado.",
    "fields": [
      "id",
      "title",
      "verification",
      "source_url",
      "rodada",
      "data",
      "agente",
      "escopo",
      "proxima_duvida"
    ]
  }
};
const root = path.join("knowledge",".okf","specs");
let changed=0;
for (const [type, policy] of Object.entries(policies)) {
  const slug=type.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
  const file=path.join(root, slug+".md");
  if(!fs.existsSync(file)) throw new Error("okf-parser init nao gerou "+file);
  const previous=fs.readFileSync(file,"utf8");
  if (!previous.includes("TODO: describe this type's frontmatter fields and semantics.")) continue;
  const required=[...new Set(policy.fields)].filter(f=>f!=="rodada"||type!=="Rodada");
  const doc=["---",'type: Spec', 'title: '+type, 'description: '+JSON.stringify(policy.description), '---', '', '# '+type, '', policy.description, '', '## Required fields', '', '| Field | Meaning |', '| --- | --- |', ...required.map(field=>'| `'+field+'` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |'), '', '## Regra epistemologica', '', 'Este tipo registra somente seu proprio significado, nao autoriza inferir observacoes ou autenticidade fisica. `verification` distingue VERIfIED_REPO, REPORTED_REPO, HYPOTHESIS e NOT_RUN. O corpo deve apontar para os outros conceitos com links Markdown quando houver dependencia. Nenhum resultado de PR ou CI vira fato historico sem confronto original.', '', '## Fonte do scaffold', '', 'Scaffold original criado por `okf-parser init --infer-schema --write`; descricao e obrigatoriedade de campos acrescentadas apos a geracao.', ''].join("\n");
  fs.writeFileSync(file,doc);
  changed++;
}
console.log("specs_enriquecidas="+changed+" tipos="+Object.keys(policies).length);
