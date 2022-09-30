FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./cache_model.py /code/cache_model.py

# first for downloading and aching the torch models
# second so 🤗 models cache is moved to the new place
RUN python cache_model.py
RUN python cache_model.py

COPY ./app.py /code/app.py

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
