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
CMD ["python", "-u", "-c", "print('START', flush=True); import backend.agent.agent; print('AGENT OK', flush=True)"]