from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from inventario.db.models import Producto, Salida, Usuario


def generar_pdf_salida(
    salida: Salida,
    producto: Producto,
    usuario: Usuario,
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"salida_{salida.id:06d}.pdf"
    pdf_path = output_dir / file_name

    pdf = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    y = height - 60

    pdf.setTitle(f"Salida {salida.id}")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Comprobante de salida")

    y -= 40
    pdf.setFont("Helvetica", 11)
    rows = [
        ("Numero de documento", f"SAL-{salida.id:06d}"),
        ("Fecha", str(salida.fecha)),
        ("Codigo producto", producto.codigo),
        ("Nombre producto", producto.nombre),
        ("Unidad de medida", producto.unidad_medida),
        ("Cantidad salida", str(salida.cantidad)),
        ("Tipo de salida", salida.tipo_salida),
        ("Usuario", usuario.usuario),
        ("Observacion", salida.observacion or "-"),
        ("Stock restante", str(producto.stock_actual)),
    ]

    for label, value in rows:
        pdf.drawString(50, y, f"{label}: {value}")
        y -= 24

    pdf.line(50, y, width - 50, y)
    y -= 30
    pdf.drawString(50, y, "Documento generado automaticamente por el sistema.")
    pdf.save()
    return pdf_path


def generar_pdf_tabular(
    titulo: str,
    encabezados: list[str],
    filas: list[list[str]],
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4
    top_margin = height - 50
    left_margin = 40
    row_height = 18

    def draw_page_header(page_title: str) -> float:
        y_pos = top_margin
        pdf.setFont("Helvetica-Bold", 15)
        pdf.drawString(left_margin, y_pos, page_title)
        y_pos -= 28
        pdf.setFont("Helvetica-Bold", 9)
        x_pos = left_margin
        for header in encabezados:
            pdf.drawString(x_pos, y_pos, _truncate(header, 18))
            x_pos += 65
        y_pos -= 12
        pdf.line(left_margin, y_pos, width - left_margin, y_pos)
        return y_pos - 14

    y = draw_page_header(titulo)
    pdf.setFont("Helvetica", 8)

    for fila in filas:
        if y < 60:
            pdf.showPage()
            y = draw_page_header(titulo)
            pdf.setFont("Helvetica", 8)

        x = left_margin
        for value in fila:
            pdf.drawString(x, y, _truncate(value, 18))
            x += 65
        y -= row_height

    pdf.save()
    return output_path


def _truncate(value: str, limit: int) -> str:
    text = str(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."
