# Use the official Python image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

