import os
import shutil
import zipfile
import tempfile
import mimetypes
from services.logging_service import logging_service
from pypdf import PdfReader

def save_uploaded_file(uploaded_file, save_dir):
    """Salva arquivo enviado pelo usuário"""
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)
    
    # Log do upload
    logging_service.log_file_upload(
        uploaded_file.name, 
        detect_file_type(file_path), 
        uploaded_file.size
    )
    
    return file_path

def detect_file_type(file_path):
    """Detecta o tipo de arquivo baseado na extensão (método simples)"""
    ext = file_path.split(".")[-1].lower()
    if ext in ["pdf", "xml", "csv", "xls", "xlsx", "zip"]:
        return ext
    return None

def detectar_tipo_arquivo(file_path):
    """Detecta o tipo de arquivo usando mimetypes e análise de conteúdo"""
    tipo, _ = mimetypes.guess_type(file_path)
    
    if tipo == "text/csv":
        return "CSV"
    elif tipo == "application/xml" or file_path.lower().endswith(".xml"):
        return "XML"
    elif tipo == "application/pdf":
        # Detecta se é PDF texto ou imagem
        try:
            reader = PdfReader(file_path)
            if any(page.extract_text() for page in reader.pages):
                return "PDF_TEXTO"
            else:
                return "PDF_IMAGEM"
        except Exception:
            return "PDF_IMAGEM"
    elif tipo == "application/vnd.ms-excel" or tipo == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return "EXCEL"
    elif file_path.lower().endswith(".zip"):
        return "ZIP"
    else:
        return "DESCONHECIDO"

def get_supported_file_type(file_path):
    """Retorna o tipo de arquivo suportado ou None se não suportado"""
    detected_type = detectar_tipo_arquivo(file_path)
    
    # Mapeia tipos detectados para tipos suportados
    type_mapping = {
        "CSV": "csv",
        "XML": "xml", 
        "PDF_TEXTO": "pdf",
        "PDF_IMAGEM": "pdf",  # Ainda suportamos, mas com limitações
        "EXCEL": "xlsx",  # Assumimos xlsx por padrão
        "ZIP": "zip"
    }
    
    return type_mapping.get(detected_type, None)

def extract_zip_file(zip_path, extract_dir):
    """Extrai arquivos de um ZIP e retorna lista de arquivos extraídos"""
    extracted_files = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Lista todos os arquivos no ZIP
            file_list = zip_ref.namelist()
            
            # Filtra apenas arquivos (não diretórios)
            files_only = [f for f in file_list if not f.endswith('/')]
            
            # Extrai cada arquivo
            for file_name in files_only:
                # Verifica se é um tipo de arquivo suportado
                file_ext = file_name.split('.')[-1].lower()
                if file_ext in ["pdf", "xml", "csv", "xls", "xlsx"]:
                    # Extrai o arquivo
                    zip_ref.extract(file_name, extract_dir)
                    extracted_path = os.path.join(extract_dir, file_name)
                    extracted_files.append(extracted_path)
        
        # Log da extração
        logging_service.log_zip_extraction(
            os.path.basename(zip_path), 
            [os.path.basename(f) for f in extracted_files]
        )
        
        return extracted_files
        
    except zipfile.BadZipFile:
        logging_service.log_file_processing_error(
            os.path.basename(zip_path), 
            "Arquivo ZIP inválido ou corrompido"
        )
        raise ValueError("Arquivo ZIP inválido ou corrompido")
    except Exception as e:
        logging_service.log_file_processing_error(
            os.path.basename(zip_path), 
            f"Erro ao extrair ZIP: {str(e)}"
        )
        raise

def get_supported_files_from_directory(directory_path):
    """Retorna lista de arquivos suportados em um diretório"""
    supported_files = []
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_type = detect_file_type(file_path)
            if file_type:
                supported_files.append({
                    'path': file_path,
                    'name': file,
                    'type': file_type,
                    'size': os.path.getsize(file_path)
                })
    
    return supported_files

def create_temp_directory():
    """Cria um diretório temporário para extração de arquivos"""
    temp_dir = tempfile.mkdtemp(prefix="agente_extracao_")
    return temp_dir

def cleanup_temp_directory(temp_dir):
    """Remove diretório temporário e seus conteúdos"""
    try:
        shutil.rmtree(temp_dir)
        logging_service.file_logger.info(f"Diretório temporário removido: {temp_dir}")
    except Exception as e:
        logging_service.log_file_processing_error(
            "cleanup", 
            f"Erro ao remover diretório temporário: {str(e)}"
        )

