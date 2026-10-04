from pathlib import Path
import re,json,html,zipfile,subprocess,uuid
from xml.etree import ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER,TA_JUSTIFY
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader
from PIL import Image
root=Path(__file__).resolve().parents[1]
chapters=json.loads((root/'editorial/capitulos.json').read_text(encoding='utf-8'))
title='A Magia do Corredor 21';author='Vorne Ermel';W,H=360,576
for name,file in [('Georgia','georgia.ttf'),('Georgia-Bold','georgiab.ttf'),('Georgia-Italic','georgiai.ttf'),('Georgia-BoldItalic','georgiaz.ttf')]:pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Georgia',normal='Georgia',bold='Georgia-Bold',italic='Georgia-Italic',boldItalic='Georgia-BoldItalic')
OriginalCanvas=canvas.Canvas
class EmbeddedCanvas(OriginalCanvas):
    def __init__(self,*args,**kwargs):
        kwargs['initialFontName']='Georgia'
        super().__init__(*args,**kwargs)
canvas.Canvas=EmbeddedCanvas
body=ParagraphStyle('Body',fontName='Georgia',fontSize=11.5,leading=15.5,alignment=TA_JUSTIFY,firstLineIndent=13,spaceAfter=1,splitLongWords=False,allowWidows=0,allowOrphans=0)
first=ParagraphStyle('First',parent=body,firstLineIndent=0)
center=ParagraphStyle('Center',fontName='Georgia',fontSize=11,leading=16,alignment=TA_CENTER)
head=ParagraphStyle('Heading',parent=center,fontName='Georgia-Bold',fontSize=18,leading=23,spaceAfter=22,keepWithNext=True)
small=ParagraphStyle('Small',parent=center,fontSize=9,leading=13)
chapter_starts={}
def markup(text):
    text=html.escape(text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'\*(.+?)\*',r'<i>\1</i>',text)
    return text
class Book(BaseDocTemplate):
    def afterFlowable(self,f):
        if hasattr(f,'chapter_num'):chapter_starts[f.chapter_num]=self.page

def page(c,d):
    if d.page>=4:
        c.setFillColor(HexColor('#555555'));c.setFont('Georgia',7.5)
        c.drawCentredString(W/2,H-27,title)
        c.setFont('Georgia',9);c.drawCentredString(W/2,24,str(d.page))
def build(path,toc):
    chapter_starts.clear()
    doc=Book(str(path),pagesize=(W,H),title=title,author=author)
    odd=Frame(49,45,W-49-38,H-45-49,id='odd',leftPadding=0,rightPadding=0,bottomPadding=0,topPadding=0)
    even=Frame(38,45,W-49-38,H-45-49,id='even',leftPadding=0,rightPadding=0,bottomPadding=0,topPadding=0)
    doc.addPageTemplates([PageTemplate(id='odd',frames=[odd],onPage=page,autoNextPageTemplate='even'),PageTemplate(id='even',frames=[even],onPage=page,autoNextPageTemplate='odd')])
    s=[Spacer(1,96),Paragraph('A Magia do<br/>Corredor 21',ParagraphStyle('Title',parent=head,fontSize=29,leading=36,spaceAfter=32)),Paragraph(author,center),Spacer(1,90),Paragraph('Um conto sobre encontros e esperança',small),PageBreak(),Spacer(1,100),Paragraph('© 2026 Vorne Ermel',center),Spacer(1,16),Paragraph('A Magia do Corredor 21',center),Paragraph('Primeira edição · Português brasileiro',small),Spacer(1,20),Paragraph('Esta é uma obra de ficção.',small),PageBreak(),Spacer(1,28),Paragraph('Sumário',head)]
    for c in chapters:s.append(Paragraph(f'{c["numero"]}. {html.escape(c["titulo"])}<br/><font size="9">{toc.get(c["numero"],"—")}</font>',ParagraphStyle('Toc',parent=center,spaceAfter=15,leading=15)))
    s.append(PageBreak())
    for i,c in enumerate(chapters):
        if i:s.append(PageBreak())
        s.extend([Spacer(1,25),Paragraph(str(c['numero']),small),Spacer(1,8)])
        p=Paragraph(c['titulo'],head);p.chapter_num=c['numero'];s.append(p)
        fresh=True
        for para in c['texto'].split('\n\n'):
            if para=='***':s.append(Paragraph('•   •   •',ParagraphStyle('Scene',parent=center,fontSize=8,spaceBefore=10,spaceAfter=10,keepWithNext=True)));fresh=True
            else:s.append(Paragraph(markup(para),first if fresh else body));fresh=False
    doc.build(s,canvasmaker=EmbeddedCanvas)
    return dict(chapter_starts)
