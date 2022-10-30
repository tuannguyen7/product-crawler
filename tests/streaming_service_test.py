import unittest
from services.streaming_service import StreamingService


class StreamingServiceTest(unittest.TestCase):

    def test_merge_stmt(self):
        s = StreamingService(None, None)
        id_columns = ["link"]
        columns_update = ["original_price", "sale_price"]
        columns_insert = ["link", "original_price", "sale_price", "_date"]
        merge_stmt = s._get_merge_query(dest_table="`staging.competitor_price`", source_table="`pre_sync.competitor_price`", id_columns=id_columns, columns_update=columns_update, columns_insert=columns_insert)
        print(merge_stmt)