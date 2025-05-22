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

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "uvicorn", "codeassist.api.main:app", "--host", "0.0.0.0", "--port", "8000"]