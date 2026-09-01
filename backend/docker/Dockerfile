FROM python:3.13-slim

RUN useradd \
    --create-home \
    --shell /bin/bash \
    atlas

RUN mkdir /app && chown atlas:atlas /app

WORKDIR /app

COPY --chown=atlas:atlas requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=atlas:atlas backend ./backend
COPY --chown=atlas:atlas client ./client
COPY --chown=atlas:atlas README.md .

USER atlas
CMD ["python", "-u", "-c", "print('START', flush=True); from sentence_transformers import SentenceTransformer; print('IMPORT OK', flush=True); model=SentenceTransformer('all-MiniLM-L6-v2'); print('MODEL OK', flush=True)"]