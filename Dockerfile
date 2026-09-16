# ---- Build stage ----
FROM python:3.12-slim AS builder
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Final stage ----
FROM python:3.12-slim
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser static/ static/
RUN chown appuser:appuser /app
ENV PATH="/opt/venv/bin:$PATH"
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/todos')" || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]