miolo=root/'output/pdf/a-magia-do-corredor-21-miolo-v1.pdf'
starts=build(root/'tmp/miolo-primeira-prova.pdf',{})
final_starts=build(miolo,starts)
assert final_starts==starts
reader=PdfReader(miolo)
if len(reader.pages)%2:
    from pypdf import PdfWriter
    writer=PdfWriter();writer.append(reader,import_outline=False);writer.add_blank_page(width=W,height=H)
    writer.add_metadata({'/Title':title,'/Author':author})
    with miolo.open('wb') as f:writer.write(f)
pagecount=len(PdfReader(miolo).pages)
assert pagecount>=24,pagecount
(root/'editorial/paginacao.json').write_text(json.dumps({'paginas':pagecount,'formato_polegadas':[5,8],'capitulos':starts,'pagina_final_branca':len(reader.pages)%2==1},ensure_ascii=False,indent=2),encoding='utf-8')
cream='#F5ECDD';green='#354D40';gold='#9D7D45'
front_art=root/'output/capa/arte-frente-v1.png';back_art=root/'output/capa/arte-verso-v1.png'
art_w=3.28*72;fw,fh=Image.open(front_art).size;art_h=art_w*fh/fw
# A arte ocupa apenas 3,28 polegadas de largura: resolução real >300 ppi, sem fingir detalhe por ampliação.
def front(c,x=0,y=0):
    c.saveState();c.translate(x,y);c.setFillColor(HexColor(cream));c.rect(0,0,W,H,fill=1,stroke=0)
    c.drawImage(str(front_art),(W-art_w)/2,35,width=art_w,height=art_h)
    c.setFillColor(HexColor(green));c.setFont('Georgia',25);c.drawCentredString(W/2,520,'A MAGIA')
    c.setFont('Georgia',20);c.drawCentredString(W/2,489,'DO CORREDOR')
    c.setFont('Georgia-Bold',37);c.drawCentredString(W/2,445,'21')
    c.setFont('Georgia',12);c.drawCentredString(W/2,28,'VORNE ERMEL');c.restoreState()
frontpdf=root/'tmp/capa-frontal.pdf';c=canvas.Canvas(str(frontpdf),pagesize=(W,H));front(c);c.showPage();c.save()
subprocess.run(['pdftoppm','-singlefile','-scale-to-x','1600','-scale-to-y','2560','-png',str(frontpdf),str(root/'tmp/capa-digital')],check=True,capture_output=True)
Image.open(root/'tmp/capa-digital.png').convert('RGB').save(root/'output/capa/capa-digital-v1.jpg',quality=95,subsampling=0)
# SVG mantém tipografia editável; a imagem original é referenciada por caminho relativo.
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 360 576" width="1600" height="2560"><rect width="360" height="576" fill="{cream}"/><image x="{(W-art_w)/2}" y="{H-35-art_h}" width="{art_w}" height="{art_h}" xlink:href="arte-frente-v1.png"/><g fill="{green}" text-anchor="middle" font-family="Georgia,serif"><text x="180" y="56" font-size="25">A MAGIA</text><text x="180" y="87" font-size="20">DO CORREDOR</text><text x="180" y="131" font-size="37" font-weight="bold">21</text><text x="180" y="548" font-size="12">VORNE ERMEL</text></g></svg>'''
(root/'output/capa/capa-frontal-editavel-v1.svg').write_text(svg,encoding='utf-8')
bleed=9;spine=pagecount*.0025*72;CW=2*W+spine+2*bleed;CH=H+2*bleed
cover=root/'output/capa/proposta-capa-impressa-v1.pdf'
c=canvas.Canvas(str(cover),pagesize=(CW,CH));c.setTitle(title+' — proposta de capa');c.setAuthor(author)
c.setFillColor(HexColor(cream));c.rect(0,0,CW,CH,fill=1,stroke=0)
front(c,bleed+W+spine,bleed)
c.setFillColor(HexColor(green));c.rect(bleed+W,0,spine,CH,fill=1,stroke=0)
back_w=3.0*72;bw,bh=Image.open(back_art).size;back_h=back_w*bh/bw
c.drawImage(str(back_art),bleed+(W-back_w)/2,bleed+118,width=back_w,height=back_h)
# Colocar sinopse em painel claro acima da ilustração, sem atingir área reservada ao código.
c.setFillColor(HexColor(cream));c.rect(bleed+28,bleed+300,W-56,240,fill=1,stroke=0)
backstyle=ParagraphStyle('Back',fontName='Georgia',fontSize=10.5,leading=14.5,textColor=HexColor(green),spaceAfter=10)
y=bleed+525
for paragraph in (root/'output/capa/contracapa.md').read_text(encoding='utf-8').strip().split('\n\n'):
    p=Paragraph(html.escape(paragraph),backstyle);_,h=p.wrap(W-70,240);p.drawOn(c,bleed+35,y-h);y-=h+12
