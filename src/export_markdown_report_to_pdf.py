from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch

ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / 'notebooks' / 'Shota Emoto' / 'results' / 'copilot' / 'k3_cluster_analysis_report.md'
REPORT_PDF = REPORT_MD.with_suffix('.pdf')


def read_markdown_as_paragraphs(path: Path) -> list[str]:
    text = path.read_text(encoding='utf-8')
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def build_pdf() -> None:
    doc = SimpleDocTemplate(str(REPORT_PDF), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph('3-cluster analysis report', styles['Title']))
    story.append(Spacer(1, 0.2 * inch))

    for line in read_markdown_as_paragraphs(REPORT_MD):
        if line.startswith('!['):
            image_path = ROOT / line.split('(')[1].split(')')[0]
            if image_path.exists():
                story.append(Image(str(image_path), width=5.5 * inch, height=3.5 * inch))
                story.append(Spacer(1, 0.1 * inch))
        else:
            story.append(Paragraph(line, styles['BodyText']))
            story.append(Spacer(1, 0.08 * inch))

    doc.build(story)
    print(f'Saved PDF report to: {REPORT_PDF}')


if __name__ == '__main__':
    build_pdf()
