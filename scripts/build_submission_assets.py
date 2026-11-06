"""Optional generation of submission PDF + editable PowerPoint from REPORT.md.

Install: pip install -r requirements-assets.txt
Run from project root: python scripts/build_submission_assets.py
"""
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def make_pdf():
    import mistune
    from weasyprint import HTML, CSS
    source = (DOCS / "REPORT.md").read_text(encoding="utf8")
    html_body = mistune.create_markdown(plugins=["table", "strikethrough"])(source)
    css = r"""
    @page { size: A4; margin: 19mm 19mm 20mm 19mm;
        @bottom-center { content: 'CS3235 | BhashaWrite   •   Page ' counter(page); color:#60778d; font-size:8.3pt; }
    }
    @font-face {font-family: Noto;src:local('Noto Sans');}
    body { font-family: Noto, 'DejaVu Sans', sans-serif; color:#182d3f; font-size:9.35pt; line-height:1.50; }
    h1 { color:#102f49; font-size:21pt; line-height:1.22; margin:0 0 16px; font-weight:800; padding-bottom:16px;
         border-bottom:5px solid #13a08f; }
    h2 { font-size:13.1pt; color:#0d5366; padding-top:12px; margin:20px 0 7px; page-break-after:avoid; }
    h3 { font-size:10.3pt; color:#176575; margin:11px 0 5px; page-break-after:avoid; }
    h1 + p {color:#435a6b;}
    p { margin:6px 0 9px; orphans:3; widows:3; }
    a { color:#126c91; text-decoration:none;overflow-wrap:anywhere; }
    strong { color:#13374c; }
    blockquote { background:#eaf5f4; border-left:4px solid #20a78c; padding:10px 14px; margin:14px 0;
                 color:#315d63; }
    pre { white-space:pre-wrap; overflow-wrap:anywhere; border-radius:7px; padding:11px;
          background:#eff3f7; color:#16364b; font-size:7.4pt; line-height:1.35; }
    code {font-family:'DejaVu Sans Mono', monospace; font-size:0.9em; background:#f4f6f8;
          padding:1px 2px; overflow-wrap:anywhere;}
    pre code {background:none;}
    table {border-collapse:collapse; width:100%; margin:12px 0 16px; table-layout:fixed; font-size:8.4pt;}
    th {background:#17364c;color:white;font-weight:700;}
    th, td {border:1px solid #d6e1e8; padding:7px 7px; text-align:left; vertical-align:top;overflow-wrap:anywhere; }
    tr:nth-child(even) td {background:#f4f8fa;}
    ul,ol {margin:7px 0 10px;padding-left:21px;}
    li {padding-bottom:3px;}
    h2, h3,table,pre,blockquote {break-inside:avoid-page;}
    """
    doc = f"<!doctype html><html><head><meta charset='utf-8'></head><body>{html_body}</body></html>"
    HTML(string=doc, base_url=str(ROOT)).write_pdf(str(DOCS/"BhashaWrite_Project_Report.pdf"),
                                                     stylesheets=[CSS(string=css)])


