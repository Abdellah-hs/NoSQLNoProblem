from turtle import st

from langchain_google_genai import ChatGoogleGenerativeAI
from pyngrok import ngrok
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

from langchain_core.example_selectors.semantic_similarity import SemanticSimilarityExampleSelector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate

from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
DB_URI = os.getenv("DATABASE_URL")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=API_KEY,
    temperature=0
)

db = SQLDatabase.from_uri(DB_URI)

few_shots = [
    {
        'Question': "How much is the total price of the inventory for all S-size t-shirts?",
        'SQLQuery': "SELECT SUM(price * stock_quantity) FROM t_shirts WHERE size = 'S'",
        'SQLResult': "Result of the SQL query",
        'Answer': '22292'
    },
    {
        'Question': "If we have to sell all the Levi’s T-shirts today. How much revenue our store will generate without discount?",
        'SQLQuery': "SELECT SUM(price * stock_quantity) FROM t_shirts WHERE brand = 'Levi'",
        'SQLResult': "Result of the SQL query",
        'Answer': '17462'
    },
    {
        'Question': "How many white color Levi's shirts do I have?",
        'SQLQuery': "SELECT SUM(stock_quantity) FROM t_shirts WHERE brand = 'Levi' AND color = 'White'",
        'SQLResult': "Result of the SQL query",
        'Answer': '290'
    }
]

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
to_vectorize = [" ".join(example.values()) for example in few_shots]
chroma = Chroma.from_texts(to_vectorize, embeddings, metadatas=few_shots)

example_selector = SemanticSimilarityExampleSelector(
    vectorstore=chroma,
    k=2,
)

mysql_prompt = """
You are a MySQL expert. Follow these rules:

1. First, write a syntactically correct MySQL query.
2. Then, based on the results, answer the question.
3. Never SELECT * — only query needed columns.
4. Wrap all column names in backticks like `col`.
5. Use LIMIT {top_k} unless the user asks for a different number.
6. Use CURDATE() for "today".
7. Only use columns that exist in the provided schema.

FORMAT (must always match EXACTLY):

Question: <question>
SQLQuery: <query>
SQLResult: <result>
Answer: <final answer>
"""

example_prompt = PromptTemplate(
    input_variables=["Question", "SQLQuery", "SQLResult", "Answer"],
    template=(
        "Question: {Question}\n"
        "SQLQuery: {SQLQuery}\n"
        "SQLResult: {SQLResult}\n"
        "Answer: {Answer}"
    )
)

CUSTOM_SUFFIX = """
Here is the database schema:
{table_info}

Question: {input}
SQLQuery:
"""

few_shot_prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix=mysql_prompt,
    suffix=CUSTOM_SUFFIX,
    input_variables=["input", "table_info", "top_k"],
)

chain = SQLDatabaseChain.from_llm(
    llm=llm,
    db=db,
    prompt=few_shot_prompt,
    return_direct=True,
    verbose=True,
)

import streamlit as st

question = st.text_input("Ask something about your database:")

if st.button("Run Query") and question.strip():
    with st.spinner("Running query..."):
        try:
            answer = chain.run(question)
            st.success("Result:")
            st.write(answer)
        except Exception as e:
            st.error(f"Error: {e}")
