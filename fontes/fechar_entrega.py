from pathlib import Path
import json,hashlib,zipfile,re
from pypdf import PdfReader
root=Path(__file__).resolve().parents[1]
vpath=root/'editorial/validacao-v1.json';v=json.loads(vpath.read_text(encoding='utf-8'))
v['pdf']['inspecao_visual']='32 páginas inspecionadas integralmente nas 8 folhas de prova da versão final; página 32 branca intencional'
v['pdf']['comparacao_original']='narrativa integral igual ao texto ampliado aprovado, salvo as três correções documentadas'
v['capa_digital']['inspecao_visual']='título, autor, composição e área segura conferidos'
v['capa_impressa']['inspecao_visual']='frente, contracapa, lombada e área livre de código conferidos; template e preview pendentes'
cover=PdfReader(root/'output/capa/proposta-capa-impressa-v1.pdf');fonts={}
for p in cover.pages:
    for f in p['/Resources']['/Font'].values():
        f=f.get_object();d=f['/FontDescriptor'].get_object();fonts[str(f['/BaseFont'])]=any(k in d for k in ['/FontFile','/FontFile2','/FontFile3'])
assert all(fonts.values());v['capa_impressa']['fontes_incorporadas']=fonts
for p,info in v['arquivos'].items():assert hashlib.sha256((root/p).read_bytes()).hexdigest()==info['sha256']
vpath.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'editorial/dossie-publicacao.md';s=p.read_text(encoding='utf-8-sig').replace('450 parágrafos','451 parágrafos');p.write_text(s,encoding='utf-8')
p=root/'README.md';s=p.read_text(encoding='utf-8').replace('PDF e EPUB gerados; prova e conferência em andamento, com evidência atualizada em editorial/validacao-v1.json.','PDF e EPUB validados localmente: narrativa integral conferida e 32 páginas do miolo inspecionadas, com evidência em editorial/validacao-v1.json.');p.write_text(s,encoding='utf-8')
(root/'editorial/cobertura-final.md').write_text('''# Cobertura final — 04/10/2026

Leitura integral do texto ampliado aprovado: todas as 12 cenas originais, organizadas em 5 capítulos sem corte de narrativa. Contagem final: 4.319 palavras. Ajuste objetivo de continuidade: 3 frases no capítulo 4.
Preparação linguística e leitura transversal: toda a obra, nomes indiretos, objetos, trajeto e final. Ditado inicial preservado como documento de origem, com marcas de transcrição.

Conferência integral entre original e capítulos: igualdade de texto após aplicação exclusiva das três correções registradas, desconsiderando separadores substituídos por títulos. PDF: 451 parágrafos presentes na ordem. EPUB: todos os parágrafos iguais à fonte, XML/recursos/links/âncoras conferidos. Miolo: todas as fontes incorporadas; páginas e área segura conferidas.

Prova visual completa: 32 páginas, inspecionadas nas 8 folhas de quatro páginas da renderização final, não apenas amostra. Aberturas, sumário, rodapés, última frase e página branca final conferidos. Capa digital e capa aberta inspecionadas na última renderização. Todas as fontes da capa incorporadas.

A prova detectou e resolveu dois problemas técnicos na primeira conversão: omissão do primeiro parágrafo durante separação do cabeçalho e uma fonte padrão não incorporada. O original não foi alterado por esses problemas. Também foi corrigida a reserva gráfica que tocava a borda da ilustração traseira. As versões finais foram regeneradas e revalidadas.

Não executados: EPUBCheck, Kindle Previewer, Print Previewer, aplicação do template e inspeção de prova física. Assim, PDF/EPUB estão validados localmente; capa aberta é proposta pronta para validação externa. Não houve submissão ou publicação comercial.
''',encoding='utf-8')
p=root/'editorial/relatorio-editorial-v1.md';s=p.read_text(encoding='utf-8');s=s.replace('O resultado da comparação entre fontes e formatos, paginação, fontes incorporadas e cobertura visual será registrado em validacao-v1.json.','Comparação integral de 451 parágrafos narrativos, paginação, fontes incorporadas e prova visual de todas as 32 páginas aprovadas localmente, com evidência em validacao-v1.json e cobertura-final.md.');p.write_text(s,encoding='utf-8')
(root/'editorial/progresso.md').write_text('''# Progresso — 04/10/2026

Preparação editorial da versão 1 concluída. Originais preservados; texto integral em cinco capítulos, 4.319 palavras. Três correções objetivas de continuidade documentadas. Sem novo desfecho ou identidade inventada.
PDF de 32 páginas e EPUB validados localmente. 451 parágrafos conferidos, todos os capítulos comparados ao original. Todas as 32 páginas inspecionadas visualmente. Capa digital concluída; capa aberta entregue como proposta, com imagens acima de 300 ppi efetivos no tamanho aplicado e fontes incorporadas. Template e previews da plataforma pendentes.

Nova instrução explícita do autor em 04/10/2026 permite commits e push das etapas salvas, prevalecendo sobre o procedimento anterior da habilidade. Primeiro backup confirmado: a2fd9bd1afce9c5d50c3c4e089cb881f1ccef3bc, etapa em conferência. A correção da conversão e os entregáveis finais serão enviados em segundo commit; o SHA e a confirmação final estarão na entrega e em tmp/backup-confirmado.json para evitar autorreferência no próprio commit.

Repositório público: https://github.com/vorneermel/a-magia-do-corredor-21 . Esta obra está isolada em Documentos/livros/magia do corredor 21. Não houve publicação comercial.
''',encoding='utf-8')
(root/'editorial/backup.json').write_text(json.dumps({'repo':'vorneermel/a-magia-do-corredor-21','publico':True,'url':'https://github.com/vorneermel/a-magia-do-corredor-21','primeiro_backup_confirmado':'a2fd9bd1afce9c5d50c3c4e089cb881f1ccef3bc','etapa':'preparação final concluída; envio do commit final em seguida'},ensure_ascii=False,indent=2),encoding='utf-8')
# Todos os arquivos de recuperação, exceto o próprio ZIP e temporários reproduzíveis.
files=[p for p in root.rglob('*') if p.is_file() and not any(part in ['.git','tmp','__pycache__'] for part in p.relative_to(root).parts) and p.suffix not in ['.zip','.pyc']]
zip_path=root/'output/entrega/a-magia-do-corredor-21-edicao-v1.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None
for target in re.findall(r'\]\(([^)]+)\)',(root/'README.md').read_text(encoding='utf-8')):
    if not target.startswith('http'):assert (root/target).exists(),target
print(json.dumps({'zip':str(zip_path),'arquivos':len(files),'bytes':zip_path.stat().st_size,'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'fontes_capa':fonts},ensure_ascii=False))
