FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY agent_app.py /app/
COPY agent_lib.py /app/

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost/_stcore/health || exit 1

ENTRYPOINT [ "streamlit", "run", "agent_app.py", \
             "--logger.level", "info", \
             "--browser.gatherUsageStats", "false", \
             "--browser.serverAddress", "0.0.0.0", \
             "--server.enableCORS", "false", \
             "--server.enableXsrfProtection", "false", \
             "--server.port", "80"]
