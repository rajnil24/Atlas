FROM python:3.13-slim

RUN useradd \
    --create-home \
    --shell /bin/bash \
    atlas
RUN mkdir /app && chown atlas:atlas /app
WORKDIR /app
USER atlas