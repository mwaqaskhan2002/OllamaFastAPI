import os
import subprocess
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import time
import logging

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define the Ollama server URL from an environment variable with a default fallback
OLLAMA_SERVER_URL = os.getenv("OLLAMA_SERVER_URL", "http://localhost:11434")


def start_ollama():
    """Start the Ollama server."""
    try:
        logging.info("Starting Ollama server...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)  # Give Ollama some time to start up
        logging.info("Ollama server started successfully.")
    except Exception as e:
        logging.error(f"Failed to start Ollama server: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama server failed to start: {e}")


def pull_model(model_name: str):
    """Pull the specified model from Ollama."""
    try:
        logging.info(f"Pulling model '{model_name}'...")
        response = requests.post(
            f"{OLLAMA_SERVER_URL}/api/pull", json={"name": model_name}
        )
        if response.status_code != 200:
            logging.error(f"Failed to pull model '{model_name}': {response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to download model: {response.text}")
        logging.info(f"Model '{model_name}' downloaded successfully.")
        return {"message": f"Model {model_name} downloaded successfully"}
    except requests.RequestException as e:
        logging.error(f"Error pulling model '{model_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Error pulling model: {e}")


@app.on_event("startup")
async def startup_event():
    """Event triggered when the app starts."""
    start_ollama()  # Ollama starts when the app starts
    
@app.get('/')
def home():
    return RedirectResponse(url="/docs")

@app.get("/ask")
def ask(prompt: str):
    """Generate a response from the model."""
    try:
        logging.info(f"Generating response for prompt: {prompt}")
        res = requests.post(
            f"{OLLAMA_SERVER_URL}/api/generate",
            json={"prompt": prompt, "stream": False, "model": "llama3.2"}
        )
        res.raise_for_status()

        # Return only the response content without verbose metadata
        response_json = res.json()
        if "response" in response_json:
            return {"response": response_json["response"]}  # Return the response correctly
        else:
            raise HTTPException(status_code=500, detail="Malformed response from Ollama")
    except requests.RequestException as e:
        logging.error(f"Error during prompt generation: {e}")
        raise HTTPException(status_code=500, detail=f"Error during prompt generation: {e}")

import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
