FROM python:3.8.6

WORKDIR /usr/src/api

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
ENTRYPOINT [ "python", "-u", "./startup.py"]
