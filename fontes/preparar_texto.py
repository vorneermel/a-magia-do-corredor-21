from pathlib import Path
import re,json,difflib,subprocess,urllib.request,urllib.error,os
root=Path(__file__).resolve().parents[1]
source=(root/'originais/texto-ampliado-aprovado.md').read_text(encoding='utf-8-sig')
body=source.split('\n\n',1)[1].split('\n\n',1)[1]
segments=body.strip().split('\n\n***\n\n')
assert len(segments)==12,len(segments)
changes=[
('Voltei para o meu carro empurrando o carrinho vazio dela junto ao meu.','Voltei para o meu carro empurrando o carrinho vazio dela junto ao meu, que ainda levava as compras.'),
('Precisei corrigir a direção duas vezes até chegar ao lugar onde devolveria os carrinhos.','Precisei corrigir a direção duas vezes até chegar ao meu carro.'),
('Guardei as compras e me sentei ao volante. Antes de ligar o motor, tirei o celular do bolso.','Guardei as compras, devolvi os carrinhos e me sentei ao volante. Antes de ligar o motor, tirei o celular do bolso.')]
for old,new in changes:
    assert body.count(old)==1,old
    body=body.replace(old,new)
segments=body.strip().split('\n\n***\n\n')
names=['Uma manhã qualquer','A sensação','O corredor 21','Uma próxima conversa','Uma caneca para o amanhã']
bounds=[0,2,3,7,11,12]
chapters=[]
for i,name in enumerate(names):
    text='\n\n***\n\n'.join(segments[bounds[i]:bounds[i+1]])
    chapters.append({'numero':i+1,'titulo':name,'texto':text,'palavras':len(re.findall(r'\b[\wÀ-ÿ]+\b',text))})
    (root/f'capitulos/{i+1:02}.md').write_text(f'# {i+1}. {name}\n\n{text}\n',encoding='utf-8')
