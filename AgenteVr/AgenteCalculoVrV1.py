import os
import sqlite3
import pandas as pd
from langchain_groq import ChatGroq
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from datetime import datetime
from io import StringIO

# Set Groq API key
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Initialize Groq LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Updated file paths
BASE_DIR = r"C:\DesenvolvimentoEstudos\Python\AgenteI2A2Groq\data\documentosDesafio4"
FILE_PATHS = {
    "admissao_abril": os.path.join(BASE_DIR, "ADMISSÃO ABRIL.xlsx"),
    "afastamentos": os.path.join(BASE_DIR, "AFASTAMENTOS.xlsx"),
    "aprendiz": os.path.join(BASE_DIR, "APRENDIZ.xlsx"),
    "ativos": os.path.join(BASE_DIR, "ATIVOS.xlsx"),
    "dias_uteis": os.path.join(BASE_DIR, "Base dias uteis.xlsx"),
    "sindicato_valor": os.path.join(BASE_DIR, "Base sindicato x valor.xlsx"),
    "desligados": os.path.join(BASE_DIR, "DESLIGADOS.xlsx"),
    "estagio": os.path.join(BASE_DIR, "ESTÁGIO.xlsx"),
    "exterior": os.path.join(BASE_DIR, "EXTERIOR.xlsx"),
    "ferias": os.path.join(BASE_DIR, "FÉRIAS.xlsx")
}

# Tools
@tool
def save_to_sqlite(data_json: str, table_name: str) -> str:
    """Save JSON data to SQLite database."""
    try:
        # Debug: Print first 200 chars of data_json
        print(f"DEBUG save_to_sqlite - data_json preview: {data_json[:200]}...")
        
        if not data_json or data_json == "[]":
            return f"No data to save to table {table_name}"
            
        df = pd.read_json(StringIO(data_json))
        if df.empty:
            return f"Empty dataframe, no data saved to table {table_name}"
            
        conn = sqlite3.connect('vr_automation.db')
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        return f"Successfully saved {len(df)} records to table {table_name}"
    except Exception as e:
        return f"Error saving to SQLite: {str(e)}"

@tool
def query_sqlite(query: str) -> str:
    """Execute SQL query on SQLite database, return JSON."""
    try:
        conn = sqlite3.connect('vr_automation.db')
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return "[]"
        
        result = df.to_json(orient='records')
        print(f"DEBUG query_sqlite - returning {len(df)} records")
        return result
    except Exception as e:
        return f"Error querying SQLite: {str(e)}"

@tool
def generate_excel_output(data_json: str, file_path: str) -> str:
    """Generate Excel file from JSON data."""
    try:
        print(f"DEBUG generate_excel - data_json preview: {data_json[:200]}...")
        
        if not data_json or data_json == "[]":
            return f"No data to generate Excel file at {file_path}"
            
        df = pd.read_json(StringIO(data_json))
        if df.empty:
            return f"Empty dataframe, no Excel file generated at {file_path}"
            
        # Calculate empresa and profissional values
        if 'valor_total_vr' in df.columns:
            df['valor_empresa'] = df['valor_total_vr'] * 0.8
            df['valor_profissional'] = df['valor_total_vr'] * 0.2
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        df.to_excel(file_path, index=False)
        return f"Successfully generated Excel with {len(df)} records at {file_path}"
    except Exception as e:
        return f"Error generating Excel: {str(e)}"

@tool
def validate_data(data_json: str) -> str:
    """Validate the consolidated data and provide summary statistics."""
    try:
        if not data_json or data_json == "[]":
            return "No data to validate"
            
        df = pd.read_json(StringIO(data_json))
        if df.empty:
            return "Empty dataframe to validate"
        
        # Validation checks
        total_records = len(df)
        duplicates = df.duplicated(subset=['matricula']).sum() if 'matricula' in df.columns else 0
        total_vr_value = df['valor_total_vr'].sum() if 'valor_total_vr' in df.columns else 0
        
        validation_report = f"""
VALIDATION REPORT:
- Total records: {total_records}
- Duplicate matriculas: {duplicates}
- Total VR value: R$ {total_vr_value:,.2f}
- Columns present: {list(df.columns)}
        """
        
        if duplicates > 0:
            validation_report += f"\nWARNING: Found {duplicates} duplicate records!"
            
        return validation_report
    except Exception as e:
        return f"Error validating data: {str(e)}"