def make_slides():
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    BLUE=RGBColor(17,49,72); DARK=RGBColor(20,48,66); TEAL=RGBColor(20,154,137)
    CLOUD=RGBColor(234,246,244); WHITE=RGBColor(255,255,255); SLATE=RGBColor(77,99,118)
    LIGHT=RGBColor(245,249,250); GOLD=RGBColor(245,183,71); RED=RGBColor(209,80,80)

    def shape(slide,x,y,w,h,fill,rounding=True):
        sh=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounding else MSO_SHAPE.RECTANGLE,
                                  Inches(x),Inches(y),Inches(w),Inches(h))
        sh.fill.solid();sh.fill.fore_color.rgb=fill
        sh.line.fill.background()
        return sh

    def textbox(slide,x,y,w,h,text,size=19,color=DARK,bold=False,align=None):
        s=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
        tf=s.text_frame;tf.word_wrap=True;tf.margin_left=Inches(.06);tf.margin_right=Inches(.06)
        tf.margin_top=Inches(.01);tf.margin_bottom=Inches(.01)
        for ix,line in enumerate(text.split('\n')):
            p=tf.paragraphs[0] if ix==0 else tf.add_paragraph()
            p.text=line;p.font.name='Aptos';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color
            p.space_after=Pt(6)
            if align: p.alignment=align
        return s

    def base(title,kicker='CS3235 MINI PROJECT 04'):
        slide=prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid();slide.background.fill.fore_color.rgb=LIGHT
        shape(slide,0,0,13.333,.1,TEAL,False)
        textbox(slide,.65,.34,10.8,.34,kicker,11,TEAL,True)
        textbox(slide,.65,.84,11.9,.7,title,29,BLUE,True)
        shape(slide,.66,1.60,.85,.055,GOLD,False)
        textbox(slide,.7,7.08,9.8,.24,'BHASHAWRITE   /   HINDI  ·  KANNADA  ·  TAMIL',9,SLATE)
        textbox(slide,12.45,7.06,.45,.25,str(len(prs.slides)),10,SLATE)
        return slide
    def card(slide,x,y,w,h,head,detail,headcolor=BLUE):
        shape(slide,x,y,w,h,WHITE)
        shape(slide,x,y,.075,h,TEAL,False)
        textbox(slide,x+.22,y+.20,w-.44,.55,head,19,headcolor,True)
        textbox(slide,x+.22,y+.83,w-.44,h-1.0,detail,15,SLATE)

    # Cover
    s=prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid();s.background.fill.fore_color.rgb=BLUE
    shape(s,.72,.85,1.18,.13,GOLD,False)
    textbox(s,.75,1.23,11.8,1.0,'BHASHAWRITE',48,WHITE,True)
    textbox(s,.77,2.34,11.7,.7,'Hinglish Smart Writing Assistant',28,RGBColor(179,232,225),False)
    textbox(s,.80,3.32,11,.5,'Roman script  →  Native script  →  Clearer writing  →  Optional English',19,WHITE)
    shape(s,.75,4.5,11.8,.025,TEAL,False)
    textbox(s,.8,5.10,11.6,.6,'CS3235   •   Mini Project 4   •   CIE3 Lab',19,WHITE,True)
    textbox(s,.82,5.79,10.8,.7,'Individual submission  |  Student: [Your name]  |  USN: [Your USN]',15,RGBColor(210,223,228))

    s=base('The problem: Roman-script Indian languages')
    card(s,.7,1.93,3.8,3.65,'People type informally','“mujhe paani chahiye”\n“nanna hesaru”\n“enakku thanni venum”')
    card(s,4.75,1.93,3.8,3.65,'Naive tools fail','Variable Roman spellings\nEnglish technical words\nAmbiguous proper names\nMixed punctuation')
    card(s,8.80,1.93,3.8,3.65,'Our solution','Language-aware conversion\nClear model provenance\nMeasurable evaluation\nUsable Streamlit frontend')
    textbox(s,1,6.0,11,.48,'Design principle: separate transliteration from translation and rewriting.',17,TEAL,True)

    s=base('What the application does')
    funcs=[('1','Input','Roman Hindi, Kannada or Tamil'),('2','Convert','IndicXlit or explicit offline demo'),
           ('3','Polish','Whitespaces and punctuation'),('4','Extend','Optional BharatGen / IndicTrans2'),('5','Evaluate','CER, word accuracy, exact match')]
    for i,(num,head,detail) in enumerate(funcs):
        y=1.87+i*.88
        shape(s,.80,y,.59,.57,TEAL)
        textbox(s,.95,y+.06,.32,.36,num,16,WHITE,True,PP_ALIGN.CENTER)
        textbox(s,1.67,y-.02,2.85,.56,head,21,BLUE,True)
        textbox(s,4.37,y,8.0,.47,detail,17,SLATE)

    s=base('Modular, inspectable architecture')
    nodes=[('INPUT','Streamlit editor'),('PROTECT','URL • email • numbers'),('CONVERT','IndicXlit / demo'),
           ('POLISH','Local correction'),('OPTIONAL','Param1 + IndicTrans2'),('OUTPUT','Results + export')]
    for i,(label,detail) in enumerate(nodes):
        x=.77+(i%3)*4.16;y=2.02+(i//3)*2.18
        fill=TEAL if i in (0,5) else BLUE
        shape(s,x,y,3.67,1.53,fill)
        textbox(s,x+.20,y+.14,3.3,.41,label,17,WHITE,True)
        textbox(s,x+.20,y+.69,3.28,.62,detail,14,WHITE)
    textbox(s,5.95,3.66,1.5,.45,'↓',24,TEAL,True,PP_ALIGN.CENTER)
    textbox(s,4.03,2.47,.6,.5,'→',24,TEAL,True,PP_ALIGN.CENTER)
    textbox(s,8.23,2.47,.6,.5,'→',24,TEAL,True,PP_ALIGN.CENTER)
    textbox(s,4.03,4.65,.6,.5,'→',24,TEAL,True,PP_ALIGN.CENTER)
    textbox(s,8.23,4.65,.6,.5,'→',24,TEAL,True,PP_ALIGN.CENTER)

    s=base('Model roles, hardware and honesty')
    card(s,.75,1.98,3.8,3.63,'AI4Bharat IndicXlit','Real neural Roman → native transliteration. Optional install and weights. Word-level inference.')
    card(s,4.77,1.98,3.8,3.63,'BharatGen Param1','Param-1-2.9B-Instruct optional Hindi-only rewriting via a separate vLLM endpoint.')
    card(s,8.79,1.98,3.8,3.63,'AI4Bharat IndicTrans2','Optional native → English using distilled 200M model and IndicTransToolkit.')
    textbox(s,.95,6.03,11.4,.49,'Pretrained model inference was NOT benchmarked here; demo baseline ≠ neural accuracy.',17,RED,True)

    s=base('Streamlit app: three simple tabs')
    card(s,.78,2.05,3.75,3.63,'Writer','Select language and backend\nEnter Roman text\nConvert and download\nSee unknown-word warnings')
    card(s,4.80,2.05,3.75,3.63,'Evaluation','45 reference examples\nRun a backend on all rows\nCER and word accuracy\nDownload detailed CSV')
    card(s,8.82,2.05,3.75,3.63,'Project info','Architecture and models\nWhich features are optional\nLimitations and privacy\nReproducibility notes')

    s=base('Test corpus and methodology')
    for i,(lang,text) in enumerate([('Hindi','15 cases'),('Kannada','15 cases'),('Tamil','15 cases')]):
        x=.90+i*4.15
        shape(s,x,1.97,3.72,1.38,WHITE)
        textbox(s,x+.16,2.17,3.34,.41,lang,20,BLUE,True)
        textbox(s,x+.17,2.72,3.1,.34,text,16,TEAL,True)
    textbox(s,1.06,3.73,11.55,1.25,'Categories: greeting • self-introduction • education • question • request • numeric time • code mixing • unseen words',19,SLATE)
    shape(s,.90,5.37,11.55,.65,CLOUD)
    textbox(s,1.10,5.54,11.0,.36,'Tiny, manually authored evaluation set — not the official Aksharantar benchmark.',16,BLUE,True)

    s=base('Measured results: OFFLINE demo only')
    rows=[('Hindi',.0571,.9556,.8667),('Kannada',.0351,.9778,.9333),('Tamil',.0293,.9778,.9333)]
    textbox(s,.78,1.92,2.5,.42,'Mean CER ↓',20,BLUE,True)
    for j,(name,cer,word,exact) in enumerate(rows):
        y=2.54+j*1.16
        textbox(s,.82,y,2.05,.40,name,17,BLUE,True)
        shape(s,3.09,y,cer*70,.43,TEAL)
        textbox(s,7.36,y,1.05,.42,f'{cer:.4f}',17,BLUE,True)
        textbox(s,8.7,y,3.35,.43,f'Words {word:.1%} · Exact {exact:.1%}',15,SLATE)
    shape(s,.79,6.06,11.73,.58,CLOUD)
    textbox(s,.96,6.18,11.3,.41,'Overall: CER 0.0405   |   Word accuracy 97.04%   |   Exact match 91.11%',17,BLUE,True)

    s=base('Error analysis: four observed failures')
    items=[('H13','“certificate” retained in Roman script'),('H14','“Email” preserved as a technical term'),
           ('K13','“assignment” missing from Kannada lexicon'),('T13','“assignment” missing from Tamil lexicon')]
    for i,(case,desc) in enumerate(items):
        y=1.93+i*1.03
        shape(s,.83,y,1.16,.70,RED)
        textbox(s,.99,y+.14,.9,.38,case,17,WHITE,True)
        shape(s,2.24,y,10.13,.70,WHITE)
        textbox(s,2.50,y+.12,9.68,.47,desc,18,SLATE)
    textbox(s,.96,6.37,10.5,.42,'Cause: tiny lexicon and code-mix tradeoffs — not a result of neural inference.',15,TEAL,True)

    s=base('Safety, limitations and future work')
    card(s,.77,1.97,3.77,3.61,'Known limitations','Roman spelling ambiguity\nSmall authored dataset\nNo official corpus benchmark\nUnverified neural setup')
    card(s,4.81,1.97,3.77,3.61,'Safety controls','Input length limit\nModel provenance shown\nUntrusted prompt boundaries\nNo silent fake translation')
    card(s,8.85,1.97,3.77,3.61,'Next steps','Real IndicXlit benchmark\nNative-speaker review\nTop-k choice editor\nRate limits and deployment')

    s=base('Reproduce the demonstration')
    shape(s,.85,1.96,11.75,3.26,BLUE)
    commands=['python -m venv .venv','pip install -r requirements.txt','streamlit run app.py',
              'python -m pytest -q','python evaluation/run_eval.py --mode demo']
    textbox(s,1.22,2.28,11.02,2.68,'\n'.join(commands),20,WHITE)
    textbox(s,.98,5.55,11.19,.57,'20 local tests passed  •  45 offline-demo cases  •  source and docs included',19,TEAL,True)

    s=base('What is included and what remains')
    card(s,.85,1.98,5.63,3.88,'Delivered & verified','Streamlit source + CLI\n45-case CSV & metrics\n20 passing pytest tests\nPDF report + editable slides\nArchitecture and failure analysis')
    card(s,6.82,1.98,5.64,3.88,'Student completion actions','Install / verify real AI4Bharat models\nAdd actual name and USN\nPublish your own GitHub repository\nCapture true UI demonstration\nAdd real model benchmark results')
    textbox(s,1.05,6.28,11.24,.4,'Repository-ready deliverable — no claim of a published GitHub URL.',16,SLATE)

    s=prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid();s.background.fill.fore_color.rgb=BLUE
    shape(s,.8,1.54,1.4,.13,GOLD,False)
    textbox(s,.80,2.0,10.9,1.13,'THANK YOU',47,WHITE,True)
    textbox(s,.84,3.17,11.6,.69,'BhashaWrite  •  CS3235 CIE3 Mini Project 4',25,RGBColor(170,233,222))
    textbox(s,.88,5.19,11.36,.65,'Questions: IndicXlit • transliteration vs translation • CER • error cases • model limits',17,WHITE)

    prs.save(str(DOCS/"BhashaWrite_Presentation.pptx"))

if __name__ == "__main__":
    make_pdf();make_slides()
    print(DOCS/"BhashaWrite_Project_Report.pdf")
    print(DOCS/"BhashaWrite_Presentation.pptx")
