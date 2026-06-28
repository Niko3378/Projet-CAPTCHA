# -*- coding: utf-8 -*-
import re
import os
from fpdf import FPDF

with open('MANUEL.md', encoding='utf-8') as f:
    lines = f.readlines()

REPLACEMENTS = {
    '—': '-', '–': '-',
    '‘': "'", '’': "'",
    '“': '"', '”': '"',
    '…': '...',
    '\U0001f50a': '[Audio]',
    '✓': 'OK', '✗': 'X',
    '→': '->', '•': '-',
}


def clean(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    for k, v in REPLACEMENTS.items():
        text = text.replace(k, v)
    return text.encode('latin-1', errors='ignore').decode('latin-1')


class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(79, 70, 229)
        self.cell(0, 8, 'Manuel utilisation - Projet CAPTCHA IA', align='C')
        self.ln(3)
        self.set_draw_color(79, 70, 229)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def write_text(self, h, text):
        self.set_x(self.l_margin)
        self.multi_cell(0, h, text)

    def write_code(self, text):
        self.set_x(self.l_margin)
        self.set_font('Courier', size=8)
        self.set_text_color(226, 232, 240)
        self.set_fill_color(15, 23, 42)
        self.multi_cell(0, 5, text, fill=True)


pdf = PDF()
pdf.set_margins(15, 20, 15)
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=20)

in_code = False

for idx, line in enumerate(lines):
    raw = line.rstrip()

    if raw.startswith('```'):
        in_code = not in_code
        pdf.ln(2)
        if not in_code:
            pdf.set_fill_color(255, 255, 255)
        continue

    if in_code:
        pdf.write_code(raw.replace('\t', '    '))
        continue

    pdf.set_text_color(30, 41, 59)
    pdf.set_fill_color(255, 255, 255)

    if raw == '':
        pdf.ln(2)

    elif raw.startswith('# ') and not raw.startswith('## '):
        pdf.set_font('Helvetica', 'B', 18)
        pdf.set_text_color(79, 70, 229)
        pdf.ln(3)
        pdf.write_text(10, clean(raw[2:]))
        pdf.set_draw_color(79, 70, 229)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(4)

    elif raw.startswith('## '):
        pdf.set_font('Helvetica', 'B', 13)
        pdf.set_text_color(14, 165, 233)
        pdf.ln(4)
        pdf.write_text(8, clean(raw[3:]))
        pdf.set_draw_color(200, 210, 220)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(2)

    elif raw.startswith('### '):
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(51, 65, 85)
        pdf.ln(2)
        pdf.write_text(7, clean(raw[4:]))

    elif raw.startswith('| '):
        parts = [p.strip() for p in raw.split('|')[1:-1]]
        if not parts or all(set(p) <= set('-: ') for p in parts):
            continue
        col_w = 180 / max(len(parts), 1)
        next_line = lines[idx + 1].rstrip() if idx + 1 < len(lines) else ''
        is_header = '---' in next_line
        pdf.set_x(pdf.l_margin)
        for cell in parts:
            if is_header:
                pdf.set_fill_color(79, 70, 229)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font('Helvetica', 'B', 8)
            else:
                pdf.set_fill_color(248, 250, 252)
                pdf.set_text_color(30, 41, 59)
                pdf.set_font('Helvetica', size=8)
            pdf.cell(col_w, 6, clean(cell)[:50], border=1, fill=True)
        pdf.ln()
        pdf.set_x(pdf.l_margin)

    elif raw.startswith('- ') or raw.startswith('* '):
        pdf.set_font('Helvetica', size=10)
        pdf.set_text_color(30, 41, 59)
        pdf.write_text(6, '  -  ' + clean(raw[2:]))

    elif raw.startswith('---'):
        pdf.set_draw_color(226, 232, 240)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(3)

    else:
        pdf.set_font('Helvetica', size=10)
        pdf.set_text_color(30, 41, 59)
        pdf.write_text(6, clean(raw))

pdf.output('MANUEL.pdf')
print('PDF genere : MANUEL.pdf')
print('Taille :', round(os.path.getsize('MANUEL.pdf') / 1024, 1), 'KB')
