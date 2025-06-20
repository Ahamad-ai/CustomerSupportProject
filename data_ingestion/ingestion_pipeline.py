import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from typing import List, Tuple
from langchain_core.documents import Document
from langchain_astradb import AstraDBVectorStore
from myutils.model_loader import ModelLoader
from myutils.config_loader import load_config

class DataIngestion:
    """
    Class to handle data transformation and ingestion into Astra DB vector store.
    """

    def __init__(self):
        """
        Initiate environment variables, embedding model and set CSV file path
        """
        print("Initializing DataIngestion pipeline...")
        self.model_loader=ModelLoader()
        self._load_env_variables()
        self.csv_path = self._get_csv_path()
        self.product_data=self._load_csv()
        self.config=load_config()

    def _load_env_variables(self):
        """
        Load and validate required environment variables
        """
        load_dotenv()
        required_vars=["GOOGLE_API_KEY","ASTRA_DB_API_ENDPOINT","ASTRA_DB_APPLICATION_TOKEN",
                       "ASTRA_DB_KEYSPACE"]
        
        missing_vars=[var for var in required_vars if os.getenv(var) is None]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")
        
        self.google_api_key=os.getenv("GOOGLE_API_KEY")
        self.db_api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT")
        self.db_application_token=os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.db_keyspace=os.getenv("ASTRA_DB_KEYSPACE")

    def _get_csv_path(self):
        """
        Get path to the csv file located inside 'data' folder
        """
        current_dir=os.getcwd()
        csv_path=os.path.join(current_dir,"data","flipkart_realtime_scrape.csv")

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at : {csv_path}")
        
        return csv_path

    def _load_csv(self):
        """
        Load product data from CSV.
        """
        df=pd.read_csv(self.csv_path)
        expected_columns={'product_title', 'product_price', 'product_rating',
       'product_highlights', 'product_description', 'product_reviews',
       'product_link'}

        if not expected_columns.issubset(set(df.columns)):
            raise ValueError(f"CSV must contain columns: {expected_columns}")
        
        return df
    
    def transform_data(self):
        product_list=[]
        
        for _,row in self.product_data.iterrows():
            product_entry={
                "product_title": row["product_title"],
                "product_price": row["product_price"],
                "product_rating": row["product_rating"],
                "product_highlights": row["product_highlights"],
                "product_reviews": row["product_reviews"],
                "product_description": row["product_description"],
                "product_link": row["product_link"]            
                }
            product_list.append(product_entry)

        documents=[]
        for entry in product_list:
            metadata = {
                "product_title": entry["product_title"],
                "product_price": entry["product_price"],
                "product_rating": entry["product_rating"],
                "product_highlights": entry["product_highlights"],
                "product_description": entry["product_description"],
                "product_link": entry["product_link"]
            }
            for key, value in metadata.items():
                if isinstance(value, float) and np.isnan(value):  # Check if it's NaN
                    metadata[key] = ""  # Replace NaN with an empty string

            review_content = entry.get("product_reviews", "")
            if isinstance(review_content, float) and np.isnan(review_content):
                review_content = "No reviews available."

            doc = Document(page_content=review_content, metadata=metadata)
            documents.append(doc)

        return documents
        
    def store_in_vector_db(self,documents: List[Document]):
        """
        Store documents into AstraDB vector store
        """
        collection_name=self.config["astra_db"]["collection_name"]
        vstore=AstraDBVectorStore(
            embedding=self.model_loader.load_embeddings(),
            collection_name=collection_name,
            api_endpoint=self.db_api_endpoint,
            token=self.db_application_token,
            namespace=self.db_keyspace
            )
        inserted_ids=vstore.add_documents(documents)
        print(f"Successfully inserted {len(inserted_ids)} documents into AstraDB")
        return vstore, inserted_ids
    
    def run_pipeline(self):
        """
        Run the full data ingestion pipeline : transform data and store into vector DB
        """

        documents=self.transform_data()
        vstore,inserted_ids = self.store_in_vector_db(documents)


if __name__=="__main__":
    ingestion = DataIngestion()
    ingestion.run_pipeline()