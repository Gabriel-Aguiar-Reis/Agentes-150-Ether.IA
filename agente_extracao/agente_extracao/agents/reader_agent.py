import pandas as pd
import pypdf
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from pathlib import Path
import hashlib

def read_file(file_path, file_type):
    """
    Extrai dados estruturados de diferentes tipos de arquivo,
    retornando um JSON bem formatado para inserção em banco NoSQL
    """
    base_metadata = _get_file_metadata(file_path, file_type)

    match file_type:
        case "pdf":
            return _process_pdf(file_path, base_metadata)
        case "csv":
            return _process_csv(file_path, base_metadata)
        case "xls" | "xlsx":
            return _process_excel(file_path, base_metadata)
        case "xml":
            return _process_xml(file_path, base_metadata)
        case _:
            raise ValueError(f"Tipo de arquivo não suportado: {file_type}")

def _get_file_metadata(file_path, file_type):
    """Gera metadados básicos do arquivo"""
    file_path_obj = Path(file_path)
    file_stats = file_path_obj.stat()
    
    # Hash do arquivo para identificação única
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    
    return {
        "metadata": {
            "file_name": file_path_obj.name,
            "file_path": str(file_path_obj.absolute()),
            "file_type": file_type,
            "file_size": file_stats.st_size,
            "file_hash": file_hash,
            "created_at": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            "processed_at": datetime.now().isoformat()
        }
    }

def _process_pdf(file_path, base_metadata):
    """Processa PDF extraindo texto estruturado por páginas"""
    try:
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            
            pages_content = []
            full_text = ""
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                full_text += page_text + "\n"
                
                pages_content.append({
                    "page_number": page_num,
                    "text": page_text,
                    "word_count": len(page_text.split()),
                    "char_count": len(page_text)
                })
            
            # Extração de padrões comuns
            extracted_data = _extract_common_patterns(full_text)
            
            return {
                **base_metadata,
                "document_info": {
                    "total_pages": len(reader.pages),
                    "total_words": len(full_text.split()),
                    "total_chars": len(full_text)
                },
                "content": {
                    "full_text": full_text,
                    "pages": pages_content,
                    "extracted_patterns": extracted_data
                }
            }
    except Exception as e:
        return {**base_metadata, "error": str(e), "content": None}

def _process_csv(file_path, base_metadata):
    """Processa CSV com análise de estrutura e tipos de dados"""
    try:
        df = pd.read_csv(file_path)
        
        # Análise da estrutura
        column_info = {}
        for col in df.columns:
            column_info[col] = {
                "data_type": str(df[col].dtype),
                "non_null_count": int(df[col].count()),
                "null_count": int(df[col].isnull().sum()),
                "unique_values": int(df[col].nunique()),
                "sample_values": df[col].dropna().head(3).tolist()
            }
        
        return {
            **base_metadata,
            "structure_info": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": list(df.columns),
                "column_analysis": column_info
            },
            "content": {
                "records": df.to_dict(orient="records"),
                "summary_stats": df.describe(include='all').to_dict() if not df.empty else {}
            }
        }
    except Exception as e:
        return {**base_metadata, "error": str(e), "content": None}

def _process_excel(file_path, base_metadata):
    """Processa Excel com suporte a múltiplas planilhas"""
    try:
        excel_file = pd.ExcelFile(file_path)
        sheets_data = {}
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Análise da estrutura por planilha
            column_info = {}
            for col in df.columns:
                column_info[col] = {
                    "data_type": str(df[col].dtype),
                    "non_null_count": int(df[col].count()),
                    "null_count": int(df[col].isnull().sum()),
                    "unique_values": int(df[col].nunique())
                }
            
            sheets_data[sheet_name] = {
                "structure_info": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "columns": list(df.columns),
                    "column_analysis": column_info
                },
                "records": df.to_dict(orient="records")
            }
        
        return {
            **base_metadata,
            "workbook_info": {
                "total_sheets": len(excel_file.sheet_names),
                "sheet_names": excel_file.sheet_names
            },
            "content": {
                "sheets": sheets_data
            }
        }
    except Exception as e:
        return {**base_metadata, "error": str(e), "content": None}

def _process_xml(file_path, base_metadata):
    """Processa XML extraindo estrutura hierárquica completa"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        def xml_to_dict(element):
            """Converte elemento XML para dicionário recursivamente"""
            result = {}
            
            # Atributos
            if element.attrib:
                result['@attributes'] = element.attrib
            
            # Texto do elemento
            if element.text and element.text.strip():
                if len(element) == 0:  # Elemento folha
                    return element.text.strip()
                result['#text'] = element.text.strip()
            
            # Elementos filhos
            children = {}
            for child in element:
                child_data = xml_to_dict(child)
                if child.tag in children:
                    # Múltiplos elementos com mesmo nome -> lista
                    if not isinstance(children[child.tag], list):
                        children[child.tag] = [children[child.tag]]
                    children[child.tag].append(child_data)
                else:
                    children[child.tag] = child_data
            
            result.update(children)
            return result
        
        # Estatísticas do XML
        def count_elements(element):
            count = 1
            for child in element:
                count += count_elements(child)
            return count
        
        xml_data = xml_to_dict(root)
        
        return {
            **base_metadata,
            "xml_info": {
                "root_tag": root.tag,
                "total_elements": count_elements(root),
                "namespace": root.tag.split('}')[0][1:] if '}' in root.tag else None,
                "root_attributes": root.attrib
            },
            "content": {
                "structure": xml_data,
                "raw_elements": [{"tag": elem.tag, "attrib": elem.attrib, "text": elem.text} 
                               for elem in root.iter()]
            }
        }
    except Exception as e:
        return {**base_metadata, "error": str(e), "content": None}

def _extract_common_patterns(text):
    """Extrai padrões comuns como emails, telefones, datas, CPF, CNPJ"""
    patterns = {
        "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
        "phones": re.findall(r'(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\s?)?\d{4}[-\s]?\d{4}', text),
        "dates": re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text),
        "cpf": re.findall(r'\b\d{3}\.?\d{3}\.?\d{3}[-.]?\d{2}\b', text),
        "cnpj": re.findall(r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}[-.]?\d{2}\b', text),
        "money": re.findall(r'R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?', text),
        "urls": re.findall(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*)?(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?', text)
    }
    
    # Remove padrões vazios
    return {k: v for k, v in patterns.items() if v}