# Local data consolidation and calculation
def consolidate_data():
    """Consolidate and calculate VR data locally using Pandas."""
    try:
        print("Starting data consolidation...")
        dataframes = {}
        
        # Load all files
        for key, path in FILE_PATHS.items():
            try:
                if not os.path.exists(path):
                    print(f"Warning: {key} file not found at {path}, skipping.")
                    dataframes[key] = pd.DataFrame()
                    continue
                    
                df = pd.read_excel(path)
                
                # Handle files with headers in second row
                if df.columns.str.contains('Unnamed').any():
                    df = pd.read_excel(path, skiprows=1)
                
                # Clean column names
                df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
                dataframes[key] = df
                print(f"Loaded {key}: {len(df)} records")
                
            except Exception as e:
                print(f"Error loading {key}: {str(e)}")
                dataframes[key] = pd.DataFrame()

        # Check if we have the base ATIVOS data
        if dataframes["ativos"].empty:
            return '[]'

        # Normalize column names
        column_mappings = {
            "matricula": ["matricula", "id_funcionario", "employee_id"],
            "nome": ["nome", "name"],
            "cargo": ["titulo_do_cargo", "cargo", "position"],
            "sindicato": ["sindicato", "sindicado", "union"],
            "data_admissao": ["data_admissao", "admission_date"],
            "data_desligamento": ["data_demissao", "data_desligamento", "termination_date"],
            "ferias_inicio": ["ferias_inicio", "inicio_ferias", "vacation_start"],
            "ferias_fim": ["ferias_fim", "fim_ferias", "vacation_end"],
            "afastamento_type": ["desc_situacao", "afastamento", "absence_type"],
            "pais": ["pais", "country"],
            "valor_diario_vr": ["valor_diario_vr", "daily_vr_value"],
            "dias_uteis": ["dias_uteis", "working_days"]
        }

        # Apply column mappings
        for key, df in dataframes.items():
            for standard, variants in column_mappings.items():
                for variant in variants:
                    if variant in df.columns:
                        df.rename(columns={variant: standard}, inplace=True)
                        break
            dataframes[key] = df

        # Start with ATIVOS as base
        consolidated = dataframes["ativos"].copy()
        print(f"Base ATIVOS: {len(consolidated)} records")

        # Merge additional data
        merge_keys = ["admissao_abril", "afastamentos", "desligados", "estagio", "exterior", "ferias"]
        for key in merge_keys:
            if not dataframes[key].empty and 'matricula' in dataframes[key].columns:
                before_count = len(consolidated)
                consolidated = consolidated.merge(dataframes[key], on="matricula", how="left", suffixes=("", f"_{key}"))
                print(f"After merging {key}: {len(consolidated)} records")

        # Merge dias_uteis by sindicato
        if not dataframes["dias_uteis"].empty and 'sindicato' in dataframes["dias_uteis"].columns:
            consolidated = consolidated.merge(dataframes["dias_uteis"], on="sindicato", how="left", suffixes=("", "_du"))

        # Merge sindicato_valor for VR values
        if not dataframes["sindicato_valor"].empty and 'sindicato' in dataframes["sindicato_valor"].columns:
            consolidated = consolidated.merge(dataframes["sindicato_valor"], on="sindicato", how="left", suffixes=("", "_sv"))

        print(f"After all merges: {len(consolidated)} records")

        # Apply exclusions
        initial_count = len(consolidated)
        
        # Exclude directors, interns, apprentices
        if 'cargo' in consolidated.columns:
            consolidated = consolidated[
                ~consolidated["cargo"].str.contains("diretor|estagiario|aprendiz", case=False, na=False)
            ]
        
        # Exclude specific absence types
        if 'afastamento_type' in consolidated.columns:
            consolidated = consolidated[
                (consolidated["afastamento_type"].isna()) | 
                (~consolidated["afastamento_type"].isin(["Atestado", "Licença Maternidade"]))
            ]
        
        # Include only Brazil (or null country)
        if 'pais' in consolidated.columns:
            consolidated = consolidated[
                (consolidated["pais"].isna()) | (consolidated["pais"] == "Brasil")
            ]

        print(f"After exclusions: {len(consolidated)} records (excluded {initial_count - len(consolidated)})")

        # Handle dates and dismissal logic
        if 'data_desligamento' in consolidated.columns:
            consolidated["data_desligamento"] = pd.to_datetime(consolidated["data_desligamento"], errors="coerce")
            
            current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = current_month.replace(day=15)
            
            # Apply dismissal rule
            consolidated["eligible"] = consolidated.apply(
                lambda row: pd.isna(row["data_desligamento"]) or 
                           (row["data_desligamento"] > cutoff_date and 
                            row.get("comunicado_de_desligamento") != "OK"), 
                axis=1
            )
            
            consolidated = consolidated[consolidated["eligible"]].copy()
            print(f"After dismissal rules: {len(consolidated)} records")

        # Calculate working days
        if "dias_uteis" in consolidated.columns:
            consolidated["dias_uteis"] = consolidated["dias_uteis"].fillna(21)
        else:
            consolidated["dias_uteis"] = 21
        
        # Handle vacation days
        if "ferias_inicio" in consolidated.columns and "ferias_fim" in consolidated.columns:
            consolidated["ferias_inicio"] = pd.to_datetime(consolidated["ferias_inicio"], errors="coerce")
            consolidated["ferias_fim"] = pd.to_datetime(consolidated["ferias_fim"], errors="coerce")
            
            consolidated["vacation_days"] = consolidated.apply(
                lambda row: (row["ferias_fim"] - row["ferias_inicio"]).days 
                           if pd.notna(row["ferias_inicio"]) and pd.notna(row["ferias_fim"])
                           else 0, axis=1
            )
            
            consolidated["working_days"] = (consolidated["dias_uteis"] - consolidated["vacation_days"]).clip(lower=0)
        else:
            consolidated["working_days"] = consolidated["dias_uteis"]

        # Calculate VR values
        if "valor_diario_vr" in consolidated.columns:
            consolidated["valor_diario_vr"] = consolidated["valor_diario_vr"].fillna(50.0)
        else:
            consolidated["valor_diario_vr"] = 50.0
            
        consolidated["valor_total_vr"] = consolidated["working_days"] * consolidated["valor_diario_vr"]

        print(f"Final consolidated data: {len(consolidated)} records")
        
        # Clean up columns for output
        essential_columns = ["matricula", "nome", "cargo", "sindicato", "working_days", "valor_diario_vr", "valor_total_vr"]
        
        # Keep only columns that exist
        output_columns = [col for col in essential_columns if col in consolidated.columns]
        consolidated = consolidated[output_columns]

        result_json = consolidated.to_json(orient="records")
        print(f"Returning JSON with {len(consolidated)} records")
        
        return result_json

    except Exception as e:
        print(f"Error consolidating data: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return "[]"

@tool
def consolidated_data() -> str:
    """Return pre-consolidated and calculated VR data."""
    return consolidate_data()

# Define tools
tools = [consolidated_data, save_to_sqlite, query_sqlite, generate_excel_output, validate_data]

# Simple system prompt that works better with the agent
system_prompt = """
You are an agent to automate VR (meal voucher) purchase calculations.

Your task is to:
1. First, call consolidated_data() to get processed data
2. Then call validate_data with the data from step 1  
3. Finally, call generate_excel_output with the data to create 'vr_mensal.xlsx'

Be sure to use the actual JSON data returned by each tool, not placeholder text.
Report the results of each step.
"""

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=system_prompt),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Initialize agent
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=10)

