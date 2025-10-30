from services.logging_service import logging_service
from services.db_service import inserir_dado

def insert_into_db(formatter_output, raw_metadata=None):
    """Insere dados, análise de campos e metadata de arquivo no banco.

    Parameters
    ----------
    formatter_output : dict
        Deve conter chaves 'dados' (lista ou objeto) e 'analise_campos'.
    raw_metadata : dict | None
        Metadados completos do arquivo vindos do reader_agent (raw_data['metadata']).
    """
    dados = formatter_output.get("dados", [])
    analise_campos = formatter_output.get("analise_campos")

    # Normaliza metadata mínima
    metadata = None
    if isinstance(raw_metadata, dict):
        metadata = {
            "file_name": raw_metadata.get("file_name"),
            "file_hash": raw_metadata.get("file_hash"),
            "file_type": raw_metadata.get("file_type"),
            "processed_at": raw_metadata.get("processed_at"),
            # Guarda original completo também
            "original": raw_metadata,
        }

    inserir_dado(dados, analise_campos, metadata)
    records_count = len(dados) if isinstance(dados, list) else 1
    logging_service.log_database_operation("INSERT", "dados", records_count)
    return records_count

