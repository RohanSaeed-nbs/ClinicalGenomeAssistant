# Use an official lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose necessary ports
EXPOSE 8501 5000

# Start both frontend and backend
CMD ["sh", "-c", "streamlit run frontend/generate.py & python backend/app.py"]