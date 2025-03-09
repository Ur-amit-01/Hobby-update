import os
from pyrogram import Client, filters
from pyrogram.types import Message
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from io import BytesIO

# Function to create N-up PDF
def create_n_up_pdf(input_pdf_path, output_pdf_path, n_up=2, gap=0.5):
    # Read the input PDF
    reader = PdfReader(input_pdf_path)
    num_pages = len(reader.pages)

    # Create a new PDF with A4 landscape orientation
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Calculate the size of each page
    page_width = (width - (n_up + 1) * gap * mm) / n_up
    page_height = (height - (n_up + 1) * gap * mm) / n_up

    for i in range(num_pages):
        if i % n_up == 0 and i != 0:
            can.showPage()  # Create a new page after every n_up pages

        x = (i % n_up) * (page_width + gap * mm) + gap * mm
        y = height - page_height - gap * mm

        # Draw the page
        can.drawImage(input_pdf_path, x, y, width=page_width, height=page_height, preserveAspectRatio=True, mask='auto')

    can.save()

    # Move to the beginning of the BytesIO buffer
    packet.seek(0)

    # Read the new PDF
    new_pdf = PdfReader(packet)
    writer = PdfWriter()

    for page in new_pdf.pages:
        writer.add_page(page)

    # Write the output PDF
    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

# Handler for /N-up command
@Client.on_message(filters.command("N_up") & filters.document)
async def handle_n_up(client: Client, message: Message):
    # Check if the document is a PDF
    if message.document.mime_type == "application/pdf":
        # Download the PDF file
        input_pdf_path = "input.pdf"
        output_pdf_path = "output_n_up.pdf"

        await message.download(file_name=input_pdf_path)

        # Create N-up PDF
        create_n_up_pdf(input_pdf_path, output_pdf_path)

        # Send the processed PDF back to the user
        await message.reply_document(document=output_pdf_path)

        # Clean up files
        os.remove(input_pdf_path)
        os.remove(output_pdf_path)
    else:
        await message.reply("Please send a PDF file.")

