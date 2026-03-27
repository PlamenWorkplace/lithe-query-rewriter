# LITHE: LLM-based SQL Query Rewriter

## Prerequisites

- Python 3.8+
- A running database instance (e.g., PostgreSQL) to test the `EXPLAIN` query costs. We use the dataset from Assignment 1.
- API keys for your preferred LLM provider (Groq, OpenAI, Google Gemini, etc.) or a local Ollama instance.

## Installation

1. Clone this repository and navigate to the project directory.
2. Create and activate a virtual environment. Install required dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Configuration

This script relies on environment variables to connect to your database and LLM provider. You must create a .env file in the root directory of the project.

Create a file named .env and add the following configuration:

```code
DATABASE_URI=postgresql://username:password@localhost:5432/your_database

# Examples: "groq/llama-3.3-70b-versatile", "gemini/gemini-2.5-flash", "ollama/llama3"
LLM_MODEL=

GROQ_API_KEY=
GEMINI_API_KEY=
OPENAI_API_KEY=
```

## Usage

Once your environment is activated and your .env file is configured, run the main script to start evaluating the queries:

```code
python lithe.py
```