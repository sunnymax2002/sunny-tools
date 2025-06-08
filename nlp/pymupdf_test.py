import pymupdf
import pathlib
import pymupdf4llm

def writeText2File(text, ftxt):
	# Write the text to some file in UTF8-encoding
	pathlib.Path(ftxt).write_bytes(text.encode())

def pdf2md(fpdf, ftxt):
	"""Convert PDF to Markdown using pymupdf4llm."""

	md_text = pymupdf4llm.to_markdown(fpdf, ignore_images=True, ignore_graphics=True, show_progress=True)
	
	# Write the Markdown text to some file in UTF8-encoding
	writeText2File(md_text, ftxt)

def pdf2txt(fpdf, ftxt):
	"""Convert PDF to text using pymupdf."""

	with pymupdf.open(fname) as doc:  # open document
		text = chr(12).join([page.get_text() for page in doc])
	
	# Write the text to some file in UTF8-encoding
	writeText2File(text, ftxt)

fname = r"C:\Users\sunny\sunny_tools_data\finance\chatpdf\2025-04_ECT_Shilchar.pdf"
fname = r"H:\My Drive\Financials\Stock Analysis\Nvidia\AR_Nvidia_2024.pdf"
fname = r"H:\My Drive\Financials\Stock Analysis\HUL\HUL-AR-2024-25.pdf"

#sys.argv[1]  # get document filename

ftxt = fname + ".txt"  # output filename
pdf2txt(fname, ftxt)

ftxt = fname + ".md"  # output filename
pdf2md(fname, ftxt)