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
