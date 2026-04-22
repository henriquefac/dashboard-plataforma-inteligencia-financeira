FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy the project configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy the application code
COPY app ./app

# Expose the port
EXPOSE 8501

# Set environment variables
ENV PYTHONPATH=.

# Command to run the application
CMD ["uv", "run", "streamlit", "run", "app/main.py", "--server.address", "0.0.0.0"]
