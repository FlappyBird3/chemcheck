FROM python:3.12-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /home/user/app

COPY --chown=user . .
RUN pip install --no-cache-dir ".[api]"

EXPOSE 8000
CMD ["sh", "-c", "python -m uvicorn chemcheck.api:app --host 0.0.0.0 --port ${PORT:-8000}"]