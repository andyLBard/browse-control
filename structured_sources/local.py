import sqlalchemy
import pandas as pd
import io
import sys
from enum import Enum

from _abstracts import _abstractSource, _abstractSourceConnection

class LSS_TYPES(Enum):
    CSV_DIR = 1
    XLSX_FILE = 2
    CSV_XLSX_COMBO_DIR = 3
    JSON_FILE = 4
    FILE_DIR = 5

class LocalStructuredSource(_abstractSource):
    def __init__(self, type=LSS_TYPES.CSV_DIR.name, **connection_kwargs):
        pass

    def bootstrap_connection(self):
        pass

    def get_query_results(self, query):
        pass







##testiing

if __name__=="__main__":
    lss = LocalStructuredSource()
