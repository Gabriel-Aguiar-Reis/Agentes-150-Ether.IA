from agents.reader_agent import read_file
from agents.formatter_agent import format_data
from agents.db_agent import insert_into_db

def process_file(file_path, file_type):
    raw_data = read_file(file_path, file_type)
    formatted_data = format_data(raw_data, file_type)
    insert_into_db(formatted_data)
    return "Processamento concluído com sucesso!"

