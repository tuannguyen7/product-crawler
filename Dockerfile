FROM python:3.9.13
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install -r requirements.txt
COPY app.ini ./
COPY setenv.sh ./
COPY entrypoint.sh ./
COPY product-crawler-service-account.json ./
RUN chmod +x ./setenv.sh ./entrypoint.sh
COPY . .
ENTRYPOINT ["./entrypoint.sh"]
