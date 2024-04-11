FROM python:3.11

#
WORKDIR /code

#
ADD ./.env /code/.env

#
COPY ./requirements.txt /code/requirements.txt

#
COPY ./requirements_dev.txt /code/requirements_dev.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements_dev.txt

#
COPY ./app /code/app

#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]