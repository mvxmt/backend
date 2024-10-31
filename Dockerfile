FROM python:3.12

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
    
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install && rm -rf $POETRY_CACHE_DIR

COPY . /app

EXPOSE 8000
ENTRYPOINT ["poetry", "run", "python", "main.py"]