FROM python:3.12.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install uv==0.3.0

# Create and activate a virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

# Sync dependencies into the activated virtual environment
RUN uv pip sync uv.lock

# Debugging step to check for alembic executable in the venv
RUN ls -l /opt/venv/bin

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
