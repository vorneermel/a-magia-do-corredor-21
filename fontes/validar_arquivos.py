from pathlib import Path
import json,re,hashlib,zipfile,subprocess,posixpath
from xml.etree import ElementTree as ET
from pypdf import PdfReader
import pdfplumber
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1];chapters=json.loads((root/'editorial/capitulos.json').read_text(encoding='utf-8'))
miolo=root/'output/pdf/a-magia-do-corredor-21-miolo-v1.pdf';epub=root/'output/epub/a-magia-do-corredor-21-v1.epub'
normal=lambda x:re.sub(r'\s+','',x.replace('*',''))
reader=PdfReader(miolo);fonts={};extracted=[];bounds=[]
with pdfplumber.open(miolo) as pdf:
    for i,p in enumerate(pdf.pages):
        assert (p.width,p.height)==(360,576)
        if i>=3:
            crop=p.crop((0,42,360,531));extracted.append(crop.extract_text() or '')
            for char in crop.chars:
                if char['text'].strip():assert char['x0']>=37 and char['x1']<=323,(i+1,char['text'],char['x0'],char['x1'])
            bounds.append({'pagina':i+1,'caracteres':len(crop.chars)})
for page in reader.pages:
    for key,ref in page['/Resources'].get('/Font',{}).items():
        f=ref.get_object();fd=f.get('/FontDescriptor');embedded=False
        if fd:embedded=any(k in fd.get_object() for k in ['/FontFile','/FontFile2','/FontFile3'])
        fonts[str(f.get('/BaseFont'))]=embedded
joined=normal(''.join(extracted));cursor=0;paragraphs=0
for c in chapters:
    for p in c['texto'].split('\n\n'):
        if p=='***':continue
        value=normal(p);found=joined.find(value,cursor)
        assert found>=0,('Parágrafo não encontrado na ordem do PDF',c['numero'],p[:90])
        cursor=found+len(value);paragraphs+=1
assert all(fonts.values()),fonts
ns={'x':'http://www.w3.org/1999/xhtml','o':'http://www.idpf.org/2007/opf'}
with zipfile.ZipFile(epub) as z:
    assert z.testzip() is None
    assert z.infolist()[0].filename=='mimetype' and z.infolist()[0].compress_type==0
    assert z.read('mimetype')==b'application/epub+zip'
    for name in z.namelist():
        if name.endswith(('.xml','.xhtml','.opf')):ET.fromstring(z.read(name))
    opf=ET.fromstring(z.read('OEBPS/content.opf'));ids=set()
    for item in opf.findall('o:manifest/o:item',ns):
        assert 'OEBPS/'+item.attrib['href'] in z.namelist();assert item.attrib['id'] not in ids;ids.add(item.attrib['id'])
    for item in opf.findall('o:spine/o:itemref',ns):assert item.attrib['idref'] in ids
    for c in chapters:
        xml=ET.fromstring(z.read(f'OEBPS/chapter{c["numero"]}.xhtml'))
        actual=[''.join(p.itertext()) for p in xml.findall('.//x:p',ns) if p.attrib.get('class')!='scene']
        expected=[p.replace('**','').replace('*','') for p in c['texto'].split('\n\n') if p!='***']
        assert actual==expected,('Diferença de texto EPUB',c['numero'])
    for name in z.namelist():
        if name.endswith('.xhtml'):
            xml=ET.fromstring(z.read(name))
            for element in xml.iter():
                for attr in ['href','src']:
                    target=element.attrib.get(attr)
                    if not target:continue
                    path,_,anchor=target.partition('#');resolved=posixpath.normpath(posixpath.join(posixpath.dirname(name),path)) if path else name
                    assert resolved in z.namelist(),(name,target)
                    if anchor:
                        dst=ET.fromstring(z.read(resolved));assert any(e.attrib.get('id')==anchor for e in dst.iter())
cover=Image.open(root/'output/capa/capa-digital-v1.jpg');assert cover.size==(1600,2560) and cover.mode=='RGB'
proof=root/'tmp/prova';proof.mkdir(exist_ok=True)
subprocess.run(['pdftoppm','-r','100','-png',str(miolo),str(proof/'pagina')],capture_output=True,check=True)
pages=sorted(proof.glob('pagina-*.png'));assert len(pages)==len(reader.pages)
for start in range(0,len(pages),4):
    sheet=Image.new('RGB',(1200,1660),'#cccccc');d=ImageDraw.Draw(sheet)
    for j,path in enumerate(pages[start:start+4]):
        im=Image.open(path).convert('RGB');im.thumbnail((560,790));x=(j%2)*600+(600-im.width)//2;y=(j//2)*830+24
        sheet.paste(im,(x,y));d.text((x,y-17),f'Página {start+j+1}',fill='black')
    sheet.save(proof/f'folha-{start//4+1:02}.jpg',quality=92)
subprocess.run(['pdftoppm','-singlefile','-r','125','-png',str(root/'output/capa/proposta-capa-impressa-v1.pdf'),str(proof/'capa-aberta')],capture_output=True,check=True)
files=['livro-revisado.md','output/pdf/a-magia-do-corredor-21-miolo-v1.pdf','output/epub/a-magia-do-corredor-21-v1.epub','output/capa/capa-digital-v1.jpg','output/capa/proposta-capa-impressa-v1.pdf']
result={'data':'2026-10-04','pdf':{'paginas':len(reader.pages),'dimensoes_pontos':[360,576],'fontes':fonts,'paragrafos_na_ordem':paragraphs,'inspecao_visual':'pendente; 32 páginas renderizadas'},'epub':{'xml':'todos os documentos bem formados','recursos_links_ancoras':'verificados','paragrafos':'idênticos à fonte revisada','EPUBCheck':'não executado; ferramenta não encontrada','Kindle_Previewer':'não executado; ferramenta não encontrada'},'capa_digital':{'pixels':list(cover.size),'modo':cover.mode},'capa_impressa':json.loads((root/'editorial/geometria-capa.json').read_text(encoding='utf-8')),'arquivos':{p:{'bytes':(root/p).stat().st_size,'sha256':hashlib.sha256((root/p).read_bytes()).hexdigest()} for p in files}}
(root/'editorial/validacao-v1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'paginas':len(reader.pages),'paragrafos':paragraphs,'fontes':fonts,'folhas_para_inspecao':len(list(proof.glob('folha-*.jpg')))},ensure_ascii=False))
