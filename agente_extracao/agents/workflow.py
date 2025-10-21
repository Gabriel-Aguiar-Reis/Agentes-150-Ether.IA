"""Workflow de processamento de arquivos para leitura, formatação e inserção no banco de dados."""

import os
import time
from typing import List, Dict
from agents.reader_agent import read_file
from agents.formatter_agent import format_data
from agents.db_agent import insert_into_db
from services.logging_service import logging_service
from services.file_service import (
    extract_zip_file,
    create_temp_directory,
    cleanup_temp_directory,
    get_supported_files_from_directory,
)


def process_file(file_path, file_type):
    """Processa um único arquivo"""
    start_time = time.time()

    try:
        # Log do início do processamento
        logging_service.log_file_processing_start(
            os.path.basename(file_path), file_type
        )

        # Processamento do arquivo
        raw_data = read_file(file_path, file_type)
        formatter_output = format_data(raw_data, file_type)

        # Inserção no banco de dados com metadata do raw_data
        metadata = raw_data.get("metadata") if isinstance(raw_data, dict) else None
        records_count = insert_into_db(formatter_output, raw_metadata=metadata)

        # Log do sucesso
        processing_time = time.time() - start_time
        logging_service.log_file_processing_success(
            os.path.basename(file_path), records_count, processing_time
        )

        return {
            "status": "success",
            "file": os.path.basename(file_path),
            "records": records_count,
            "processing_time": processing_time,
        }

    except (IOError, ValueError) as e:
        # Log do erro
        logging_service.log_file_processing_error(os.path.basename(file_path), str(e))
        return {"status": "error", "file": os.path.basename(file_path), "error": str(e)}


def process_multiple_files(file_list: List[Dict]) -> Dict:
    """Processa múltiplos arquivos em lote"""
    start_time = time.time()
    results = []
    successful = 0
    failed = 0

    # Log do início do processamento em lote
    logging_service.log_batch_processing_start(len(file_list))

    for file_info in file_list:
        file_path = file_info["path"]
        file_type = file_info["type"]

        result = process_file(file_path, file_type)
        results.append(result)

        if result["status"] == "success":
            successful += 1
        else:
            failed += 1

    # Log do resumo do processamento em lote
    total_time = time.time() - start_time
    logging_service.log_batch_processing_summary(
        len(file_list), successful, failed, total_time
    )

    return {
        "total_files": len(file_list),
        "successful": successful,
        "failed": failed,
        "total_time": total_time,
        "results": results,
    }


def process_zip_file(zip_path: str) -> Dict:
    """Processa um arquivo ZIP extraindo e processando todos os arquivos suportados"""
    temp_dir = None

    try:
        # Cria diretório temporário
        temp_dir = create_temp_directory()

        # Extrai arquivos do ZIP
        extracted_files = extract_zip_file(zip_path, temp_dir)

        if not extracted_files:
            return {
                "status": "warning",
                "message": "Nenhum arquivo suportado encontrado no ZIP",
                "extracted_files": 0,
            }

        # Obtém lista de arquivos suportados
        supported_files = get_supported_files_from_directory(temp_dir)

        # Processa todos os arquivos
        batch_result = process_multiple_files(supported_files)

        return {
            "status": "success",
            "zip_file": os.path.basename(zip_path),
            "extracted_files": len(extracted_files),
            "processed_files": batch_result["total_files"],
            "successful": batch_result["successful"],
            "failed": batch_result["failed"],
            "total_time": batch_result["total_time"],
        }

    except (IOError, ValueError) as e:
        logging_service.log_file_processing_error(
            os.path.basename(zip_path), f"Erro ao processar ZIP: {str(e)}"
        )
        return {
            "status": "error",
            "zip_file": os.path.basename(zip_path),
            "error": str(e),
        }

    finally:
        # Limpa diretório temporário
        if temp_dir:
            cleanup_temp_directory(temp_dir)
