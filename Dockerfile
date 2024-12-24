FROM python:3.12 AS base
WORKDIR /opt/poetry
RUN python3 -m venv .
ENV PATH="/opt/poetry/bin:$PATH"
RUN pip install --upgrade pip && pip install poetry==1.8.3
RUN poetry --version

WORKDIR /src
RUN python3 -m venv --copies /venv
RUN /venv/bin/pip install --upgrade pip wheel
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml ./

RUN --mount=type=cache,sharing=locked,target=/var/cache/apt \
    --mount=type=cache,sharing=locked,target=/var/lib/apt \
    apt-get update && apt-get install -yqq libdbus-1-dev libglib2.0-dev

RUN poetry export -f requirements.txt -o requirements-base.txt
RUN grep 'git\+' requirements-base.txt > requirements-vcs.txt || test $? = 1
RUN grep 'git\+' -v requirements-base.txt > requirements-hashed.txt || test $? = 1
RUN /venv/bin/pip install --no-deps -r requirements-vcs.txt
RUN /venv/bin/pip install -r requirements-hashed.txt
FROM base AS dev

FROM python:3.12-slim
RUN --mount=type=cache,sharing=locked,target=/var/cache/apt \
    --mount=type=cache,sharing=locked,target=/var/lib/apt \
    apt-get update && apt-get install -yqq libglib2.0-bin libdbus-1-3
ENV PATH="/venv/bin:$PATH" PYTHONUNBUFFERED=1 VIRTUAL_ENV="/venv"
COPY --from=base /venv /venv
RUN mkdir /app
COPY . /app
WORKDIR /app
CMD [ "python3", "./timekpr-next-web.py"]