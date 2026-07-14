FROM python:3.13.4-slim-bullseye

WORKDIR /app

# Install system dependencies (only runs once unless the image base changes)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies separately to leverage caching
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Now copy your application code
COPY . .

ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV HOME=/tmp
ENV STREAMLIT_SERVER_HEADLESS=true

# Expose Streamlit default port
EXPOSE 8501

# Optional: lightweight healthcheck for Streamlit
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "ui_lang_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
