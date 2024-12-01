FROM python:3.12-slim
RUN mkdir /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . /app
WORKDIR /app
CMD [ "python3", "./timekpr-next-web.py"]
