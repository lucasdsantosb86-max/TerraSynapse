from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def build_simple_pdf(title: str, body: str) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height-60, title[:90])
    c.setFont("Helvetica", 11)
    y = height - 100
    for line in body.split("\n"):
        c.drawString(50, y, line[:110])
        y -= 16
        if y < 80:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 80
    c.showPage()
    c.save()
    return buf.getvalue()
