# NoSQLNoProblem

NoSQLNoProblem is a natural language interface to your SQL databases powered by Google Generative AI and LangChain. It lets you ask questions conversationally without ever needing to see or write SQL queries. The app handles SQL generation and execution behind the scenes, returning clear, human-friendly answers.

## Features

- Natural language question answering over any SQL database
- SQL query generation fully abstracted from the user
- Powered by Google Gemini 2.5 for accurate, context-aware responses
- Few-shot learning with semantic example retrieval for better query understanding
- Streamlit-based clean user interface focusing on ease-of-use
- Provides only answers no SQL code exposure
- Error handling and feedback for conversational flow

Type your question about the database and receive a human readable answer no SQL exposure.

## Example Questions

- What is the total inventory value for small t-shirts?
- How much revenue would we generate selling all Levi's shirts without discount?
- How many white Levi's shirts are currently in stock?

## How It Works

- You enter a question in natural language
- The backend LLM generates the SQL query internally
- The SQL is executed on your database
- The result is converted to a clean, summarized answer and displayed

## Contributing

Feel free to open issues or submit PRs to improve conversational flow or add support for new database types.


