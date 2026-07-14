from weasyprint import HTML
from datetime import datetime


class PdfGenerator:

    @classmethod
    def pdf_generator(cls, booking, parking) -> bytes:

        now = datetime.now()

        # Datos del cliente
        user = booking.user
        profile = user.profile
        client_name = f"{profile.name} {profile.last_name}" if profile else "Sin datos"
        client_dni = profile.dni if profile else "N/A"
        client_email = user.email

        # Datos de la empresa
        company = parking.company
        company_name = company.name if company else "N/A"
        company_cif = company.cif if company else "N/A"

        # Datos de la reserva
        booking_id = booking.id
        license_plate = booking.license_plate or "N/A"
        space_name = booking.space.name if booking.space else "N/A"
        parking_name = parking.name
        parking_location = parking.municipality or parking.province or ""
        start_date = booking.start_date
        end_date = booking.end_date
        nights = (end_date - start_date).days if start_date and end_date else 0
        space_price = booking.space.price if booking.space else 0.0
        total_price = booking.total_price

        # Nº de factura
        if booking.invoice_serie and booking.invoice_number:
            invoice_number = f"{booking.invoice_serie}-{booking.invoice_number}"
        else:
            invoice_number = "Pendiente"

        # Fecha de factura
        invoice_date = booking.invoice_date or now.strftime('%Y-%m-%d')

        # TicketBAI
        tbai_id = booking.tbai_id or "N/A"
        tbai_qr = booking.tbai_qr_code or ""

        html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Factura</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 30px;
                        color: #333;
                        font-size: 13px;
                    }}

                    .header {{
                        text-align: center;
                        border-bottom: 3px solid #2E2EFF;
                        padding-bottom: 15px;
                        margin-bottom: 20px;
                    }}

                    .header h1 {{
                        margin: 0;
                        color: #2E2EFF;
                        font-size: 28px;
                        text-transform: uppercase;
                    }}

                    .header p {{
                        margin: 4px 0;
                        color: #666;
                        font-size: 12px;
                    }}

                    .section {{
                        margin-bottom: 20px;
                    }}

                    .two-columns {{
                        display: flex;
                        gap: 30px;
                    }}

                    .two-columns .col {{
                        flex: 1;
                    }}

                    .col h3 {{
                        margin: 0 0 8px 0;
                        color: #2E2EFF;
                        font-size: 13px;
                        text-transform: uppercase;
                        border-bottom: 1px solid #ddd;
                        padding-bottom: 5px;
                    }}

                    .col p {{
                        margin: 3px 0;
                        font-size: 12px;
                    }}

                    .booking-details {{
                        background: #f8f9fa;
                        border: 1px solid #e9ecef;
                        border-radius: 6px;
                        padding: 15px;
                        margin-bottom: 20px;
                    }}

                    .booking-details h3 {{
                        margin: 0 0 10px 0;
                        color: #2E2EFF;
                        font-size: 13px;
                        text-transform: uppercase;
                    }}

                    .booking-grid {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 10px 30px;
                    }}

                    .booking-grid .item {{
                        min-width: 180px;
                    }}

                    .booking-grid .item label {{
                        font-size: 10px;
                        color: #888;
                        text-transform: uppercase;
                        display: block;
                        margin-bottom: 2px;
                    }}

                    .booking-grid .item span {{
                        font-size: 13px;
                        font-weight: bold;
                        color: #333;
                    }}

                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 10px;
                    }}

                    th {{
                        background: #2E2EFF;
                        color: white;
                        padding: 10px 8px;
                        text-align: left;
                        font-size: 12px;
                        text-transform: uppercase;
                    }}

                    td {{
                        padding: 10px 8px;
                        border-bottom: 1px solid #eee;
                        font-size: 12px;
                    }}

                    tr:nth-child(even) {{
                        background: #f8f9fa;
                    }}

                    .total-section {{
                        text-align: right;
                        margin-top: 20px;
                        padding: 15px;
                        background: #f0f4ff;
                        border-radius: 6px;
                    }}

                    .total-section .total-label {{
                        font-size: 14px;
                        color: #666;
                    }}

                    .total-section .total-amount {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #2E2EFF;
                        margin-top: 5px;
                    }}

                    .tbai-section {{
                        margin-top: 25px;
                        padding: 15px;
                        border: 1px solid #e9ecef;
                        border-radius: 6px;
                        display: flex;
                        align-items: center;
                        gap: 15px;
                    }}

                    .tbai-section .qr-img {{
                        width: 90px;
                        height: 90px;
                    }}

                    .tbai-section .tbai-info {{
                        font-size: 11px;
                        color: #666;
                    }}

                    .tbai-section .tbai-info strong {{
                        color: #333;
                        display: block;
                        margin-bottom: 3px;
                    }}

                    .footer {{
                        margin-top: 30px;
                        text-align: center;
                        font-size: 10px;
                        color: #aaa;
                        border-top: 1px solid #eee;
                        padding-top: 10px;
                    }}
                </style>
            </head>
            <body>

                <div class="header">
                    <h1>Factura</h1>
                    <p>Fecha: {invoice_date}</p>
                </div>

                <div class="two-columns">
                    <div class="col">
                        <h3>Empresa</h3>
                        <p><strong>{company_name}</strong></p>
                        <p>CIF: {company_cif}</p>
                    </div>
                    <div class="col">
                        <h3>Cliente</h3>
                        <p><strong>{client_name}</strong></p>
                        <p>DNI: {client_dni}</p>
                        <p>Email: {client_email}</p>
                    </div>
                </div>

                <div class="booking-details">
                    <h3>Datos de la Reserva</h3>
                    <div class="booking-grid">
                        <div class="item">
                            <label>Nº Reserva</label>
                            <span>#{booking_id}</span>
                        </div>
                        <div class="item">
                            <label>Matrícula</label>
                            <span>{license_plate}</span>
                        </div>
                        <div class="item">
                            <label>Plaza</label>
                            <span>{space_name}</span>
                        </div>
                        <div class="item">
                            <label>Parking</label>
                            <span>{parking_name} ({parking_location})</span>
                        </div>
                        <div class="item">
                            <label>Entrada</label>
                            <span>{start_date}</span>
                        </div>
                        <div class="item">
                            <label>Salida</label>
                            <span>{end_date}</span>
                        </div>
                        <div class="item">
                            <label>Noches</label>
                            <span>{nights}</span>
                        </div>
                    </div>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Concepto</th>
                            <th>Noches</th>
                            <th>Precio / noche</th>
                            <th>Importe</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Plaza "{space_name}" en {parking_name}</td>
                            <td>{nights}</td>
                            <td>{space_price:.2f} €</td>
                            <td>{nights * space_price:.2f} €</td>
                        </tr>
                    </tbody>
                </table>

                <div class="total-section">
                    <div class="total-label">TOTAL</div>
                    <div class="total-amount">{total_price:.2f} €</div>
                </div>

                <div class="tbai-section">
                    {f'<img class="qr-img" src="data:image/png;base64,{tbai_qr}" />' if tbai_qr else ''}
                    <div class="tbai-info">
                        <strong>TicketBAI</strong>
                        ID: {tbai_id}
                    </div>
                </div>

                <div class="footer">
                    Hemen-Go - Plataforma de reserva de aparcamientos para campers
                </div>

            </body>
            </html>
            """

        pdf_bytes = HTML(string=html).write_pdf()
        return pdf_bytes
