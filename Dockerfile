FROM python:3.11.3 AS pre

WORKDIR /opt/kazoo

RUN python -m pip install poetry

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry export --without-hashes --format requirements.txt --output requirements.txt

FROM python:3.11.3 AS prod

WORKDIR /opt/kazoo

COPY --from=pre /opt/kazoo/requirements.txt .
COPY app ./app

RUN python -m pip install --no-cache-dir --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt install -y ffmpeg
RUN rm -rf /var/lib/apt/lists/*

RUN rm requirements.txt

ENV BOT_TOKEN="your.bot.token"
ENV BOT_CACHE_DIR="/opt/kazoo/cache"
ENV BOT_PREFIX="&"

CMD ["python3", "-m", "app"]
