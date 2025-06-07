import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_pdf(filename, text):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 100, text)
    c.save()

def generate_test_files():
    # Create test directory structure
    os.makedirs("tests/office/test_pdf_merge/test_dir1", exist_ok=True)
    os.makedirs("tests/office/test_pdf_merge/test_dir1/subdir", exist_ok=True)

    # Create test PDF files
    create_pdf("tests/office/test_pdf_merge/top_level.pdf", "Top level PDF")
    create_pdf("tests/office/test_pdf_merge/test_dir1/file1.pdf", "First level PDF 1")
    create_pdf("tests/office/test_pdf_merge/test_dir1/file2.pdf", "First level PDF 2")
    create_pdf("tests/office/test_pdf_merge/test_dir1/subdir/file3.pdf", "Second level PDF")

if __name__ == "__main__":
    generate_test_files()
