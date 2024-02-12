FROM python:3-slim

RUN useradd -m python
USER python

COPY --chown=python . /app
WORKDIR /app

RUN pip install --user --upgrade pip
RUN pip install --user -r requirements.txt
RUN pip install --user gunicorn
ENV PATH="/home/python/.local/bin:$PATH"

CMD ["gunicorn", "-b", "0.0.0.0:8000", "status_dwarf:create_app()"]
EXPOSE 8000
