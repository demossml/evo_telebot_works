FROM duffn/python-poetry:3.10-slim-1.1.12-2022-01-21
# FROM duffn/python-poetry:3.9-buster-2021-06-25
WORKDIR /app
#COPY pyproject.toml poetry.lock ./
# RUN poetry install
COPY . .
RUN poetry install
CMD ["sh"]

