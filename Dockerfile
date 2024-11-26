# Use the prebuilt Ollama image as the base
FROM ollama/ollama:latest

# Set the working directory for your FastAPI app
WORKDIR /app

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Copy requirements and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy the entire project into the container
COPY . /app

# Make the start script executable
RUN chmod +x /app/start.sh

# Expose ports for both Ollama and FastAPI
EXPOSE 8080 11434

# Use the start script to start both services
ENTRYPOINT ["/bin/bash", "/app/start.sh"]