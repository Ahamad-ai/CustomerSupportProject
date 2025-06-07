import streamlit as st
import pandas as pd
from Collection.flipkart_scrapper import FlipkartScraper
from data_ingestion.ingestion_pipeline import DataIngestion
from retriever.retrievals import Retriever
from prompt_library.prompt import PROMPT_TEMPLATES

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from myutils.model_loader import ModelLoader

# Set up Streamlit page
st.set_page_config(page_title="Flipkart AI Chatbot", layout="wide")

st.title("🛒 Flipkart AI Chatbot")

# Initialize objects
retriever_obj = Retriever()
model_loader = ModelLoader()

# Sidebar: Product Scraping
with st.sidebar:
    st.header("🔍 Product Scraper")
    product_category = st.text_input("Enter product category")
    
    if st.button("Scrape Data"):
        if product_category:
            scraper = FlipkartScraper(product_category)
            df = scraper.run_pipeline()
            st.session_state["scraped_data"] = df  # Store scraped data in session state
            st.success(f"Data scraped for {product_category}.")
        else:
            st.warning("Please enter a product category!")

    if st.button("Ingest Data"):
        ingestion = DataIngestion()
        ingestion.run_pipeline()
        st.success("Data successfully stored in AstraDB!")

# Display Scraped Data (if available)
if "scraped_data" in st.session_state:
    st.subheader("📌 Scraped Product Data")
    st.dataframe(st.session_state["scraped_data"])

# Chatbot Interface
st.subheader("💬 Chat with Flipkart AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

def invoke_chain(query: str):
    retriever = retriever_obj.load_retriever()
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATES["customer_support_bot"])
    llm = model_loader.load_llm()

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke(query)

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
user_input = st.chat_input("Ask about Flipkart products...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    response = invoke_chain(user_input)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.chat_message("assistant").write(response)