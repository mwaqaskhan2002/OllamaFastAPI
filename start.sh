#!/bin/bash

# Start Ollama server in the background
ollama serve &

# Store the PID of the Ollama server
ollama_pid=$!

# Wait for the Ollama server to initialize
echo "Waiting for Ollama server to start..."
sleep 5
echo "Ollama server started."

# Check if the model is already downloaded
if [ ! -d "/data/models/llama3.2" ]; then
    echo "Model not found in /data/models. Pulling the llama3.2 model..."
    ollama pull llama3.2
else
    echo "Model already exists in /data/models. Skipping download."
fi


# Start FastAPI
echo "Starting FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8080

# Wait for Ollama server process to finish before exiting
wait $ollama_pid
