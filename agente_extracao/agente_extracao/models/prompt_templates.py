from langchain.prompts import PromptTemplate

QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="Você é um assistente que responde perguntas sobre os dados carregados. Pergunta: {question}"
)

