import os
import fitz  # PyMuPDF
from pyrogram import Client, filters
from pyrogram.types import Message

# Function to arrange PDF pages (N-up)
def arrange_pdf_pages(input_pdf, output_pdf, pages_per_sheet=4):
    doc = fitz.open(input_pdf)
    output_doc = fitz.open()

    # A4 paper size in points (landscape)
    A4_WIDTH, A4_HEIGHT = 842, 595  # Points (1 point = 1/72 inch)

    # Convert 0.5 mm to points (~1.42 points)
    gap = 1.42  

    # 2×2 layout for 4 pages per sheet
    cols, rows = (2, 2)

    # Page size (excluding gaps)
    page_width = (A4_WIDTH - (cols - 1) * gap) / cols
    page_height = (A4_HEIGHT - (rows - 1) * gap) / rows

    for i in range(0, len(doc), pages_per_sheet):
        new_page = output_doc.new_page(width=A4_WIDTH, height=A4_HEIGHT)

        for j in range(pages_per_sheet):
            if i + j >= len(doc):
                break  # Stop if no more pages

            page = doc[i + j]

            # Calculate position with gaps
            x_offset = (j % cols) * (page_width + gap)
            y_offset = (j // cols) * (page_height + gap)

            # Define the area where the page will be placed
            new_rect = fitz.Rect(x_offset, y_offset, x_offset + page_width, y_offset + page_height)

            # Insert and fit the page into the defined area
            new_page.show_pdf_page(new_rect, doc, i + j)

    output_doc.save(output_pdf)

# Command to handle /N-up when replying to a PDF
@Client.on_message(filters.command("N-up") & filters.reply)
async def n_up_handler(client: Client, message: Message):
    replied_msg = message.reply_to_message

    if not replied_msg or not replied_msg.document or not replied_msg.document.file_name.endswith(".pdf"):
        await message.reply("❌ Please reply to a PDF file.")
        return

    # Download the PDF
    pdf_path = f"{replied_msg.document.file_id}.pdf"
    await client.download_media(replied_msg, file_name=pdf_path)

    output_pdf = f"N-up_{replied_msg.document.file_name}"

    try:
        # Process PDF
        arrange_pdf_pages(pdf_path, output_pdf)

        # Send the processed PDF
        await message.reply_document(output_pdf, caption="✅ Here is your arranged PDF.")

    except Exception as e:
        await message.reply(f"❌ Error: {e}")

    finally:
        # Clean up files
        os.remove(pdf_path) if os.path.exists(pdf_path) else None
        os.remove(output_pdf) if os.path.exists(output_pdf) else None
