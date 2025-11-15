from typing import List, Dict
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm


def export_table_pdf(filepath: Path, title: str, headers: List[str], rows: List[List[str]]) -> None:
	c = canvas.Canvas(str(filepath), pagesize=A4)
	width, height = A4
	margin = 2 * cm
	y = height - margin
	# Title
	c.setFont("Helvetica-Bold", 14)
	c.drawString(margin, y, title)
	y -= 1 * cm

	# Headers
	c.setFont("Helvetica-Bold", 10)
	x = margin
	col_widths = [ (width - 2*margin) / max(1, len(headers)) ] * len(headers)
	for i, h in enumerate(headers):
		c.drawString(x, y, str(h))
		x += col_widths[i]
	y -= 0.6 * cm

	# Rows
	c.setFont("Helvetica", 9)
	for row in rows:
		x = margin
		for i, cell in enumerate(row):
			c.drawString(x, y, str(cell))
			x += col_widths[i]
		y -= 0.5 * cm
		if y < margin:
			c.showPage()
			y = height - margin
			c.setFont("Helvetica", 9)

	c.showPage()
	c.save()


def export_sale_receipt(filepath: Path, title: str, meta: dict) -> None:
	c = canvas.Canvas(str(filepath), pagesize=A4)
	width, height = A4
	margin = 2 * cm
	y = height - margin

	c.setFont("Helvetica-Bold", 16)
	c.drawString(margin, y, title)
	y -= 1 * cm

	c.setFont("Helvetica", 11)
	for k in ["date", "lot", "quantite", "prix_unitaire", "montant", "client"]:
		line = f"{k.capitalize()}: {meta.get(k, '')}"
		c.drawString(margin, y, line)
		y -= 0.6 * cm

	c.setFont("Helvetica-Oblique", 9)
	c.drawString(margin, margin, "Merci pour votre confiance.")
	c.showPage()
	c.save()


