import logging
import os
from datetime import datetime
from pathlib import Path
import json

class LoggingService:
    """Serviço centralizado de logging para a aplicação"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Configura os loggers da aplicação"""
        
        # Logger principal da aplicação
        self.app_logger = logging.getLogger('agente_extracao')
        self.app_logger.setLevel(logging.INFO)
        
        # Logger para processamento de arquivos
        self.file_logger = logging.getLogger('file_processing')
        self.file_logger.setLevel(logging.DEBUG)
        
        # Logger para operações de banco de dados
        self.db_logger = logging.getLogger('database')
        self.db_logger.setLevel(logging.INFO)
        
        # Logger para queries AI
        self.ai_logger = logging.getLogger('ai_queries')
        self.ai_logger.setLevel(logging.INFO)
        
        # Configuração de handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura os handlers de logging"""
        
        # Formatter padrão
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para arquivo geral
        general_handler = logging.FileHandler(
            self.log_dir / 'application.log',
            encoding='utf-8'
        )
        general_handler.setFormatter(formatter)
        self.app_logger.addHandler(general_handler)
        
        # Handler para processamento de arquivos
        file_handler = logging.FileHandler(
            self.log_dir / 'file_processing.log',
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        self.file_logger.addHandler(file_handler)
        
        # Handler para banco de dados
        db_handler = logging.FileHandler(
            self.log_dir / 'database.log',
            encoding='utf-8'
        )
        db_handler.setFormatter(formatter)
        self.db_logger.addHandler(db_handler)
        
        # Handler para AI queries
        ai_handler = logging.FileHandler(
            self.log_dir / 'ai_queries.log',
            encoding='utf-8'
        )
        ai_handler.setFormatter(formatter)
        self.ai_logger.addHandler(ai_handler)
        
        # Console handler para desenvolvimento
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.app_logger.addHandler(console_handler)
    
    def log_file_upload(self, filename, file_type, file_size):
        """Log de upload de arquivo"""
        self.file_logger.info(
            f"Arquivo enviado: {filename} | Tipo: {file_type} | Tamanho: {file_size} bytes"
        )
    
    def log_file_processing_start(self, filename, file_type):
        """Log de início de processamento"""
        self.file_logger.info(f"Iniciando processamento: {filename} ({file_type})")
    
    def log_file_processing_success(self, filename, records_count, processing_time):
        """Log de sucesso no processamento"""
        self.file_logger.info(
            f"Processamento concluído: {filename} | "
            f"Registros: {records_count} | "
            f"Tempo: {processing_time:.2f}s"
        )
    
    def log_file_processing_error(self, filename, error_message):
        """Log de erro no processamento"""
        self.file_logger.error(f"Erro no processamento: {filename} | Erro: {error_message}")
    
    def log_zip_extraction(self, zip_filename, extracted_files):
        """Log de extração de ZIP"""
        self.file_logger.info(
            f"ZIP extraído: {zip_filename} | "
            f"Arquivos: {len(extracted_files)} | "
            f"Lista: {', '.join(extracted_files)}"
        )
    
    def log_batch_processing_start(self, total_files):
        """Log de início de processamento em lote"""
        self.file_logger.info(f"Iniciando processamento em lote: {total_files} arquivos")
    
    def log_batch_processing_summary(self, total_files, successful, failed, total_time):
        """Log de resumo do processamento em lote"""
        self.file_logger.info(
            f"Processamento em lote concluído: "
            f"Total: {total_files} | "
            f"Sucessos: {successful} | "
            f"Falhas: {failed} | "
            f"Tempo total: {total_time:.2f}s"
        )
    
    def log_database_operation(self, operation, table, records_count=None):
        """Log de operação de banco de dados"""
        message = f"DB {operation}: {table}"
        if records_count is not None:
            message += f" | Registros: {records_count}"
        self.db_logger.info(message)
    
    def log_ai_query(self, query, response_time, success=True):
        """Log de query AI"""
        status = "SUCCESS" if success else "ERROR"
        self.ai_logger.info(
            f"AI Query {status}: '{query[:50]}...' | Tempo: {response_time:.2f}s"
        )
    
    def log_application_start(self):
        """Log de início da aplicação"""
        self.app_logger.info("=== APLICAÇÃO INICIADA ===")
    
    def log_application_error(self, error_message, exception=None):
        """Log de erro da aplicação"""
        self.app_logger.error(f"ERRO DA APLICAÇÃO: {error_message}")
        if exception:
            self.app_logger.exception(exception)
    
    def get_processing_stats(self):
        """Retorna estatísticas de processamento dos logs"""
        try:
            log_file = self.log_dir / 'file_processing.log'
            if not log_file.exists():
                return {"error": "Log file not found"}
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            stats = {
                "total_operations": 0,
                "successful": 0,
                "failed": 0,
                "zip_extractions": 0,
                "batch_operations": 0
            }
            
            for line in lines:
                if "Processamento concluído" in line:
                    stats["successful"] += 1
                    stats["total_operations"] += 1
                elif "Erro no processamento" in line:
                    stats["failed"] += 1
                    stats["total_operations"] += 1
                elif "ZIP extraído" in line:
                    stats["zip_extractions"] += 1
                elif "processamento em lote" in line:
                    stats["batch_operations"] += 1
            
            return stats
        except Exception as e:
            return {"error": str(e)}

# Instância global do serviço de logging
logging_service = LoggingService()
