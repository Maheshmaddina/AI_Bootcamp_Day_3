# Trip Buddy (lesson 15: agent + MCP server + A2A Local Guide)
# Runs on any container host (e.g. the AWS EC2 server); listens on port 8080.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv
WORKDIR /app

# Install the exact versions from uv.lock, but with the small CPU-only PyTorch
# (the default Linux PyTorch pulls in ~4 GB of GPU libraries we don't need).
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-hashes --no-emit-project \
      | grep -v -E '^(nvidia-|triton|cuda-)' > requirements.txt \
 && uv pip install --system --no-cache --torch-backend cpu -r requirements.txt

# Download the embedding model now, so the app starts fast and needs no download at runtime
ENV HF_HOME=/app/hf_cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" \
 && chmod -R a+rwX /app/hf_cache   # lets the app run as a normal (non-root) user too

COPY *.py start.sh ./
RUN chmod +x start.sh

# The model is already saved inside the image, so never contact Hugging Face at runtime
ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

# Gradio listens on all interfaces, port 8080
ENV GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=8080 \
    PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["./start.sh"]
