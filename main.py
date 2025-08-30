# Importing required libraries
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from PIL import Image
import qrcode


app = FastAPI() # Create FastAPI instance

class Url(BaseModel): # Defining URL through Pydantic
    url: str = Field("localhost:8000")
    
@app.post("/generate") # POST HTTP endpoint when generating QR code
async def generate_qr_code(url: Url):
    try: 
        img = qrcode.make(url.url)
        filename = "qrcode.png" # Defining name of QR Code and save location
        img.save("./qrcodes/" + filename)
        return {"message": "QR Code has been generated successfully!", "qrcode": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") # QR code generation fails due to the server

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) # Run the uvicorn server for FastAPI
    