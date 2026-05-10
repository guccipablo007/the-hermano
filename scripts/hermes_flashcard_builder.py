#!/usr/bin/env python3
import argparse, json, math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image as RLImage, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
VERIFY=Path('/root/.hermes/scripts/hermes_verify.py')
DELIVER=Path('/root/.hermes/scripts/hermes_telegram_deliver.py')
P={'pink':(255,214,230),'rose':(255,120,160),'red':(230,70,100),'purple':(165,120,255),'yellow':(255,220,100),'green':(75,180,120),'blue':(110,180,255),'skin':(245,190,150),'brown':(110,75,45),'dark':(35,45,65),'white':(255,255,255)}
def run(cmd,timeout=180): return subprocess.run(cmd,shell=True,text=True,capture_output=True,timeout=timeout)
def font(size,bold=False):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']:
        if Path(p).exists(): return ImageFont.truetype(p,size=size)
    return ImageFont.load_default()
def heart(d,cx,cy,size,fill):
    r=size//4; d.ellipse((cx-r*2,cy-r,cx,cy+r),fill=fill); d.ellipse((cx,cy-r,cx+r*2,cy+r),fill=fill); d.polygon([(cx-r*2,cy),(cx+r*2,cy),(cx,cy+r*3)],fill=fill)
def mom(path):
    img=Image.new('RGB',(720,520),P['pink']); d=ImageDraw.Draw(img); d.rounded_rectangle((30,30,690,490),45,fill=(255,245,250),outline=P['rose'],width=8); d.ellipse((230,80,490,350),fill=P['brown']); d.ellipse((260,120,460,320),fill=P['skin'],outline=P['dark'],width=4); d.pieslice((240,70,480,260),180,360,fill=P['brown']); d.ellipse((315,205,335,225),fill=P['dark']); d.ellipse((385,205,405,225),fill=P['dark']); d.arc((320,215,400,280),10,170,fill=P['red'],width=5); d.rounded_rectangle((250,330,470,470),40,fill=P['purple'],outline=P['dark'],width=4); heart(d,560,140,70,P['red']); heart(d,150,380,55,P['rose']); img.save(path)
def hug(path):
    img=Image.new('RGB',(720,520),(230,245,255)); d=ImageDraw.Draw(img); d.rounded_rectangle((30,30,690,490),45,fill=(250,253,255),outline=P['blue'],width=8); d.ellipse((200,115,340,255),fill=P['skin'],outline=P['dark'],width=4); d.arc((235,190,305,235),10,170,fill=P['red'],width=4); d.ellipse((240,170,255,185),fill=P['dark']); d.ellipse((285,170,300,185),fill=P['dark']); d.rounded_rectangle((185,260,355,450),45,fill=P['rose'],outline=P['dark'],width=4); d.ellipse((380,165,500,285),fill=(240,170,125),outline=P['dark'],width=4); d.arc((415,230,465,260),10,170,fill=P['red'],width=4); d.ellipse((420,210,432,222),fill=P['dark']); d.ellipse((455,210,467,222),fill=P['dark']); d.rounded_rectangle((365,290,520,455),40,fill=P['green'],outline=P['dark'],width=4); d.line((355,325,450,360),fill=P['skin'],width=20); d.line((365,350,250,360),fill=(240,170,125),width=18); heart(d,360,95,60,P['red']); img.save(path)
def flowers(path):
    img=Image.new('RGB',(720,520),(245,255,240)); d=ImageDraw.Draw(img); d.rounded_rectangle((30,30,690,490),45,fill=(252,255,250),outline=P['green'],width=8)
    for x in [300,350,400,450]: d.line((360,430,x,230),fill=P['green'],width=10)
    d.polygon([(270,360),(460,360),(405,470),(325,470)],fill=(255,205,120),outline=P['dark']);
    def fl(cx,cy,color):
        for a in range(0,360,60):
            dx=int(math.cos(math.radians(a))*32); dy=int(math.sin(math.radians(a))*32); d.ellipse((cx+dx-22,cy+dy-22,cx+dx+22,cy+dy+22),fill=color,outline=P['dark'],width=2)
        d.ellipse((cx-20,cy-20,cx+20,cy+20),fill=P['yellow'],outline=P['dark'],width=2)
    fl(300,220,P['rose']); fl(360,185,P['purple']); fl(420,225,P['red']); fl(470,185,P['blue']); heart(d,155,135,55,P['rose']); img.save(path)
def thanks(path):
    img=Image.new('RGB',(720,520),(255,250,230)); d=ImageDraw.Draw(img); d.rounded_rectangle((30,30,690,490),45,fill=(255,253,245),outline=P['yellow'],width=8); d.ellipse((135,140,275,280),fill=(240,170,125),outline=P['dark'],width=4); d.ellipse((180,200,195,215),fill=P['dark']); d.ellipse((220,200,235,215),fill=P['dark']); d.arc((180,220,235,255),10,170,fill=P['red'],width=4); d.rounded_rectangle((130,285,285,455),35,fill=P['blue'],outline=P['dark'],width=4); d.rounded_rectangle((330,145,610,380),25,fill=P['white'],outline=P['dark'],width=5); d.text((370,210),'THANK\nYOU',font=font(56,True),fill=P['red'],align='center'); heart(d,520,300,50,P['rose']); d.line((285,330,335,300),fill=(240,170,125),width=18); img.save(path)
