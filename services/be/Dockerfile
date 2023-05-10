# pull official base image
FROM python:3.11.2-slim-buster

# set working directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1  # Prevents Python from writing pyc files to disc
ENV PYTHONUNBUFFERED 1         # Prevents Python from buffering stdout and stderr
ENV POETRY_VERSION=1.0.0

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc \
  && apt-get clean

RUN addgroup --system worker && adduser --system --group worker        # run container processes with a non-root user
COPY --chown=worker:worker be/pyproject.toml be/poetry.lock /app/

# install python dependencies
RUN pip install flake8==6.0.0                                         # poetry throwing error so using pip for flake8
RUN pip install poetry && pip install "poetry==$POETRY_VERSION"
RUN poetry install

# add app
COPY --chown=worker:worker . .
# add entrypoint.sh to ensure Postgres instance being up/running and healthy.
#COPY ./entrypoint.sh /app
#RUN chmod +x /app/entrypoint.sh      #set the execute permission to execute as a program
## run entrypoint.sh
#ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
ENTRYPOINT ["poetry", "run", "python", "-u", "main.py"]