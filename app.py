import asyncio
import logging
from datetime import datetime
import time

from google.cloud import bigquery

from clients.bq_client import BQClient
from configurations import configuration
from clients.gsheet_client import GSheetClient
from logger import SheetLogger, LogInfo
from pricing import CrawlerGetter, Product
from services.streaming_service import StreamingService


def run():
    config = configuration.config
    SPREADSHEET_ID = config['DEFAULT']['SPREADSHEET_ID']
    BQ_PROJECT_ID = config['DEFAULT']['BIGQUERY_PROJECT']
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.edit']
    LOGGING_SPREADSHEET_ID =  config['DEFAULT']['LOGGING_SPREADSHEET_ID']
    gsheet_client = GSheetClient(SPREADSHEET_ID, SCOPES)
    bq_client = BQClient(project=BQ_PROJECT_ID)

    streaming_service = StreamingService(bq_client=bq_client, gsheet_client=gsheet_client)
    asyncio.run(streaming_service.populate_prices())


async def empty():
    return None


def setup():
    # file
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='app.log', filemode='a', level=logging.INFO)
    # stdout
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)


def prepare():
    bq_client = BQClient(project=configuration.config['DEFAULT']['BIGQUERY_PROJECT'])
    presync_schem = [
        bigquery.SchemaField("link", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("sale_price", "INT64"),
        bigquery.SchemaField("original_price", "INT64"),
        #bigquery.SchemaField("_updated_at", "TIMESTAMP", mode="REQUIRED"),
        #bigquery.SchemaField("_created_at", "TIMESTAMP", mode="REQUIRED"),
        #bigquery.SchemaField("_date", "DATE", mode="REQUIRED")
    ]
    main_schem = [
        bigquery.SchemaField("link", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("sale_price", "INT64"),
        bigquery.SchemaField("original_price", "INT64"),
        bigquery.SchemaField("_updated_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("_date", "DATE", mode="REQUIRED")
    ]
    bq_client.create_presync_table("pre_sync", "competitor_price", presync_schem)
    #bq_client.create_table("staging", "competitor_price", schema)


if __name__ == "__main__":
    setup()
    #prepare()
    run()
