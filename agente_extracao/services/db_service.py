import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

DB_PATH = "data/banco.db"

def init_db():
    """Inicializa o banco e realiza migrações de schema se necessário."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Criação inicial (schema mínimo)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS dados (
            id INTEGER PRIMARY KEY,
            conteudo TEXT,
            analise_campos TEXT
        )
        """
    )

    # Verifica colunas existentes
    cursor.execute("PRAGMA table_info(dados)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    # Migrações incrementais: adiciona colunas se não existirem
    migrations = [
        ("file_name", "ALTER TABLE dados ADD COLUMN file_name TEXT"),
        ("file_hash", "ALTER TABLE dados ADD COLUMN file_hash TEXT"),
        ("file_type", "ALTER TABLE dados ADD COLUMN file_type TEXT"),
        ("metadata", "ALTER TABLE dados ADD COLUMN metadata TEXT"),
        ("processed_at", "ALTER TABLE dados ADD COLUMN processed_at TEXT"),
    ]
    for col, stmt in migrations:
        if col not in existing_cols:
            cursor.execute(stmt)

    conn.commit()
    conn.close()

def inserir_dado(
    conteudo: Any,
    analise_campos: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Insere um registro no banco incluindo metadata e campos de identificação.

    Parameters
    ----------
    conteudo : Any
        Conteúdo principal (lista de registros ou outro objeto) será serializado em JSON.
    analise_campos : dict | None
        Análise estatística gerada pelo formatter.
    metadata : dict | None
        Metadados do arquivo (file_name, file_hash, file_type, processed_at, etc.).
    """
    file_name = None
    file_hash = None
    file_type = None
    processed_at = None
    if metadata and isinstance(metadata, dict):
        file_name = metadata.get("file_name")
        file_hash = metadata.get("file_hash")
        file_type = metadata.get("file_type")
        processed_at = metadata.get("processed_at")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO dados (conteudo, analise_campos, file_name, file_hash, file_type, metadata, processed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            json.dumps(conteudo, ensure_ascii=False),
            json.dumps(analise_campos, ensure_ascii=False) if analise_campos else None,
            file_name,
            file_hash,
            file_type,
            json.dumps(metadata, ensure_ascii=False) if metadata else None,
            processed_at,
        ),
    )
    conn.commit()
    conn.close()

def ler_dados() -> List[Dict[str, Any]]:
    """Lê todos os dados do banco, retornando como objetos Python."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, conteudo, analise_campos, file_name, file_hash, file_type, metadata, processed_at FROM dados"
    )
    rows = cursor.fetchall()
    conn.close()
    result = []
    for (
        id_,
        conteudo,
        analise,
        file_name,
        file_hash,
        file_type,
        metadata,
        processed_at,
    ) in rows:
        parsed_conteudo = json.loads(conteudo) if conteudo else None
        result.append(
            {
                "id": id_,
                "conteudo": parsed_conteudo,
                "analise_campos": json.loads(analise) if analise else None,
                "file_name": file_name,
                "file_hash": file_hash,
                "file_type": file_type,
                "metadata": json.loads(metadata) if metadata else None,
                "processed_at": processed_at,
                "record_count": len(parsed_conteudo)
                if isinstance(parsed_conteudo, list)
                else (1 if parsed_conteudo else 0),
            }
        )
    return result

def listar_arquivos() -> List[Dict[str, Any]]:
    """Lista arquivos processados com contagem de registros."""
    dados = ler_dados()
    arquivos = []
    for d in dados:
        arquivos.append(
            {
                "id": d["id"],
                "file_name": d.get("file_name") or (d.get("metadata", {}) or {}).get("file_name"),
                "file_hash": d.get("file_hash") or (d.get("metadata", {}) or {}).get("file_hash"),
                "file_type": d.get("file_type") or (d.get("metadata", {}) or {}).get("file_type"),
                "processed_at": d.get("processed_at") or (d.get("metadata", {}) or {}).get("processed_at"),
                "record_count": d.get("record_count", 0),
            }
        )
    # Ordena por processed_at desc se disponível
    arquivos.sort(key=lambda x: x.get("processed_at") or "", reverse=True)
    return arquivos

def deletar_arquivo_por_id(registro_id: int) -> bool:
    """Remove um registro (arquivo) do banco pelo id. Retorna True se removeu."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dados WHERE id = ?", (registro_id,))
    changes = cursor.rowcount
    conn.commit()
    conn.close()
    return changes > 0

def deletar_por_hash(file_hash: str) -> int:
    """Remove todos registros associados a um file_hash. Retorna quantidade removida."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dados WHERE file_hash = ?", (file_hash,))
    changes = cursor.rowcount
    conn.commit()
    conn.close()
    return changes

def obter_registro(registro_id: int) -> Optional[Dict[str, Any]]:
    """Obtém um registro completo (incluindo conteudo e analise_campos) pelo id."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, conteudo, analise_campos, file_name, file_hash, file_type, metadata, processed_at
        FROM dados WHERE id = ?
        """,
        (registro_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    (
        id_,
        conteudo,
        analise,
        file_name,
        file_hash,
        file_type,
        metadata,
        processed_at,
    ) = row
    parsed_conteudo = json.loads(conteudo) if conteudo else None
    return {
        "id": id_,
        "conteudo": parsed_conteudo,
        "analise_campos": json.loads(analise) if analise else None,
        "file_name": file_name,
        "file_hash": file_hash,
        "file_type": file_type,
        "metadata": json.loads(metadata) if metadata else None,
        "processed_at": processed_at,
        "record_count": len(parsed_conteudo)
        if isinstance(parsed_conteudo, list)
        else (1 if parsed_conteudo else 0),
    }

