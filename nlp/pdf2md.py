from markitdown import MarkItDown
import pathlib

def writeText2File(text, ftxt):
	# Write the text to some file in UTF8-encoding
	pathlib.Path(ftxt).write_bytes(text.encode())

fpdf = r"H:\My Drive\Financials\Stock Analysis\LTTS\AR-FY2024-25.pdf"
ftxt = fpdf + ".md"  # output filename

md = MarkItDown(enable_plugins=False) # Set to True to enable plugins
result = md.convert(fpdf)
writeText2File(result.text_content, ftxt)