# Área sem elementos relevantes 2 x 1,2 polegadas, no canto inferior direito da contracapa; sem ISBN fictício.
c.setFillColor(HexColor(cream));c.rect(bleed+W-144-18,bleed+18,144,86.4,fill=1,stroke=0)
c.showPage();c.save()
(root/'editorial/geometria-capa.json').write_text(json.dumps({'paginas':pagecount,'papel_proposto':'creme','lombada_mm':pagecount*.0635,'sangria_mm':3.175,'capa_pontos':[CW,CH],'arte_frente_pixels':[fw,fh],'ppi_frente':fw/3.28,'arte_verso_pixels':[bw,bh],'ppi_verso':bw/3,'template_calculadora':'não aplicado','estado':'proposta; validar com template e Print Previewer'},ensure_ascii=False,indent=2),encoding='utf-8')
# EPUB 3 fluido: texto sem cabeçalhos ou paginação impressa.
uid='urn:uuid:'+str(uuid.uuid5(uuid.NAMESPACE_URL,'https://github.com/vorneermel/a-magia-do-corredor-21/edicao-v1'))
def xhtml(t,content):return '<?xml version="1.0" encoding="utf-8"?>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="pt-BR" xml:lang="pt-BR"><head><title>'+html.escape(t)+'</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>'+content+'</body></html>'
items={'style.css':'body{font-family:serif;line-height:1.45;margin:5%;}h1,h2,.center{text-align:center;}h1{font-size:1.6em;}p{margin:0;text-indent:1.2em;}p.first{margin-top:1em;text-indent:0;}.scene{text-align:center;text-indent:0;margin:1.2em 0;}img{max-width:100%;height:auto;}.titlepage p{text-align:center;text-indent:0;}.cover{text-align:center;margin:0;}'}
items['title.xhtml']=xhtml(title,'<section class="titlepage"><h1>'+title+'</h1><p>'+author+'</p><p>Primeira edição · 2026</p></section>')
items['cover.xhtml']=xhtml('Capa','<section class="cover" epub:type="cover"><img src="cover.jpg" alt="Capa de A Magia do Corredor 21, de Vorne Ermel: um encontro no supermercado."/></section>')
manifest=['<item id="style" href="style.css" media-type="text/css"/>','<item id="cover-image" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>','<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>','<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>','<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>']
spines=['<itemref idref="cover"/>','<itemref idref="title"/>','<itemref idref="nav"/>'];nav=[]
for ch in chapters:
    number=ch['numero'];content=f'<section epub:type="chapter" id="chapter{number}"><h1>{number}. {html.escape(ch["titulo"])}</h1>'
    fresh=True
    for para in ch['texto'].split('\n\n'):
        if para=='***':content+='<p class="scene" aria-label="Mudança de cena">• • •</p>';fresh=True
        else:content+='<p'+(' class="first"' if fresh else '')+'>'+markup(para).replace('<i>','<em>').replace('</i>','</em>').replace('<b>','<strong>').replace('</b>','</strong>')+'</p>';fresh=False
    items[f'chapter{number}.xhtml']=xhtml(ch['titulo'],content+'</section>')
    manifest.append(f'<item id="ch{number}" href="chapter{number}.xhtml" media-type="application/xhtml+xml"/>');spines.append(f'<itemref idref="ch{number}"/>')
    nav.append(f'<li><a href="chapter{number}.xhtml#chapter{number}">{number}. {html.escape(ch["titulo"])}</a></li>')
items['nav.xhtml']=xhtml('Sumário','<nav epub:type="toc" id="toc"><h1>Sumário</h1><ol>'+''.join(nav)+'</ol></nav>')
opf='<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bookid">'+uid+'</dc:identifier><dc:title>'+title+'</dc:title><dc:creator>'+author+'</dc:creator><dc:language>pt-BR</dc:language><meta property="dcterms:modified">2026-10-04T12:00:00Z</meta><meta name="cover" content="cover-image"/></metadata><manifest>'+''.join(manifest)+'</manifest><spine>'+''.join(spines)+'</spine></package>'
epub=root/'output/epub/a-magia-do-corredor-21-v1.epub'
with zipfile.ZipFile(epub,'w') as z:
    z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
    z.writestr('META-INF/container.xml','<?xml version="1.0" encoding="utf-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>',compress_type=zipfile.ZIP_DEFLATED)
    z.writestr('OEBPS/content.opf',opf,compress_type=zipfile.ZIP_DEFLATED)
    for name,content in items.items():z.writestr('OEBPS/'+name,content,compress_type=zipfile.ZIP_DEFLATED)
    z.write(root/'output/capa/capa-digital-v1.jpg','OEBPS/cover.jpg',compress_type=zipfile.ZIP_DEFLATED)
print(json.dumps({'paginas':pagecount,'aberturas':starts,'ppi_capa_frente':fw/3.28,'pdf':str(miolo),'epub':str(epub)},ensure_ascii=False))
