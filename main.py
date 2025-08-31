# Importing required libraries
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from io import BytesIO
from azure.storage.blob import BlobServiceClient, ContainerClient
from dotenv import load_dotenv
from PIL import Image
import os
import qrcode

# Load env variables
load_dotenv()

# Get Azure Credentials from env
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

print("AZURE_CONNECTION_STRING:", AZURE_CONNECTION_STRING)
print("AZURE_CONTAINER_NAME:", AZURE_CONTAINER_NAME)


LOCAL_QR_FOLDER="./qrcodes"
os.makedirs(LOCAL_QR_FOLDER, exist_ok=True)

# Create BlobService Client
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

app = FastAPI() # Create FastAPI instance

class Url(BaseModel): # Defining URL through Pydantic
    url: str = Field("localhost:8000")
    
@app.post("/generate") # POST HTTP endpoint when generating QR code
async def generate_qr_code(url: Url):
    try: 
        img = qrcode.make(url.url)
        
        filename = "qrcode.png"
        local_path = os.path.join(LOCAL_QR_FOLDER, filename)
        img.save(local_path)
        
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        blob_client = container_client.get_blob_client(filename)
        blob_client.upload_blob(img_bytes, overwrite=True)
        
        blob_url = blob_client.url
                
        return {"message": "QR Code has been generated successfully!",
                "local_path": local_path,
                "qrcode_url": blob_url
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}") # QR code generation fails due to the server

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) # Run the uvicorn server for FastAPI
    