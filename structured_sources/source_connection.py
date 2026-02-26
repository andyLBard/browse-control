from _abstracts import _abstractSourceConnection

#CSV_DIR, creates a sql db with one table per csv file in a directory
class CSVDirectory(_abstractSourceConnection):
    pass

#XLSX_FILE, creates a sql db with one table per worksheet in an excel workbook.
class XLSXFile(_abstractSourceConnection):
    pass

#CSV_XLSX_COMBO_DIR, a combination of both above, keeping both in one db
class ComboDirectory(_abstractSourceConnection):
    pass

#JSON_FILE, pulls a json file into pandas and allows queries into the resulting pandas dataframe
class JSONFile(_abstractSourceConnection):
    pass

#FILE_DIR, allows file listing of a specific directory, or retrieving full or partial file contents.
class FileDirectory(_abstractSourceConnection):
    pass
