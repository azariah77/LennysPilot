FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
# Split installs to cache layers individually on unstable networks
RUN pip install --default-timeout=1000 fastapi==0.110.0 uvicorn==0.29.0
RUN pip install --default-timeout=1000 sqlalchemy==2.0.29 psycopg2-binary==2.9.9
RUN pip install --default-timeout=1000 alembic==1.13.1 pgvector==0.2.5
RUN pip install --default-timeout=1000 pydantic==2.6.4 pydantic-settings==2.2.1
RUN pip install --default-timeout=1000 -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
