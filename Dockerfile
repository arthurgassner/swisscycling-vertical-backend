FROM python:3.12-slim-bookworm

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY main.py /code/main.py

CMD ["fastapi", "run", "main.py", "--port", "80"]