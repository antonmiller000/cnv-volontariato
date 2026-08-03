#!/usr/bin/env python3
"""Build trail-angels-stories-<lang>.pdf for every stories/<lang>.json present.

Uses Arial / Arial Bold embedded as TTF subsets so Greek, Cyrillic and every EU
diacritic (Romanian s/t-comma, Maltese h-bar, Latvian macrons, ...) render.
The CNV mark and the EU flag are drawn as vectors; the ESC logo is the official
PNG artwork.
"""
import json, glob, math, os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLTTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, PageBreak, NextPageTemplate)

SITE = '/Users/antonrubanenko/Desktop/CNV/site'
ESC_PNG = os.path.join(SITE, 'esc-logo.png')

# ── Unicode fonts ────────────────────────────────────────────────────────────
SUP = '/System/Library/Fonts/Supplemental'
pdfmetrics.registerFont(RLTTFont('CNVSans',      f'{SUP}/Arial.ttf'))
pdfmetrics.registerFont(RLTTFont('CNVSans-Bold', f'{SUP}/Arial Bold.ttf'))
pdfmetrics.registerFontFamily('CNVSans', normal='CNVSans', bold='CNVSans-Bold',
                              italic='CNVSans', boldItalic='CNVSans-Bold')
F, FB = 'CNVSans', 'CNVSans-Bold'

CNV_GREEN = colors.HexColor('#31A246'); CNV_GREY = colors.HexColor('#ACB0B8')
EU_BLUE   = colors.HexColor('#003399'); EU_GOLD  = colors.HexColor('#FFCC00')
INK = colors.HexColor('#1a1a1a');       MUTED    = colors.HexColor('#666666')

# ── vector logos ─────────────────────────────────────────────────────────────
def draw_cnv(c, x, y, h):
    SH = 1970.78; s = h / SH
    c.saveState(); c.translate(x, y); c.scale(s, -s); c.translate(-45.49, -2135.41)
    p = c.beginPath()
    p.moveTo(1469.27, 164.63); p.lineTo(1937.76, 164.63); p.lineTo(995.56, 2135.41)
    p.lineTo(45.49, 164.63);   p.lineTo(521.84, 164.63);  p.lineTo(675.71, 455.16)
    p.curveTo(675.71, 455.16, 974.62, 1044.05, 1319.83, 455.16); p.close()
    c.setFillColor(CNV_GREEN); c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(CNV_GREY);  c.circle(996.87, 395.93, 229.38, fill=1, stroke=0)
    c.restoreState()

def draw_eu_flag(c, x, y, w):
    h = w * 2.0 / 3.0
    c.saveState(); c.setFillColor(EU_BLUE); c.rect(x, y, w, h, fill=1, stroke=0)
    cx, cy, ring, R = x + w/2, y + h/2, h/3.0, h/18.0
    r = R * math.cos(math.radians(72)) / math.cos(math.radians(36))
    c.setFillColor(EU_GOLD)
    for k in range(12):
        a = math.radians(k*30); sx, sy = cx + ring*math.sin(a), cy + ring*math.cos(a)
        p = c.beginPath()
        for i in range(10):
            th = math.radians(90 + i*36); rad = R if i % 2 == 0 else r
            px, py = sx + rad*math.cos(th), sy + rad*math.sin(th)
            p.moveTo(px, py) if i == 0 else p.lineTo(px, py)
        p.close(); c.drawPath(p, fill=1, stroke=0)
    c.restoreState()
    return h

def draw_eu_funded(c, x, y, fw, l1, l2):
    fh = draw_eu_flag(c, x, y, fw)
    c.setFont(FB, 7.2); c.setFillColor(EU_BLUE)
    c.drawString(x + fw + 6, y + fh - 7.2, l1)
    c.drawString(x + fw + 6, y + fh - 16.0, l2)
    return fh

def draw_esc(c, x, y, fw):
    fh = fw * 2.0 / 3.0
    c.drawImage(ESC_PNG, x, y, width=fh*208.0/56.0, height=fh, mask='auto')
    return fh

