import asyncio
import concurrent
import logging
import time

from typing import List

from clients.bq_client import BQClient
from clients.gsheet_client import GSheetClient
from configurations import configuration
from pricing import CrawlerGetter, Product


class StreamingService:

    def __init__(self, bq_client: BQClient, gsheet_client: GSheetClient):
        self.bq_client = bq_client
        self.gsheet_client = gsheet_client
        self.config = configuration.config

    """
    Standard tables require columns:
    - at least one id column
    - _date: Date (partitioned column)
    - _created_at: Date
    """

    def _get_merge_query(self, source_table, dest_table, id_columns: List[str], columns_update: List[str],
                         columns_insert: List[str]) -> str:
        id_columns_select = ",".join(id_columns)
        ids_matching_stmt = ",".join(map(lambda col: f"T.{col} = S.{col}", id_columns))
        columns_update_stmt = ",".join(map(lambda col: f"T.{col} = S.{col}", columns_update))
        columns_insert_stmt = ",".join(columns_insert)
        columns_insert_assigment_stmt = ",".join(map(lambda col: f"S.{col}", columns_insert))
        merge_sql = f"""
        MERGE {dest_table} T
                USING (SELECT
                agg.table.*
                FROM (
                SELECT
                {id_columns_select},
                ARRAY_AGG(STRUCT(table)
                ORDER BY
                _created_at DESC)[SAFE_OFFSET(0)] agg
                FROM
                {source_table} table
                WHERE
                _date = CURRENT_DATE("+7")
                GROUP BY
                {id_columns_select},
                _date)) S
                ON {ids_matching_stmt}
                WHEN MATCHED THEN
            UPDATE SET {columns_update_stmt}, T._updated_at = CURRENT_TIMESTAMP()
                WHEN NOT MATCHED THEN
            INSERT ({columns_insert_stmt}, _updated_at) VALUES ({columns_insert_assigment_stmt}, CURRENT_TIMESTAMP())
        """
        return merge_sql

    async def populate_prices(self):
        LINK_RANGE_FORMART = self.config['DEFAULT']['LINK_RANGE_FORMART']

        crawler_getter = CrawlerGetter()
        start_index = 2
        STEPS = 20
        valid_products = []

        try:
            while True:
                link_range = LINK_RANGE_FORMART.format(start_index, start_index + STEPS)
                result = self.gsheet_client.get(link_range)
                if not result:
                    break

                tasks = []
                for row in result:
                    if len(row) == 0:
                        tasks.append(asyncio.create_task(self.empty()))
                        continue
                    link = row[0]
                    crawler = crawler_getter.get_crawler(link)
                    tasks.append(asyncio.create_task(crawler.get_price(link)))

                start = time.time()
                products = await asyncio.gather(*tasks, return_exceptions=True)
                end = time.time()
                logging.info(f"parsing html took {end - start}s")
                for product in products:
                    if product is None:
                        pass
                    elif isinstance(product, Product):
                        valid_products.append(product)
                    else:
                        logging.warning(f"product is not recognized {product}")

                start_index += STEPS
        except Exception:
            logging.exception("error while crawling price")

        try:
            self.bq_client.insert_product(dataset="pre_sync", table_name="competitor_price", products=valid_products)
            self.merge_product()
        except Exception:
            logging.exception("error during inserting and merging products")

    def merge_product(self):
        id_columns = ["link"]
        columns_update = ["original_price", "sale_price"]
        columns_insert = ["link", "original_price", "sale_price", "_date"]
        sql = self._get_merge_query(dest_table="`staging.competitor_price`",
                                    source_table="`pre_sync.competitor_price`", id_columns=id_columns,
                                    columns_update=columns_update, columns_insert=columns_insert)
        job = self.bq_client.query(sql)
        logging.info(f"job_id: {job.job_id}")
        try:
            ignored = job.result(timeout=5*60) # wait for 5 mins
            logging.info("merging done")
        except concurrent.futures.TimeoutError:
            logging.warning("getting merge result timed out after 5min")

    async def empty(self):
        return None
