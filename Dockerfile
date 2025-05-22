# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml .
COPY README.md .

# Install dependencies
RUN pip install --no-cache-dir -e .

# Copy the entire project
COPY . .

# Create startup script
RUN echo '#!/bin/bash\nexec python -m uvicorn codeassist.api.main:app --host 0.0.0.0 --port ${PORT:-8000}' > /app/start.sh
RUN chmod +x /app/start.sh

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["python", "codeassist/api/main.py"]