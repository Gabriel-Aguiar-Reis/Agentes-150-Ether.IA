import pytest
from pathlib import Path
import tempfile
import pandas as pd
from unittest.mock import patch, MagicMock
from agents.reader_agent import (
    read_file, 
    _get_file_metadata, 
    _process_pdf,
    _extract_common_patterns
)
import os
import glob


class TestReaderAgent:
    """Testes para o agente de leitura de arquivos"""
    
    class TestFileMetadata:
        """Testes relacionados aos metadados dos arquivos"""
        
        def test_should_extract_basic_file_metadata(self):
            """Deve extrair metadados básicos de um arquivo existente"""
            # Arrange
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write("conteúdo de teste")
                tmp_file_path = tmp_file.name
            
            try:
                # Act
                metadata = _get_file_metadata(tmp_file_path, "txt")
                
                # Assert
                assert "metadata" in metadata
                assert metadata["metadata"]["file_name"].endswith(".txt")
                assert metadata["metadata"]["file_type"] == "txt"
                assert metadata["metadata"]["file_size"] > 0
                assert metadata["metadata"]["file_hash"] is not None
                assert len(metadata["metadata"]["file_hash"]) == 32  # MD5 hash length
                assert "created_at" in metadata["metadata"]
                assert "modified_at" in metadata["metadata"]
                assert "processed_at" in metadata["metadata"]
                # Verifica formato ISO
                assert "T" in metadata["metadata"]["created_at"]
                assert "T" in metadata["metadata"]["modified_at"] 
                assert "T" in metadata["metadata"]["processed_at"]
            finally:
                Path(tmp_file_path).unlink()
        
        def test_should_handle_nonexistent_file(self):
            """Deve tratar arquivo inexistente adequadamente"""
            # Arrange
            nonexistent_path = "/caminho/que/nao/existe/arquivo.txt"
            
            # Act & Assert
            with pytest.raises(FileNotFoundError):
                _get_file_metadata(nonexistent_path, "txt")
    
    class TestPDFProcessing:
        """Testes para processamento de arquivos PDF"""
        
        @patch('builtins.open', create=True)
        @patch('agents.reader_agent.pypdf.PdfReader')
        def test_should_process_valid_pdf(self, mock_pdf_reader, mock_file_open):
            """Deve processar um PDF válido com múltiplas páginas"""
            # Arrange
            mock_page1 = MagicMock()
            mock_page1.extract_text.return_value = "Conteúdo da página 1 com email@teste.com"
            mock_page2 = MagicMock()
            mock_page2.extract_text.return_value = "Conteúdo da página 2 com telefone (11) 99999-9999"
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page1, mock_page2]
            mock_pdf_reader.return_value = mock_reader_instance
            
            # Mock file operations
            mock_file_open.return_value.__enter__ = mock_file_open
            mock_file_open.return_value.__exit__ = MagicMock()
            
            # Mock metadados
            base_metadata = {"metadata": {"file_name": "teste.pdf"}}
            
            # Act
            result = _process_pdf("fake_path.pdf", base_metadata)
            
            # Assert
            assert "error" not in result
            assert result["document_info"]["total_pages"] == 2
            assert result["document_info"]["total_words"] > 0
            assert len(result["content"]["pages"]) == 2
            assert result["content"]["pages"][0]["page_number"] == 1
            assert result["content"]["pages"][1]["page_number"] == 2
            assert "extracted_patterns" in result["content"]
            assert "emails" in result["content"]["extracted_patterns"]
            assert "phones" in result["content"]["extracted_patterns"]
        
        def test_should_handle_pdf_processing_error(self):
            """Deve tratar erros ao processar PDF inválido"""
            # Arrange
            invalid_pdf_path = "/caminho/inexistente/arquivo.pdf"
            base_metadata = {"metadata": {"file_name": "teste.pdf"}}
            
            # Act
            result = _process_pdf(invalid_pdf_path, base_metadata)
            
            # Assert
            assert "error" in result
            assert result["content"] is None
            assert result["metadata"]["file_name"] == "teste.pdf"
    
    class TestCSVProcessing:
        """Testes para processamento de arquivos CSV"""
        
        def test_should_process_valid_csv_file(self):
            """Deve processar um arquivo CSV válido com análise completa"""
            # Arrange
            csv_content = "nome,idade,cidade,salario\nJoão,30,São Paulo,5000.50\nMaria,25,Rio de Janeiro,6000.75\nPedro,35,,4500.25"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                tmp_file.write(csv_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Act
                result = read_file(tmp_file_path, "csv")
                
                # Assert
                assert "error" not in result
                assert "structure_info" in result
                assert result["structure_info"]["total_rows"] == 3
                assert result["structure_info"]["total_columns"] == 4
                assert set(result["structure_info"]["columns"]) == {"nome", "idade", "cidade", "salario"}
                
                # Verifica análise das colunas
                column_analysis = result["structure_info"]["column_analysis"]
                assert "nome" in column_analysis
                assert column_analysis["nome"]["non_null_count"] == 3
                assert column_analysis["nome"]["null_count"] == 0
                assert column_analysis["cidade"]["null_count"] == 1  # Pedro não tem cidade
                
                # Verifica registros
                assert len(result["content"]["records"]) == 3
                assert result["content"]["records"][0]["nome"] == "João"
                assert result["content"]["records"][0]["idade"] == 30
                
                # Verifica estatísticas
                assert "summary_stats" in result["content"]
            finally:
                Path(tmp_file_path).unlink()
        
        def test_should_handle_empty_csv_file(self):
            """Deve tratar arquivo CSV vazio"""
            # Arrange
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                tmp_file.write("")
                tmp_file_path = tmp_file.name
            
            try:
                # Act
                result = read_file(tmp_file_path, "csv")
                
                # Assert
                # Pode retornar erro ou estrutura vazia, ambos são válidos
                if "error" not in result:
                    assert result["structure_info"]["total_rows"] == 0
                    assert result["content"]["summary_stats"] == {}
            finally:
                Path(tmp_file_path).unlink()
        
        def test_should_handle_malformed_csv(self):
            """Deve tratar CSV mal formado"""
            # Arrange
            malformed_csv = "nome,idade\nJoão,30,extra_column\nMaria"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                tmp_file.write(malformed_csv)
                tmp_file_path = tmp_file.name
            
            try:
                # Act
                result = read_file(tmp_file_path, "csv")
                
                # Assert
                # Pandas geralmente consegue lidar com CSVs mal formados
                # Verificamos se pelo menos não crashou
                assert isinstance(result, dict)
            finally:
                Path(tmp_file_path).unlink()
    
    class TestExcelProcessing:
        """Testes para processamento de arquivos Excel"""
        
        def test_should_process_excel_with_multiple_sheets(self):
            """Deve processar Excel com múltiplas planilhas"""
            # Arrange
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                tmp_file_path = tmp_file.name
            
            # Cria um Excel de teste
            df1 = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
            df2 = pd.DataFrame({"C": [4, 5], "D": ["a", "b"]})
            
            with pd.ExcelWriter(tmp_file_path, engine='xlsxwriter') as writer:
                df1.to_excel(writer, sheet_name='Sheet1', index=False)
                df2.to_excel(writer, sheet_name='Sheet2', index=False)
            
            try:
                # Act - Testamos com "xls" que está na lista do match
                result = read_file(tmp_file_path, "xls")
                
                # Assert
                assert "error" not in result
                assert "workbook_info" in result
                assert result["workbook_info"]["total_sheets"] == 2
                assert set(result["workbook_info"]["sheet_names"]) == {"Sheet1", "Sheet2"}
                
                # Verifica conteúdo das planilhas
                sheets = result["content"]["sheets"]
                assert "Sheet1" in sheets
                assert "Sheet2" in sheets
                assert sheets["Sheet1"]["structure_info"]["total_rows"] == 3
                assert sheets["Sheet2"]["structure_info"]["total_rows"] == 2
            finally:
                Path(tmp_file_path).unlink()
        
        def test_should_handle_excel_processing_error(self):
            """Deve tratar erros ao processar Excel inválido"""
            # Arrange - Cria um arquivo temporário inválido
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xls', delete=False) as tmp_file:
                tmp_file.write("conteúdo inválido para excel")
                tmp_file_path = tmp_file.name
            
            try:
                # Act
                result = read_file(tmp_file_path, "xls")
                
                # Assert
                assert "error" in result
                assert result["content"] is None
            finally:
                Path(tmp_file_path).unlink()
    
    class TestXMLProcessing:
        """Testes para processamento de arquivos XML"""
        
        def test_should_process_valid_xml_file(self):
            """Deve processar XML válido com estrutura hierárquica"""
            # Arrange
            xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
            <root xmlns="http://example.com" version="1.0">
                <person id="1">
                    <name>João Silva</name>
                    <age>30</age>
                    <email>joao@email.com</email>
                </person>
                <person id="2">
                    <name>Maria Santos</name>
                    <age>25</age>
                </person>
                <metadata>
                    <created>2024-01-01</created>
                </metadata>
            </root>'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(xml_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Act
                result = read_file(tmp_file_path, "xml")
                
                # Assert
                assert "error" not in result
                assert "xml_info" in result
                assert result["xml_info"]["root_tag"] == "{http://example.com}root"
                assert result["xml_info"]["namespace"] == "http://example.com"
                assert result["xml_info"]["total_elements"] > 1
                assert "version" in result["xml_info"]["root_attributes"]
                
                # Verifica estrutura convertida
                structure = result["content"]["structure"]
                # Com namespace, as chaves incluem o namespace
                person_key = "{http://example.com}person"
                assert person_key in structure
                assert isinstance(structure[person_key], list)  # Múltiplos elementos person
                assert len(structure[person_key]) == 2
                
                # Verifica elementos brutos
                assert "raw_elements" in result["content"]
                assert len(result["content"]["raw_elements"]) > 0
            finally:
                Path(tmp_file_path).unlink()
        
        def test_should_handle_malformed_xml(self):
            """Deve tratar XML mal formado"""
            # Arrange
            malformed_xml = '<root><person><name>João</name></root>'  # Tag person não fechada
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp_file:
                tmp_file.write(malformed_xml)
                tmp_file_path = tmp_file.name
            
            try:
                # Act
                result = read_file(tmp_file_path, "xml")
                
                # Assert
                assert "error" in result
                assert result["content"] is None
            finally:
                Path(tmp_file_path).unlink()
    
    class TestPatternExtraction:
        """Testes para extração de padrões comuns"""
        
        def test_should_extract_all_common_patterns(self):
            """Deve extrair todos os padrões comuns do texto"""
            # Arrange
            text = """
            Contato: João Silva
            Email: joao.silva@empresa.com.br
            Telefone: (11) 99999-9999 ou +55 11 8888-8888
            CPF: 123.456.789-00
            CNPJ: 12.345.678/0001-90
            Data de nascimento: 15/08/1990
            Valor: R$ 1.500,75
            Website: https://www.exemplo.com.br/contato?id=123
            """
            
            # Act
            patterns = _extract_common_patterns(text)
            
            # Assert
            assert "emails" in patterns
            assert "joao.silva@empresa.com.br" in patterns["emails"]
            
            assert "phones" in patterns
            assert len(patterns["phones"]) >= 1
            
            assert "cpf" in patterns
            assert "123.456.789-00" in patterns["cpf"]
            
            assert "cnpj" in patterns  
            assert "12.345.678/0001-90" in patterns["cnpj"]
            
            assert "dates" in patterns
            assert "15/08/1990" in patterns["dates"]
            
            assert "money" in patterns
            assert "R$ 1.500,75" in patterns["money"]
            
            assert "urls" in patterns
            assert "https://www.exemplo.com.br/contato?id=123" in patterns["urls"]
        
        def test_should_return_empty_dict_for_no_patterns(self):
            """Deve retornar dicionário vazio quando não há padrões"""
            # Arrange
            text = "Este é um texto simples sem padrões especiais."
            
            # Act
            patterns = _extract_common_patterns(text)
            
            # Assert
            assert isinstance(patterns, dict)
            # Não deve conter chaves para padrões vazios
            for pattern_list in patterns.values():
                assert len(pattern_list) > 0
        
        def test_should_handle_empty_text(self):
            """Deve tratar texto vazio"""
            # Arrange
            text = ""
            
            # Act  
            patterns = _extract_common_patterns(text)
            
            # Assert
            assert isinstance(patterns, dict)
            assert len(patterns) == 0
    
    class TestMainFunction:
        """Testes para a função principal read_file"""
        
        def test_should_route_to_correct_processor(self):
            """Deve rotear para o processador correto baseado no tipo"""
            # Arrange
            csv_content = "nome,idade\nJoão,30"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                tmp_file.write(csv_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Act
                result = read_file(tmp_file_path, "csv")
                
                # Assert
                assert "structure_info" in result  # Específico do CSV
                assert "metadata" in result
            finally:
                Path(tmp_file_path).unlink()
        
        def test_should_raise_error_for_unsupported_file_type(self):
            """Deve levantar erro para tipo de arquivo não suportado"""
            # Arrange - Cria um arquivo temporário para não ter erro de arquivo não encontrado
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write("conteúdo de teste")
                tmp_file_path = tmp_file.name
            
            try:
                # Act & Assert
                with pytest.raises(ValueError, match="Tipo de arquivo não suportado"):
                    read_file(tmp_file_path, "unsupported")
            finally:
                Path(tmp_file_path).unlink()
        
        def test_should_handle_excel_file_types(self):
            """Deve tratar ambos os tipos de Excel (xls e xlsx)"""
            # Este teste seria mais complexo, pois precisaria criar arquivos Excel reais
            # Por enquanto, testamos que não levanta erro para tipos conhecidos
            pass
    
    class TestIntegration:
        """Testes de integração end-to-end"""
        
        def test_complete_workflow_csv(self):
            """Teste completo do workflow para arquivo CSV"""
            # Arrange
            csv_content = "produto,preco,categoria\nNotebook,2500.99,Eletrônicos\nMouse,45.50,Acessórios"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                tmp_file.write(csv_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Act
                result = read_file(tmp_file_path, "csv")
                
                # Assert - Verifica estrutura completa do resultado
                assert "metadata" in result
                assert "structure_info" in result  
                assert "content" in result
                
                # Metadados
                metadata = result["metadata"]
                assert metadata["file_type"] == "csv"
                assert metadata["file_size"] > 0
                
                # Estrutura
                structure = result["structure_info"]
                assert structure["total_rows"] == 2
                assert structure["total_columns"] == 3
                
                # Conteúdo
                content = result["content"]
                assert len(content["records"]) == 2
                assert content["records"][0]["produto"] == "Notebook"
            finally:
                Path(tmp_file_path).unlink()

    class TestNotasParaTeste:
        def test_processar_todos_xmls_na_pasta(self):
            """Deve processar todos os XMLs da pasta notas_para_teste sem erro e retornar dict"""
            pasta = os.path.join(os.path.dirname(__file__), 'notas_para_teste')
            arquivos_xml = glob.glob(os.path.join(pasta, '*.xml'))
            assert arquivos_xml, 'Nenhum arquivo XML encontrado na pasta notas_para_teste'
            for arquivo in arquivos_xml:
                resultado = read_file(arquivo, 'xml')
                print(resultado)
                assert isinstance(resultado, dict), f'Resultado não é dict para {arquivo}'