full='# A Magia do Corredor 21\n\n**Vorne Ermel**\n\n'+'\n\n'.join(f'## {c["numero"]}. {c["titulo"]}\n\n{c["texto"]}' for c in chapters)+'\n'
(root/'livro-revisado.md').write_text(full,encoding='utf-8')
(root/'editorial/capitulos.json').write_text(json.dumps(chapters,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'editorial/comparacao.diff').write_text(''.join(difflib.unified_diff(source.splitlines(True),full.splitlines(True),fromfile='texto-ampliado-aprovado.md',tofile='livro-revisado.md')),encoding='utf-8')
(root/'editorial/alteracoes.json').write_text(json.dumps([{'tipo':'continuidade objetiva','capitulo':4,'antes':a,'depois':b} for a,b in changes],ensure_ascii=False,indent=2),encoding='utf-8')
blurb='Ele entrou no supermercado com uma lista de compras e a intenção de voltar logo para casa. Mas a passagem de uma desconhecida despertou uma sensação que não soube explicar.\n\nMovido pela curiosidade, chegou ao corredor 21. Entre caixas de chá, carrinhos e pequenos sorrisos, uma conversa abriu espaço para algo que ele já não esperava encontrar naquela manhã.\n\nA Magia do Corredor 21 é um conto sobre atração, encontros na maturidade e a esperança que pode surgir enquanto fazemos as coisas mais comuns da vida.'
(root/'output/capa/contracapa.md').write_text(blurb+'\n',encoding='utf-8')
wordcount=sum(c['palavras'] for c in chapters)
reports={
'editorial/decisoes-autorais.md':'''# Decisões autorais

Autor: Vorne Ermel. Título: A Magia do Corredor 21. Sem subtítulo, série ou dedicatória inventada.
O autor aprovou o texto ampliado da conversa, registrando cerca de meia hora em sua própria leitura. Esse é relato do autor, não duração universal garantida.
Aprovou cinco capítulos, o conceito de capa no supermercado e a contracapa com caneca azul e vaso perto da janela. Autorizou prosseguir com a habilidade editor-livros-kdp em 04/10/2026.
Não houve autorização para publicação comercial, KDP Select ou gastos.
O manuscrito inicial foi ditado pelo autor; o texto ampliado foi desenvolvido com IA e aprovado. Os nomes dos protagonistas permanecem omitidos no texto por escolha narrativa, embora sejam apresentados entre eles. Não inventar nomes, cidade, idades exatas ou passado trágico.
Backup público da obra autorizado pela preferência persistente registrada na habilidade explicitamente invocada. Sincronização depende de autenticação técnica.
''',
'editorial/relatorio-editorial-v1.md':f'''# Relatório editorial — versão 1

Leitura global: toda a versão ampliada aprovada, de início ao fim. Preparação linguística: toda a narrativa. Leitura transversal: cenário, lista, chá, caneca, planta, carrinhos e consentimento no reencontro. Não houve leitura baseada apenas em amostra.

Gênero: conto romântico contemporâneo de atmosfera poética; público adulto. Narrador em primeira pessoa, passado. A magia permanece experiência subjetiva: a mulher não confirma a mesma sensação. O final oferece uma conversa futura, sem casamento ou destino inventado.

Extensão da narrativa após preparação: {wordcount} palavras. O autor relatou meia hora em sua leitura; o ritmo individual pode variar.

## Estrutura

1. Uma manhã qualquer: chegada e compras; termina com a passagem da mulher.
2. A sensação: atração e deslocamento ao corredor 21.
3. O corredor 21: encontro, diálogos, planta, pergunta e apresentação.
4. Uma próxima conversa: caneca, filas, números, estacionamento e partida.
5. Uma caneca para o amanhã: retorno à casa, chá, mensagens e esperança.

As cinco divisões substituem quatro separadores de cena. Os demais separadores permanecem. Não houve corte, ampliação artificial, novo personagem ou novo desfecho nesta preparação.

## Problema resolvido

Importante — continuidade do capítulo 4: o original fazia o narrador chegar ao lugar de devolução dos carrinhos antes de guardar as compras no carro. Três ajustes esclarecem que ele leva seu carrinho ainda carregado até o carro, guarda as compras e só então devolve ambos.

Antes: “até chegar ao lugar onde devolveria os carrinhos”. Depois: “até chegar ao meu carro”.
Antes: “Guardei as compras e me sentei ao volante.” Depois: “Guardei as compras, devolvi os carrinhos e me sentei ao volante.”

## Linguagem e opções preservadas

Mantida a alternância natural entre tratamento formal e você. Travessões em diálogos, reticências em hesitação, itálico nas mensagens. Frases curtas e repetições deliberadas sustentam a voz de observação. Não foram tratadas como erros.
Não se converteu comentário sobre alimentação em orientação médica. As expectativas dos personagens permanecem falas de ficção.

## Rastreabilidade

Original ampliado preservado em originais/texto-ampliado-aprovado.md; ditado inicial em originais/ditado-inicial.md. Alterações objetivas em alteracoes.json, comparação em comparacao.diff. Registro de geração das imagens no briefing-capa.md.

## Prova

O resultado da comparação entre fontes e formatos, paginação, fontes incorporadas e cobertura visual será registrado em validacao-v1.json. Kindle Previewer, Print Previewer e prova física são etapas externas distintas; não declarar aprovação antes da execução.
''',
'editorial/continuidade-e-estilo.md':'''# Continuidade e folha de estilo

Português brasileiro. Primeira pessoa masculina; tempo passado, com diálogos no presente. Narração íntima e cotidiana. Protagonistas sem nome revelado ao leitor; apresentação indireta preservada. Mulher de meia-idade, pele morena clara, olhos verdes, vestido claro. Idade do narrador não fixada; capa interpreta maturidade visual, sem adicioná-la como fato no texto.

Cronologia: uma manhã do último fim de semana de um mês não identificado, seguida de retorno à casa e preparação do chá antes do almoço. Nenhuma data de calendário atribuída.

Trajeto: estacionamento → frutas → corredor oito/café → produto de limpeza → corredor 21 → sal/caneca → caixas vizinhos → saída → carro dela → carro dele → devolução dos carrinhos → casa.

Carrinho dele: roda difícil desde a chegada até a partida; mantém compras até o carro. Carrinho dela fica vazio após guardar suas compras. Planta vai ao carro dela e depois à janela. Caneca azul é comprada por ele e lavada em casa. Chá experimentado pelos dois; irmã da mulher fornece referência indireta de sabor.

Lista acompanha narrador no bolso e nas mãos; verso recebe Corredor 21 em casa. Produto de limpeza segurado antes do corredor e depois colocado no carrinho. Sal é o último item indecifrável. Não se presume solidão definitiva, estado civil, doença ou passado da mulher.

Magia: sensação do narrador; contato inicial incerto. Toque final é real e deliberado. A resposta da mulher não comprova telepatia. Troca de números e convite respeitam vontade recíproca.

Diálogos com travessão; mensagens e anotação em itálico; placa destacada. Capítulos numerados, títulos em caixa de frase. Título comercial A Magia do Corredor 21; autor Vorne Ermel em todos os formatos. Não acrescentar ISBN, ASIN, ficha ou biografia fictícios.
''',
'editorial/progresso.md':'''# Progresso — 04/10/2026

Texto aprovado recuperado integralmente da conversa e preservado. Cinco capítulos preparados. Uma correção de continuidade em três frases, documentada. Título, autoria e contracapa confirmados no histórico.
Produção e conferência de PDF, EPUB e capas em andamento. Commit único final será feito ao concluir a preparação; nenhum commit por capítulo.
Pasta anterior de Ecos da Névoa não existe neste ambiente. Esta obra fica isolada em Documentos/livros/magia do corredor 21; não mistura os livros.
'''
}
for p,t in reports.items():(root/p).write_text(t,encoding='utf-8')
(root/'.gitignore').write_text('tmp/\n__pycache__/\n*.pyc\n',encoding='utf-8')
(root/'.gitattributes').write_text('*.pdf binary\n*.epub binary\n*.zip binary\n*.png binary\n*.jpg binary\n*.diff binary\n',encoding='utf-8')
print(json.dumps({'capitulos':len(chapters),'palavras':wordcount,'ajustes':len(changes)},ensure_ascii=False))