# Alternative: Direct execution without agent (for debugging)
def direct_execution():
    """Execute the process directly without the agent for debugging."""
    print("=== DIRECT EXECUTION MODE ===")
    
    # Step 1: Get consolidated data
    print("Step 1: Consolidating data...")
    data_json = consolidate_data()
    
    if data_json == "[]":
        print("No data returned from consolidation")
        return
    
    # Step 2: Save to SQLite
    print("Step 2: Saving to SQLite...")
    save_result = save_to_sqlite.invoke({"data_json": data_json, "table_name": "consolidated"})
    print(save_result)
    
    # Step 3: Query back from SQLite
    print("Step 3: Querying from SQLite...")
    query_result = query_sqlite.invoke({"query": "SELECT * FROM consolidated"})
    print(f"Query returned: {query_result[:200]}..." if len(query_result) > 200 else query_result)
    
    # Step 4: Validate
    print("Step 4: Validating data...")
    validation_result = validate_data.invoke({"data_json": query_result})
    print(validation_result)
    
    # Step 5: Generate Excel
    print("Step 5: Generating Excel...")
    excel_result = generate_excel_output.invoke({
        "data_json": query_result, 
        "file_path": "vr_mensal.xlsx"
    })
    print(excel_result)

# Run the automation
if __name__ == "__main__":
    print("Choose execution mode:")
    print("1. Agent mode (with LLM)")
    print("2. Direct mode (for debugging)")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "2":
            direct_execution()
        else:
            # Agent mode
            response = agent_executor.invoke({"input": "Automate VR purchase for current month."})
            print("=== FINAL RESPONSE ===")
            print(response['output'])
            
    except Exception as e:
        if "rate_limit_exceeded" in str(e):
            print("Token limit exceeded. Running direct execution instead...")
            direct_execution()
        elif "model_decommissioned" in str(e):
            print("Error: The specified model is decommissioned. Running direct execution instead...")
            direct_execution()
        else:
            print(f"Error: {str(e)}")
            print("Running direct execution instead...")
            direct_execution()