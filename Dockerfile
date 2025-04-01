FROM python:3.11.8
WORKDIR /usr/src
COPY requirements.txt .
RUN python -m pip --no-cache-dir install --requirement requirements.txt && rm requirements.txt
COPY . .
