from fpdf import FPDF

class PdfGenerator:

    @classmethod
    def pdf_generator(cls, titulo, texto)-> bytes:
        pdf = FPDF()
        pdf.add_page()

        # ===== Encabezado =====
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 10, "FACTURA", ln=True, align="C")

        pdf.ln(5)

        pdf.set_font("Helvetica", "", 11)
        pdf.cell(100, 6, "Empresa:", ln=0)
        pdf.cell(0, 6, "Factura: F-2026-001", ln=1)
        pdf.cell(0, 6, titulo, ln=1)
        pdf.cell(0, 6, texto, ln=1)

        pdf.cell(100, 6, "NIF: B12345678", ln=0)
        pdf.cell(0, 6, "Fecha: 02/07/2026", ln=1)

        pdf.ln(8)

        # ===== Cliente =====
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Cliente", ln=True)

        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, "Nombre: Juan Perez", ln=True)
        pdf.cell(0, 6, "Direccion: Calle Mayor 10", ln=True)
        pdf.cell(0, 6, "Ciudad: Madrid", ln=True)

        pdf.ln(10)

        # ===== Cabecera de la tabla =====
        pdf.set_font("Helvetica", "B", 11)

        pdf.cell(90, 8, "Concepto", border=1)
        pdf.cell(25, 8, "Cantidad", border=1, align="C")
        pdf.cell(35, 8, "Precio", border=1, align="R")
        pdf.cell(40, 8, "Total", border=1, align="R", ln=True)

        pdf.set_font("Helvetica", "", 11)

        productos = [
            ("Desarrollo web", 1, 500.00),
            ("Mantenimiento", 2, 75.00),
            ("Hosting", 1, 60.00),
        ]

        subtotal = 0

        for concepto, cantidad, precio in productos:
            total = cantidad * precio
            subtotal += total

            pdf.cell(90, 8, concepto, border=1)
            pdf.cell(25, 8, str(cantidad), border=1, align="C")
            pdf.cell(35, 8, f"{precio:.2f} EUROS", border=1, align="R")
            pdf.cell(40, 8, f"{total:.2f} EUROS", border=1, align="R", ln=True)

        iva = subtotal * 0.21
        total = subtotal + iva

        pdf.ln(8)

        # ===== Totales =====
        pdf.set_font("Helvetica", "B", 11)

        pdf.cell(150)
        pdf.cell(40, 8, f"Subtotal: {subtotal:.2f} EUROS", ln=True, align="R")

        pdf.cell(150)
        pdf.cell(40, 8, f"IVA (21%): {iva:.2f} EUROS", ln=True, align="R")

        pdf.cell(150)
        pdf.cell(40, 8, f"TOTAL: {total:.2f} EUROS", ln=True, align="R")

        

        pdf_bytes = pdf.output(dest="S").encode("latin-1")
        return bytes(pdf_bytes)

