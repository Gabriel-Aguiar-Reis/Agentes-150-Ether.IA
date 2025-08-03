import pandas as pd
import PyPDF2
import xml.etree.ElementTree as ET

def read_file(file_path, file_type):
    if file_type == "pdf":
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join(page.extract_text() for page in reader.pages)
        return {"content": text}

    elif file_type == "csv":
        return {"content": pd.read_csv(file_path).to_dict(orient="records")}

    elif file_type in ["xls", "xlsx"]:
        return {"content": pd.read_excel(file_path).to_dict(orient="records")}

    elif file_type == "xml":
        tree = ET.parse(file_path)
        root = tree.getroot()
        return {"content": [elem.attrib for elem in root]}

    else:
        raise ValueError("Tipo de arquivo não suportado")

