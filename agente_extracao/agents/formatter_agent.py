def format_data(raw_data, file_type):
    # Aqui você padroniza os dados
    if isinstance(raw_data["content"], list):
        return raw_data["content"]
    else:
        # Caso seja texto PDF ou XML cru
        return [{"texto": raw_data["content"]}]

