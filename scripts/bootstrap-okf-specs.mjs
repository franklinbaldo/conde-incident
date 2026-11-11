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
const fieldMeanings = {
  "id": "Identificador unico e estavel deste conceito; nao substituir ID Cxxx da matriz",
  "title": "Titulo legivel",
  "verification": "Grau: VERIFIED_REPO, REPORTED_REPO, HYPOTHESIS ou NOT_RUN",
  "source_url": "URL exata da origem com SHA, pagina ou data quando conhecida",
  "rodada": "ID da Rodada que catalogou a informacao",
  "categoria": "Classe do suporte: original, catalogo, codigo ou dataset",
  "identificador": "Codigo oficial publicado pela fonte",
  "custodia": "Origem e cadeia documental conhecida; nao presumir autenticacao",
  "integridade": "Hash efetivamente calculado ou NOT_COMPUTED",
  "fonte": "Fonte ou artefato de que o trecho deriva",
  "localizador": "Pagina, linha, epoca, segmento ou id verificavel",
  "texto_literal": "Transcricao literal, sem completar lacunas",
  "proposicao": "Afirmacao atomica e falsificavel",
  "classe_epistemica": "Relato, fonte original, catalogo, inferencia ou hipotese",
  "estado": "Situacao atual, inclusive inconclusivo ou aberto",
  "afirmacao": "Referencia a afirmacao suportada ou contestada",
  "relacao": "Apoia, refuta ou contextualiza, sem duplicar testemunhas",
  "limite": "Conclusao que a fonte nao permite",
  "origem": "Registro de entrada do encadeamento",
  "destino": "Registro derivado ou dependente",
  "tipo_dependencia": "Citacao, republicacao, compartilhamento de dados ou base de branch",
  "objeto": "Objeto efetivamente examinado",
  "observado": "Dado observado, distinto de explicacao",
  "metodo": "Procedimento de obtencao, calculo ou auditoria",
  "grandeza": "Variavel medida e definicao",
  "valor": "Valor preservado com precisao original",
  "unidade": "Unidade fisica/estatistica explicita",
  "incerteza": "Intervalo de erro ou desconhecida",
  "premissas": "Suposicoes do modelo e limites",
  "insumos": "Fonte e versao das entradas",
  "enunciado": "Proposicao ainda nao demonstrada",
  "predicao_testavel": "Previsao falsificavel",
  "criterio_refutacao": "Dados que poderiam refutar a hipotese",
  "comando": "Comando reproduzivel e ambiente",
  "head_sha": "SHA exato submetido ao ensaio",
  "run_url": "Execucao GitHub Actions ou log efetivo",
  "resultado": "PASS, FAIL, NOT_RUN ou resultado de terceiro devidamente rotulado",
  "escopo": "Fronteira temporal/documental do estudo",
  "lado_a": "Primeiro lado documentado do conflito",
  "lado_b": "Segundo lado documentado do conflito",
  "natureza": "Tipo de discrepancia: identidade, data, fonte etc.",
  "procedimento": "Consulta ou teste realmente executado",
  "decisao": "Escolha operacional/editorial",
  "fundamento": "Racional auditavel da escolha",
  "responsavel": "Papel autorizado a decidir",
  "arquivo": "Caminho da reportagem no commit",
  "anterior": "Capitulo usado como baseline",
  "novidade": "Delta factual sustentado",
  "pergunta": "Lacuna ainda aberta",
  "prova_pendente": "Evidencia que falta",
  "proximo_teste": "Verificacao capaz de resolver incerteza",
  "caminho": "Caminho ou URL do artefato",
  "versao": "SHA/edicao/hash exato",
  "tipo_artefato": "Codigo, matriz, PR, relatorio, documento ou dataset",
  "data": "Data ISO da sessao",
  "agente": "Agente autor do registro",
  "proxima_duvida": "Questao para a proxima rodada"
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
  const doc=["---",'type: Spec', 'title: '+type, 'description: '+JSON.stringify(policy.description), '---', '', '# '+type, '', policy.description, '', '## Required fields', '', '| Field | Meaning |', '| --- | --- |', ...required.map(field=>'| `'+field+'` | '+(fieldMeanings[field] || 'Campo especifico')+' |'), '', '## Regra epistemologica', '', 'Este tipo registra somente seu proprio significado, nao autoriza inferir observacoes ou autenticidade fisica. `verification` distingue VERIFIED_REPO, REPORTED_REPO, HYPOTHESIS e NOT_RUN. O corpo deve apontar para os outros conceitos com links Markdown quando houver dependencia. Nenhum resultado de PR ou CI vira fato historico sem confronto original.', '', '## Fonte do scaffold', '', 'Scaffold original criado por `okf-parser init --infer-schema --write`; descricao e obrigatoriedade de campos acrescentadas apos a geracao.', ''].join("\n");
  fs.writeFileSync(file,doc);
  changed++;
}
console.log("specs_enriquecidas="+changed+" tipos="+Object.keys(policies).length);
