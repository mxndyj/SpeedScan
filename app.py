from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Handle file upload and text editing logic
    uploaded_file = request.files['pdfFile']
    edited_pdf_io = process_pdf(uploaded_file)

    # Return the edited PDF as a downloadable file
    edited_pdf_io.seek(0)  # Reset the file pointer to the beginning
    return send_file(
        edited_pdf_io,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='edited_pdf.pdf'
    )

@app.route('/upload', methods=['POST'])
def process_pdf(file):
    reader = PdfReader(file)
    output = BytesIO()

    # Calculate the available space on each page
    page_width, page_height = letter
    margin = 72  # 1 inch margin
    content_width = page_width - 2 * margin
    content_height = page_height - 2 * margin

    c = canvas.Canvas(output, pagesize=letter)
    font_size = 13  # Adjust the font size as desired
    line_spacing = 12  # Adjust the line spacing as desired
    word_spacing = 5.2  # Adjust the spacing between words as desired

    for page in reader.pages:
        content = page.extract_text()
        words = content.split()

        # Initialize the position for adding words
        x = margin
        y = margin + content_height - font_size  # Start from the top of the content area

        for word in words:
            # Calculate the width of the word including additional spacing
            word_width = c.stringWidth(word, "Helvetica", font_size) + word_spacing

            # Calculate the remaining space on the current line
            remaining_space = content_width - (x - margin)

            # Check if the word can fit on the current line
            if word_width > remaining_space:
                # Move to the next line
                x = margin
                y -= font_size + line_spacing  # Adjust the line spacing based on font size

                # Check if the remaining space on the page can accommodate the next line
                if y < margin:
                    # Create a new page
                    c.showPage()
                    y = margin + content_height - font_size  # Start from the top of the content area

            # Check if the word exceeds the available content height
            if y - font_size < 0:
                # Create a new page
                c.showPage()
                y = margin + content_height - font_size  # Start from the top of the content area

            # Split the word into two halves
            half_length = len(word) // 2
            first_half = word[:half_length]
            second_half = word[half_length:]

            # Draw the first half of the word in bold
            c.setFont("Helvetica-Bold", font_size)
            c.drawString(x, y, first_half)

            # Calculate the width of the first half
            first_half_width = c.stringWidth(first_half, "Helvetica-Bold", font_size)

            # Draw the second half of the word normally
            c.setFont("Helvetica", font_size)
            c.drawString(x + first_half_width, y, second_half)

            # Move to the next position
            x += word_width

        # Check if the remaining space on the page can accommodate the header
        if y - margin >= font_size + line_spacing:
            # Reset the position to the top of the page
            x = margin
            y -= font_size + line_spacing  # Adjust the line spacing based on font size

        c.showPage()

    c.save()
    output.seek(0)
    return output

if __name__ == '__main__':
    app.run(debug=True)
