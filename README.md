# Flipkart Customer Support AI Chatbot System

## Overview
This project is an end-to-end AI-powered Customer Support System for e-commerce platforms, focused on Flipkart product data. It combines real-time product scraping, data ingestion, vector search, and advanced LLM-based chat to deliver instant, context-aware support and recommendations to users.

## Features
- **Flipkart Product Scraper**: Scrapes real-time product details, reviews, and ratings from Flipkart.
- **Data Ingestion Pipeline**: Transforms and stores product data in AstraDB vector store for semantic search.
- **Retriever**: Efficiently fetches relevant product information using vector search.
- **AI Chatbot (FastAPI & Streamlit)**: Provides product recommendations, troubleshooting, and customer support via web chat or Streamlit UI.
- **Prompt Engineering**: Uses advanced prompt templates for concise, helpful, and engaging responses.
- **Configurable LLMs**: Supports Google Gemini and Groq LLMs for flexible deployment.
- **Modern UI**: Responsive chat interface with custom CSS and Jinja2 templates.

## Architecture & Main Modules
- `Collection/flipkart_scrapper.py`: Scrapes product data from Flipkart.
- `data_ingestion/ingestion_pipeline.py`: Loads, transforms, and ingests data into AstraDB.
- `retriever/retrievals.py`: Handles semantic search and retrieval from the vector store.
- `myutils/model_loader.py`: Loads embedding and LLM models.
- `prompt_library/prompt.py`: Contains prompt templates for the chatbot.
- `main.py`: FastAPI backend for chat and scraping endpoints.
- `app_working.py`: Streamlit app for interactive chatbot and data management.
- `templates/chat.html` & `static/styles.css`: Frontend UI for the chatbot.

## Setup & Installation
1. **Clone the repository**
2. **Create and activate a virtual environment** (recommended):
   ```powershell
   python -m venv myenv
   .\myenv\Scripts\activate
   ```
3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
4. **Set up environment variables**:
   - Create a `.env` file with the following keys:
     - `GOOGLE_API_KEY`
     - `ASTRA_DB_API_ENDPOINT`
     - `ASTRA_DB_APPLICATION_TOKEN`
     - `ASTRA_DB_KEYSPACE`

5. **Configuration**:
   - Edit `config/config.yaml` to set model, retriever, and DB parameters as needed.

## Usage
### 1. FastAPI Web Chatbot
Start the FastAPI server:
```powershell
uvicorn main:app --reload
```
- Visit [http://localhost:8000](http://localhost:8000) for the chat UI.
- Use `/scrape/{product_category}` endpoint to scrape new product data.

### 2. Streamlit App
Run the Streamlit interface:
```powershell
streamlit run app_working.py
```
- Use the sidebar to scrape and ingest data.
- Chat with the AI bot in the main window.

## Data Files
- `flipkart_data.csv`: Sample product data.
- `Data/flipkart_realtime_scrape.csv`: Real-time scraped data.

## Technologies Used
- Python, FastAPI, Streamlit, Jinja2
- BeautifulSoup, Requests, Pandas, NLTK, Emoji
- LangChain, Google Gemini, Groq, AstraDB
- HTML, CSS

## Folder Structure
- `Collection/` - Scraper logic
- `data_ingestion/` - Data pipeline
- `retriever/` - Vector search
- `myutils/` - Model/config utilities
- `prompt_library/` - Prompt templates
- `templates/` - HTML templates
- `static/` - CSS/assets
- `config/` - YAML config
- `Data/` - Data files

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## Notice
This project is developed by **Ahamad** for educational purposes only. All rights reserved.
