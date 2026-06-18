# -*- coding: utf-8 -*-
"""
Converte os documentos Markdown de documentos/ em PDF.
Markdown -> HTML (lib markdown) -> PDF (xhtml2pdf / pisa), com estilo
corporativo claro (acento teal do Grupo Avelar) e fonte monoespaçada
Consolas para os diagramas em ASCII.
"""
import os
import re
import markdown
from xhtml2pdf import pisa
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Registra a Consolas (tem os caracteres de caixa dos diagramas ASCII).
pdfmetrics.registerFont(TTFont("Mono", r"C:\Windows\Fonts\consola.ttf"))

BASE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(BASE, "documentos")
DOCS = [
    "01-premissas-e-decisoes.md",
    "02-modelo-de-dados.md",
    "03-resumo-executivo.md",
]

# Caracteres que as fontes base do PDF (Helvetica) não possuem -> equivalentes ASCII.
SUBST = {"→": "->", "◄": "<", "≥": ">=", "≤": "<="}

CSS = """
@page { size: A4; margin: 1.9cm 1.7cm; }
body { font-family: Helvetica, sans-serif; font-size: 10.5pt; color: #232c34; }
h1 { font-size: 18pt; color: #1d2730; border-bottom: 2pt solid #46B3A3;
     padding-bottom: 5pt; margin-bottom: 10pt; }
h2 { font-size: 13pt; color: #2C8C7E; margin-top: 15pt; margin-bottom: 5pt; }
h3 { font-size: 11pt; color: #33414f; margin-top: 10pt; }
p  { margin: 5pt 0; line-height: 145%; }
strong { color: #1d2730; }
a { color: #2C8C7E; text-decoration: none; }
ul, ol { margin: 4pt 0 4pt 14pt; }
li { margin: 2pt 0; }
hr { border: none; border-top: 0.5pt solid #d6dde3; margin: 12pt 0; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; }
th { background: #1f2a33; color: #ffffff; font-size: 8.5pt; padding: 5pt 6pt;
     border: 0.5pt solid #b9c2cb; text-align: left; }
td { font-size: 9pt; padding: 5pt 6pt; border: 0.5pt solid #cfd6dd; }
tr:nth-child(even) td { background: #f3f6f8; }
pre { font-family: 'Mono'; font-size: 6.8pt; background: #f4f6f8;
      border: 0.5pt solid #dde3e8; padding: 7pt; }
code { font-family: 'Mono'; font-size: 9pt; color: #234; }
blockquote { color: #5a6b7a; border-left: 3pt solid #cdd5dd;
             padding: 2pt 0 2pt 9pt; font-size: 9.5pt; }
"""

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{css}</style></head><body>{body}</body></html>"""


def preparar(md_text):
    # remove o bloco mermaid (não renderiza em PDF); mantém o ASCII abaixo dele
    md_text = re.sub(r"```mermaid.*?```",
                     "_(diagrama de fluxo — representação textual abaixo)_",
                     md_text, flags=re.DOTALL)
    for k, v in SUBST.items():
        md_text = md_text.replace(k, v)
    return md_text


def converter(md_path, pdf_path):
    with open(md_path, encoding="utf-8") as f:
        md_text = preparar(f.read())
    body = markdown.markdown(
        md_text, extensions=["tables", "fenced_code", "sane_lists", "attr_list"]
    )
    html = HTML.format(css=CSS, body=body)
    with open(pdf_path, "wb") as out:
        result = pisa.CreatePDF(html, dest=out, encoding="utf-8")
    return not result.err


def main():
    ok = True
    for doc in DOCS:
        md_path = os.path.join(DIR, doc)
        pdf_path = os.path.join(DIR, doc.replace(".md", ".pdf"))
        good = converter(md_path, pdf_path)
        print(("OK   " if good else "FALHA") + "  " + os.path.basename(pdf_path))
        ok = ok and good
    print("\nConcluído." if ok else "\nHouve erro em algum documento.")


if __name__ == "__main__":
    main()
