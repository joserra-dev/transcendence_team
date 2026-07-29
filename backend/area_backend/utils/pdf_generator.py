from weasyprint import HTML
from datetime import datetime
from flask import render_template
from flask_babel import _, get_locale


class PdfGenerator:

    @classmethod
    def pdf_generator(cls, booking, parking) -> bytes:
        actual_locale = get_locale()
        idioma = actual_locale.language
        now = datetime.now()

        # Datos del cliente
        user = booking.user
        profile = user.profile
        client_name = f"{profile.name} {profile.last_name}" if profile else "N/A"
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
       
        # Fecha de factura
        invoice_date =  now.strftime('%Y-%m-%d')

        html_content = render_template(
            f'factura/{idioma}/factura.html',
            invoice_date = invoice_date,
            client_name=client_name,
            company_name=company_name,
            client_dni = client_dni,
            client_email = client_email,
            company = company,
            company_cif = company_cif,
            booking_id = booking.id,
            license_plate = license_plate,
            space_name = space_name,
            parking_name = parking_name,
            parking_location = parking_location,
            start_date = start_date,
            end_date = end_date,
            nights = nights,
            space_price = space_price,
            total_price = total_price
        )

        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
