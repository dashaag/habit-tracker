FROM python:3.12.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN pip install uv==0.3.0

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv pip sync uv.lock

# Debugging step to check for alembic executable
RUN ls -l /usr/local/bin

RUN addgroup --system app && adduser --system --ingroup app app

COPY --chown=app:app alembic.ini ./
COPY --chown=app:app persistence ./persistence/
COPY --chown=app:app app ./app/

COPY --chown=app:app docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

USER app

EXPOSE 5001

ENTRYPOINT ["docker-entrypoint.sh"]

CMD []
