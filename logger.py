from datetime import datetime

from clients.gsheet_client import GSheetClient


class SheetLogger:

    def __init__(self, sheet_client, metadata_cell, log_position_range_format):
        self.sheet_client = sheet_client
        self.log_position_range_format = log_position_range_format
        self.metadata_cell = metadata_cell
        self._get_metatdata(metadata_cell)

    def _get_metatdata(self, metadata_cell):
        cell_values = self.sheet_client.get(metadata_cell)
        self.current_row = int(cell_values[0][0], 10)

    def log(self, log_infos):
        if not log_infos:
            return
        ranges = self.log_position_range_format.format(self.current_row, self.current_row + len(log_infos))
        log_infos_array = list(map(LogInfo.to_array, log_infos))
        self.sheet_client.update(ranges, log_infos_array)
        self.current_row += len(log_infos)
        self._commit()

    def _commit(self):
        self.sheet_client.update(self.metadata_cell, [[self.current_row]])


class LogInfo:

    def __init__(self, product_link, err, time):
        self.product_link = product_link
        self.err = err
        self.time = time

    def to_array(self):
        return [self.product_link, self.err, str(self.time)]


if __name__ == '__main__':
    LOGGING_SPREADSHEET_ID="1I9giZ27Sxk0dYAhwp0Y31OXxmzZ78EZj7hZIZzVD9HM"
    LOGGING_LOG_RANGE_FORMAT = "Log!A{}:C{}"
    LOGGING_METADATA_RANGE = "Log!I2:I2"
    gsheet_client = GSheetClient(LOGGING_SPREADSHEET_ID, None)
    sheet_logger = SheetLogger(
            gsheet_client,
            LOGGING_METADATA_RANGE,
            LOGGING_LOG_RANGE_FORMAT
            )
    log_infos = [LogInfo("link1", "error 1", datetime.now())]
    sheet_logger.log(log_infos)

