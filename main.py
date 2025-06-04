import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from Collection.flipkart_scrapper import FlipkartScraper
from data_ingestion.ingestion_pipeline import DataIngestion
from retriever.retrievals import Retriever
from prompt_library.prompt import PROMPT_TEMPLATES
from utils.model_loader import ModelLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

app = FastAPI()

# Serve static files (CSS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load templates
templates = Jinja2Templates(directory="templates")

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

retriever_obj = Retriever()
model_loader = ModelLoader()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the chatbot interface."""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/scrape")
async def scrape_flipkart(product_category: str = Query(..., description="Product category to scrape")):
    """Scrapes Flipkart product data and returns JSON."""
    try:
        scraper = FlipkartScraper(product_category)
        df = scraper.run_pipeline()
        return JSONResponse(content={"data": df.to_dict(orient="records")})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/ingest")
async def ingest_data():
    """Transforms scraped data and stores it in AstraDB."""
    try:
        ingestion = DataIngestion()
        ingestion.run_pipeline()
        return JSONResponse(content={"message": "Data successfully stored in AstraDB"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/query")
async def query_product(question: str = Query(..., description="Ask about a Flipkart product")):
    """Retrieves product details and returns AI response."""
    try:
        retriever = retriever_obj.load_retriever()
        context_docs = retriever.invoke(question)  
        context_text = "\n".join([doc.page_content for doc in context_docs])  

        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATES["product_bot"])
        llm = model_loader.load_llm()

        chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        result = chain.invoke({"context": context_text, "question": question})  
        print(f"AI Response: {result}")  # ✅ Debugging log

        return JSONResponse(content={"answer": str(result)})
    except Exception as e:
        print(f"Error Occurred: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)