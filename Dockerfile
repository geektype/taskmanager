# Use Python 3.13 slim as base image
FROM python:3.13-slim

# Install Chrome and required dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1) \
    && echo "Chrome version: $CHROME_VERSION" \
    && CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_VERSION") \
    && echo "ChromeDriver version: $CHROMEDRIVER_VERSION" \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip" \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf chromedriver-linux64.zip chromedriver-linux64

# Set up working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set display for Chrome
ENV DISPLAY=:99

# Create a script to run both Flask and tests
RUN echo '#!/bin/bash\n\
# Start Xvfb\n\
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &\n\
\n\
# Start Flask in the background\n\
python app.py > flask.log 2>&1 &\n\
\n\
# Wait for Flask to start\n\
for i in {1..30}; do\n\
    if curl -s http://localhost:5000 > /dev/null; then\n\
        break\n\
    fi\n\
    if [ $i -eq 30 ]; then\n\
        echo "Flask failed to start"\n\
        exit 1\n\
    fi\n\
    sleep 1\n\
done\n\
\n\
# Run tests\n\
python -m unittest tests/test_task_manager.py\n\
\n\
# Get Flask process ID and kill it\n\
FLASK_PID=$(ps aux | grep "python app.py" | grep -v grep | awk "{print \$2}")\n\
if [ ! -z "$FLASK_PID" ]; then\n\
    kill $FLASK_PID\n\
fi\n\
' > /app/run_tests.sh && chmod +x /app/run_tests.sh

# Command to run tests
CMD ["/app/run_tests.sh"] 