# ── page furniture ───────────────────────────────────────────────────────────
def make_pages(d):
    ui, endo = d['ui'], d.get('endonym', d.get('name', d['lang']))
    f1, f2 = ui.get('funded1', 'Funded by'), ui.get('funded2', 'the European Union')
    disc = ui.get('disclaimer', [])

    def cover(c, doc):
        W, H = A4
        c.setFillColor(colors.HexColor('#f4faf5')); c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(CNV_GREEN); c.rect(0, H-14*mm, W, 14*mm, fill=1, stroke=0)
        draw_cnv(c, 26*mm, H-52*mm, 26*mm)
        c.setFillColor(INK); c.setFont(FB, 12)
        c.drawString(26*mm, H-62*mm, 'Centro Nazionale per il Volontariato')
        c.setFillColor(CNV_GREEN); c.setFont(FB, 8)
        c.drawString(26*mm, H-67*mm, 'LUCCA · TOSCANA · ITALIA')
        c.setFillColor(INK); c.setFont(FB, 40)
        c.drawString(26*mm, H-108*mm, 'Trail Angels')
        c.setFillColor(CNV_GREEN); c.setFont(FB, 15)
        c.drawString(26*mm, H-120*mm, ui.get('pdf_title', 'Volunteer Stories 2023–2026'))
        c.setFillColor(MUTED); c.setFont(F, 10)
        c.drawString(26*mm, H-130*mm, ui.get('pdf_sub', ''))
        # language badge
        c.setFillColor(CNV_GREEN); c.roundRect(26*mm, H-141*mm, 46*mm, 7*mm, 3, fill=1, stroke=0)
        c.setFillColor(colors.white); c.setFont(FB, 7.6)
        c.drawString(29*mm, H-139.2*mm, f"{endo.upper()}  ·  {d['lang'].upper()}")
        c.setStrokeColor(colors.HexColor('#cfe3d4')); c.setLineWidth(1)
        c.line(26*mm, H-148*mm, W-26*mm, H-148*mm)
        c.setFillColor(MUTED); c.setFont(F, 8.6)
        for i, ln in enumerate([
            'European Solidarity Corps · Project No. 101093414',
            'Call ESC-SOLID-2022-VTHPA · ESC Solidarity Volunteering Unit Grants',
            'Coordinator: Centro Nazionale per il Volontariato (CNV), Lucca — Italy',
            'Partners: Studio Progetto Società Cooperativa Sociale (IT) · Internationaler Bund Polska (PL)',
            'Granting authority: European Education and Culture Executive Agency (EACEA)',
        ]):
            c.drawString(26*mm, H-157*mm - i*5.4*mm, ln)
        draw_eu_funded(c, 26*mm, 30*mm, 40, f1, f2)
        draw_esc(c, 104*mm, 30*mm, 40)
        c.setFillColor(colors.HexColor('#8a9a8d')); c.setFont(F, 6.9)
        for i, ln in enumerate(disc[:3]):
            c.drawString(26*mm, 20*mm - i*4*mm, ln)

    def body(c, doc):
        W, H = A4
        c.setFillColor(CNV_GREEN); c.rect(0, H-6*mm, W, 6*mm, fill=1, stroke=0)
        draw_cnv(c, 20*mm, H-20*mm, 10*mm)
        c.setFillColor(MUTED); c.setFont(FB, 7.4)
        c.drawString(31*mm, H-16*mm, 'TRAIL ANGELS · ' + ui.get('pdf_running', 'VOLUNTEER STORIES').upper())
        c.setFont(F, 7)
        c.drawString(31*mm, H-19.4*mm, f"ESC 101093414 · CNV Lucca · {endo}")
        draw_eu_funded(c, W-92*mm, H-21*mm, 25, f1, f2)
        draw_esc(c, W-46*mm, H-21*mm, 25)
        c.setStrokeColor(colors.HexColor('#e4ece5')); c.setLineWidth(.7)
        c.line(20*mm, H-24*mm, W-20*mm, H-24*mm); c.line(20*mm, 17*mm, W-20*mm, 17*mm)
        c.setFillColor(colors.HexColor('#9aa79c')); c.setFont(F, 6.8)
        c.drawString(20*mm, 12.5*mm, disc[0] if disc else '')
        c.drawRightString(W-20*mm, 12.5*mm, str(doc.page - 1))
    return cover, body

def build(path):
    d = json.load(open(path, encoding='utf-8'))
    lang = d['lang']
    out = os.path.join(SITE, f'trail-angels-stories-{lang}.pdf')
    cover, body = make_pages(d)
    H1 = ParagraphStyle('H1', fontName=FB, fontSize=16.5, leading=20.5, textColor=INK, spaceAfter=3)
    KICK = ParagraphStyle('K', fontName=FB, fontSize=7.8, textColor=CNV_GREEN, spaceAfter=11)
    BODY = ParagraphStyle('B', fontName=F, fontSize=9.9, leading=15.4,
                          textColor=colors.HexColor('#333333'), alignment=TA_JUSTIFY, spaceAfter=8)
    doc = BaseDocTemplate(out, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm,
                          topMargin=30*mm, bottomMargin=22*mm,
                          title=f"Trail Angels — {d['ui'].get('pdf_title','Volunteer Stories')} ({d.get('endonym',lang)})",
                          author='Centro Nazionale per il Volontariato (CNV), Lucca',
                          subject='ESC Project No. 101093414', lang=lang)
    fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='n')
    doc.addPageTemplates([
        PageTemplate(id='cover', frames=[Frame(0, 0, A4[0], A4[1], id='c')], onPage=cover),
        PageTemplate(id='body',  frames=[fr], onPage=body),
    ])
    story = [NextPageTemplate('body'), PageBreak()]
    for i, t in enumerate(d['teams']):
        if i: story.append(PageBreak())
        story.append(Paragraph(t['kicker'].upper(), KICK))
        story.append(Paragraph(t['title'], H1))
        story.append(Spacer(1, 7))
        for p in t['paragraphs']:
            story.append(Paragraph(p, BODY))
    doc.build(story)
    return out, doc.page

if __name__ == '__main__':
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(SITE, 'stories', '*.json')))
    for p in files:
        out, pages = build(p)
        print(f'  {os.path.basename(out):38s} {pages:3d} pages  {os.path.getsize(out)//1024:4d} KB')
