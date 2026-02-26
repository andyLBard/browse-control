from structured_sources._abstracts import _abstractSourceConnection
import base64, mimetypes, os

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
    def __init__(self, **kwargs):
        dir_path = kwargs.get("dir_path", "*INVALID*PATH*")
        self.is_ready = False
        if os.path.isabs(dir_path) and os.path.isdir(dir_path) and os.path.exists(dir_path):
            self.dir_listing = ["/".join([dir_path, f]) for f in os.listdir(dir_path)]
            self.is_ready = True
        else:
            pass #just stick at not ready until a valid path is passed in.

    def get_query_types(self):
        return ["list_dir", "get_file"]

    #This one will be ignored for file directory, only because the file access is very limited, so
    #the query parsing is intentionally limited
    def prepare_query(self, query_type, **kwargs):
        pass

    def execute_query(self, prepared_query=None, **kwargs):
        if not self.is_ready:
            return "Not ready"
        query = kwargs.get("query","list_dir")
        ret_file = { "mime_type": "text/plain", "full_path": "*INVALID*PATH*", "bindata": "Bad request" }
        if query.startswith("list_dir"):
            return self.dir_listing
        else:
            query_wds = query.split(" ")
            if len(query_wds) == 2:
                file_path = query_wds[1]
                if file_path in self.dir_listing:
                    #try:
                        f = open(file_path, "rb")
                        ret_file["full_path"] = file_path
                        contents = f.read()
                        guess_type = mimetypes.guess_type(file_path)
                        ret_file["mime_type"] = guess_type[0] if guess_type[0] else "text/plain"
                        ret_file["bindata"] = contents
                        f.close()
                    #except:
                    #    ret_file["bindata"] = "Bad filename"
                return ret_file
