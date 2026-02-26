import sqlalchemy
import pandas as pd
import os
import sys
from enum import Enum
from structured_sources.source_connection import FileDirectory

from structured_sources._abstracts import _abstractSource, _abstractSourceConnection

class LSS_TYPES(Enum):
    CSV_DIR = 1
    XLSX_FILE = 2
    CSV_XLSX_COMBO_DIR = 3
    JSON_FILE = 4
    FILE_DIR = 5

class LocalStructuredSource(_abstractSource):
    def __init__(self, type=LSS_TYPES.FILE_DIR.name):
        self.type = type

    def bootstrap_connection(self, connection_kwargs):
        if self.type == LSS_TYPES.FILE_DIR.name:
            self.source_connection = FileDirectory(**connection_kwargs)
        else:
            self.source_connection = {}

    def get_query_results(self, query={}):
        return self.source_connection.execute_query(**query)







##testiing

#def main():
#    lss = LocalStructuredSource()    

#if __name__=="__main__":
#    main()
