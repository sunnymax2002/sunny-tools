import spacy
from spacy_layout import spaCyLayout

nlp = spacy.load("en_core_web_sm")
layout = spaCyLayout(nlp)

doc = layout(r"C:\Users\sunny\sunny_tools_data\finance\chatpdf\2025-04_ECT_Shilchar.pdf") #H:\My Drive\Financials\Stock Analysis\Nvidia\AR_Nvidia_2024.pdf"

# Extract the full text
print(doc.text)