def generic(path,label):
    img=Image.new('RGB',(720,520),(245,245,255)); d=ImageDraw.Draw(img); d.rounded_rectangle((30,30,690,490),45,fill=P['white'],outline=P['purple'],width=8); heart(d,360,210,110,P['rose']); d.text((90,360),label[:18],font=font(54,True),fill=P['dark']); img.save(path)
def make(path,key,label):
    k=(key or label or '').lower()
    if 'mom' in k or 'mother' in k: mom(path)
    elif 'hug' in k: hug(path)
    elif 'flower' in k or 'bouquet' in k: flowers(path)
    elif 'thank' in k or 'card' in k: thanks(path)
    else: generic(path,label)
def defaults(): return [{'word':'Mom','question':'Can you say, I love you, Mom?','image':'smiling mother'},{'word':'Hug','question':'Can you give mommy a big hug?','image':'hug'},{'word':'Flowers','question':'What color flower do you like?','image':'flowers'},{'word':'Thank You','question':'Can you say thank you, Mom?','image':'thank you card'}]
def build_pdf(output,title,cards,images_dir,age):
    output=Path(output); output.parent.mkdir(parents=True,exist_ok=True); images_dir=Path(images_dir); images_dir.mkdir(parents=True,exist_ok=True); doc=SimpleDocTemplate(str(output),pagesize=A4,rightMargin=.35*inch,leftMargin=.35*inch,topMargin=.35*inch,bottomMargin=.35*inch); styles=getSampleStyleSheet(); title_style=ParagraphStyle('CardTitle',parent=styles['Heading1'],fontSize=24,alignment=1,leading=28,textColor=colors.HexColor('#1f2937')); word_style=ParagraphStyle('Word',parent=styles['Heading2'],fontSize=26,alignment=1,leading=30,textColor=colors.HexColor('#be185d')); q_style=ParagraphStyle('Question',parent=styles['BodyText'],fontSize=15,alignment=1,leading=19,textColor=colors.HexColor('#374151')); story=[Paragraph(title,title_style),Paragraph(f'Ages {age}',q_style),Spacer(1,.18*inch)]; rows=[]; row=[]
    for idx,card in enumerate(cards,1):
        word=card.get('word') or card.get('phrase') or f'Card {idx}'; question=card.get('question') or 'Can you say the word?'; image_key=card.get('image') or word; img_path=images_dir/f"card_{idx}_{image_key.lower().replace(' ','_')}.png"; make(img_path,image_key,word); row.append([RLImage(str(img_path),width=2.65*inch,height=1.9*inch),Paragraph(word,word_style),Paragraph(question,q_style)])
        if len(row)==2: rows.append(row); row=[]
    if row: row.append([Paragraph('',q_style)]); rows.append(row)
    table=Table(rows,colWidths=[3.85*inch,3.85*inch],rowHeights=[3.95*inch]*len(rows)); table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(0,0),(-1,-1),'CENTER'),('BOX',(0,0),(-1,-1),2,colors.HexColor('#f9a8d4')),('INNERGRID',(0,0),(-1,-1),1,colors.HexColor('#fbcfe8')),('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#fff7fb'))])); story.append(table); doc.build(story)
    if not output.read_bytes().startswith(b'%PDF'): raise RuntimeError('PDF_HEADER_MISSING')
def main():
    p=argparse.ArgumentParser(description='Build illustrated flashcard PDFs with local generated pictures.'); p.add_argument('--output',required=True); p.add_argument('--title',required=True); p.add_argument('--theme',default='mothers_day'); p.add_argument('--age',default='3-4'); p.add_argument('--cards-json',default=''); p.add_argument('--deliver-telegram',action='store_true'); p.add_argument('--no-deliver-telegram',action='store_true'); a=p.parse_args(); cards=json.loads(Path(a.cards_json).read_text()) if a.cards_json else defaults(); images_dir=Path('/root/.hermes/file_outputs/flashcard_images')/Path(a.output).stem; build_pdf(a.output,a.title,cards,images_dir,a.age); v=run(f"{VERIFY} file --path {json.dumps(a.output)}",120)
    if v.returncode!=0: print('NOT VERIFIED'); print(v.stdout); print(v.stderr); raise SystemExit(v.returncode)
    delivery='SKIPPED'; should=not a.no_deliver_telegram or a.deliver_telegram
    if should:
        d=run(f"{DELIVER} --file {json.dumps(a.output)} --caption {json.dumps('Your Majesty, here is your illustrated flashcard PDF: '+Path(a.output).name)} --preview-link no",180)
        if d.returncode!=0: print('NOT VERIFIED'); print(d.stdout); print(d.stderr); raise SystemExit(d.returncode)
        delivery='PASSED'
    print('FLASHCARDS_BUILD=PASSED'); print('OUTPUT_PATH='+str(a.output)); print('CARD_COUNT='+str(len(cards))); print('IMAGES_DIR='+str(images_dir)); print('VERIFICATION=PASSED'); print('TELEGRAM_DELIVERY='+delivery)
if __name__=='__main__': main()
