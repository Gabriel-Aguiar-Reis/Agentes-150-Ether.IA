import os
from langchain.llms import OpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase


def get_query_chain():
    db_path = os.getenv("DB_PATH", "data/banco.db")
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    llm = OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
    return SQLDatabaseChain.from_llm(llm, db, verbose=True)

def answer_query(query):
    chain = get_query_chain()
    return chain.run(query)

