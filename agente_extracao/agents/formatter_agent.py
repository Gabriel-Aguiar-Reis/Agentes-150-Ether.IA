import pandas as pd
from typing import Any, Dict

def _gerar_analise_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {"tipos": {}, "describe": {}, "shape": df.shape}
    return {
        "tipos": df.dtypes.apply(lambda x: str(x)).to_dict(),
        "describe": df.describe(include='all').to_dict(),
        "shape": df.shape
    }

def format_data(raw_data, file_type):
    """
    Padroniza os dados e, se possível, gera análise dos campos (tipos, estatísticas, shape).
    - Para CSV/Excel: já vem como lista de registros em raw_data['content']['records'] ou sheets.
    - Para XML: usa raw_elements ou structure para gerar DataFrame tabular básico.
    - Para PDF: retorna texto completo, sem análise de campos tabular.
    Retorna dict: { dados: [...], analise_campos: {...}|None }
    """
    content = raw_data.get("content")

    # Caso de CSV: content.records
    if file_type in ("csv", "xls", "xlsx"):
        # Excel pode ter múltiplas sheets
        if file_type in ("xls", "xlsx") and isinstance(content, dict) and "sheets" in content:
            # Concatena todas as sheets adicionando coluna sheet_name
            frames = []
            for sheet_name, sheet_payload in content["sheets"].items():
                records = sheet_payload.get("records", [])
                if records:
                    df_sheet = pd.DataFrame(records)
                    df_sheet["__sheet__"] = sheet_name
                    frames.append(df_sheet)
            df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
            analise = _gerar_analise_dataframe(df)
            return {"dados": df.to_dict(orient="records"), "analise_campos": analise}
        else:
            # CSV simples
            if isinstance(content, dict) and "records" in content:
                records = content.get("records", [])
                df = pd.DataFrame(records)
                analise = _gerar_analise_dataframe(df)
                return {"dados": records, "analise_campos": analise}

    # Caso de XML
    if file_type == "xml":
        # Tenta usar raw_elements se existir (lista de dict-like)
        raw_elements = None
        if isinstance(content, dict):
            raw_elements = content.get("raw_elements") or content.get("structure")
        if isinstance(raw_elements, list) and raw_elements and isinstance(raw_elements[0], dict):
            df = pd.DataFrame(raw_elements)
            analise = _gerar_analise_dataframe(df)
            return {"dados": df.to_dict(orient="records"), "analise_campos": analise}
        # fallback: serializa tudo
        return {"dados": [{"texto": str(content)}], "analise_campos": None}

    # Caso de PDF: estrutura definida em reader_agent: content.full_text/pages
    if file_type == "pdf":
        if isinstance(content, dict):
            full_text = content.get("full_text") or content.get("texto") or ""
            return {"dados": [{"texto": full_text}], "analise_campos": None}
        return {"dados": [{"texto": str(content)}], "analise_campos": None}

    # Fallback genérico pré-existente
    if isinstance(content, list) and content and isinstance(content[0], dict):
        df = pd.DataFrame(content)
        analise = _gerar_analise_dataframe(df)
        return {"dados": content, "analise_campos": analise}

    return {"dados": [{"texto": content}], "analise_campos": None}

