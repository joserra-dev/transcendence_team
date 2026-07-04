
from weasyprint import HTML
from datetime import datetime

class PdfGenerator:

    @classmethod
    def pdf_generator(cls, booking, parking)-> bytes:
        
        now = datetime.now()

        html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Factura</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 40px;
                        color: #333;
                    }}

                    h1 {{
                        color: #2c3e50;
                    }}

                    .info {{
                        margin-bottom: 20px;
                    }}

                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }}

                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                    }}

                    th {{
                        background: #f4f4f4;
                        text-align: left;
                    }}

                    .total {{
                        text-align: right;
                        margin-top: 20px;
                        font-size: 18px;
                        font-weight: bold;
                    }}
                </style>
            </head>
            <body>

                <h1>FACTURA</h1>

                <div class="info">
                    <p><strong>Nº Factura:</strong> FAC-2026-001</p>
                    <p><strong>Cliente:</strong> { booking.user } </p>
                    <p><strong>Fechas:</strong> { booking.start_date } - { booking.end_date }</p>
                    <p><strong>Ticket bai:</strong> { booking.tbai_id }</p>
                    <p> { booking.tbai_qr_code } </p>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Concepto</th>
                            <th>Cantidad</th>
                            <th>Precio</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td> { parking.name } </td>
                            <td>2</td>
                            <td>100.00 €</td>
                        </tr>
                    </tbody>
                </table>

                <div class="total">
                    TOTAL: { booking.total_price } €
                </div>

            </body>
            </html>
            """

        # Genera el PDF como bytes
        pdf_bytes = HTML(string=html).write_pdf()
        return (pdf_bytes)
        
