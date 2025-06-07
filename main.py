import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from Collection.flipkart_scrapper import FlipkartScraper
from data_ingestion.ingestion_pipeline import DataIngestion
from retriever.retrievals import Retriever
from myutils.model_loader import ModelLoader
from prompt_library.prompt import PROMPT_TEMPLATES
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import pandas as pd

# Initialize FastAPI app
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Define the Query model
class Query(BaseModel):
    query: str

# Global variables for retriever and model (Initially None)
retriever_obj = None
model_loader = None

@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    """Serve the chat interface."""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/scrape/{product_category}")
async def scrape_data(product_category: str):
    """Scrape product data from Flipkart."""
    try:
        scraper = FlipkartScraper(product_category)
        df = scraper.run_pipeline()
        data = df.to_dict(orient='records')
        return {"message": f"Data scraped for {product_category}", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_data():
    """Ingest data into AstraDB and load retriever & model once."""
    global retriever_obj, model_loader  # Use global variables
    try:
        ingestion = DataIngestion()
        ingestion.run_pipeline()

        # Load retriever and model **ONLY ONCE**
        retriever_obj = Retriever().load_retriever()
        model_loader = ModelLoader().load_llm()
        
        return {"message": "Data successfully stored in AstraDB!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(query: Query):
    """Process chat queries with preloaded retriever & model."""
    global retriever_obj, model_loader

    if retriever_obj is None or model_loader is None:
        raise HTTPException(status_code=500, detail="Model & retriever not loaded. Run /ingest first.")

    try:
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATES["customer_support_bot"])

        chain = (
            {"context": retriever_obj, "question": RunnablePassthrough()}
            | prompt
            | model_loader
            | StrOutputParser()
        )

        response = chain.invoke(query.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)