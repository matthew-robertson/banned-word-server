FROM python:3

WORKDIR /usr/src/api

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "-u", "./startup.py"]