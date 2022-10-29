from datetime import datetime, date

from google.cloud import bigquery
from typing import List
import logging

from google.cloud.bigquery import DatasetReference

from pricing import Product


class BQClient:

    def __init__(self, project: str):
        self.project = project
        self.client = bigquery.Client(project=project)

    def create_presync_table(self, dataset: str, table_name: str, schema: List[bigquery.SchemaField]):
        schema.insert(0, bigquery.SchemaField("_created_at", "TIMESTAMP", mode="REQUIRED"))
        schema.insert(0, bigquery.SchemaField("_date", "DATE", mode="REQUIRED"))
        dataset_ref = DatasetReference(project=self.project, dataset_id=dataset)
        table_ref = dataset_ref.table(table_name)
        table = bigquery.Table(table_ref, schema=schema)
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="_date",  # name of column to use for partitioning
            expiration_ms=7*24*60*60*1000, # 7 days
        )
        table = self.client.create_table(table)  # Make an API request.
        logging.log(logging.INFO, "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))

    def create_table(self, dataset: str, table_name: str, schema: List[bigquery.SchemaField]):
        dataset_ref = DatasetReference(project=self.project, dataset_id=dataset)
        table_ref = dataset_ref.table(table_name)
        table = bigquery.Table(table_ref, schema=schema)
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="_date",  # name of column to use for partitioning
        )  # 90 days
        table = self.client.create_table(table)  # Make an API request.

        logging.log(logging.INFO, "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))

    def insert_product(self, dataset: str, table_name: str, products: Product):
        dataset_ref = DatasetReference(project=self.project, dataset_id=dataset)
        table_ref = dataset_ref.table(table_name)
        table = self.client.get_table(table_ref)
        today = date.today()
        current_timestamp = datetime.now()
        rows = []
        for p in products:
            rows.append({"_date": today, "_created_at": current_timestamp, "link": p.link, "original_price": p.original_price, "sale_price": p.sale_price})
        errors = self.client.insert_rows(table=table, rows=rows)

        if not errors:
            logging.info("New rows have been added.")
        else:
            logging.error(f"Encountered errors while inserting rows: {errors}")

    def query(self, sql: str):
        query_job = self.client.query(sql)
        return query_job
