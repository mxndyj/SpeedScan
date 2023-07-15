from flask import Flask, render_template, request, send_file
import PyPDF2
import io

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

def process_pdf(file):
    # Perform PDF text editing using PyPDF2
    pdf_reader = PyPDF2.PdfReader(file)
    pdf_writer = PyPDF2.PdfWriter()

    # Modify the PDF text or perform other editing operations
    # Example: Rotating each page by 90 degrees
    for page in pdf_reader.pages:
        page.rotate(90)
        pdf_writer.add_page(page)

    # Save the edited PDF to a BytesIO object
    edited_pdf_io = io.BytesIO()
    pdf_writer.write(edited_pdf_io)
    edited_pdf_io.seek(0)

    return edited_pdf_io

if __name__ == '__main__':
    app.run(debug=True)
