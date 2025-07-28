# 1. Start from a slim Python image for small size
FROM python:3.10-slim

# 2. Set working directory in container
WORKDIR /app

# 3. Copy only requirements first (to allow Docker layer caching)
COPY requirements.txt .

# 4. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 4.5. Pre-download the sentence-transformers model for offline use
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 4.6. Set environment variables for offline mode
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_OFFLINE=1

# 5. Copy Python files only
COPY *.py ./

# 6. Set a default command (expects persona.txt and job.txt in input folder)
CMD ["python", "main.py", "--input_folder", "/app/input", "--persona_file", "/app/input/persona.txt", "--job_file", "/app/input/job.txt", "--output_json", "/app/output/output.json"]
