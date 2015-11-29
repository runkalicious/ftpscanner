import xapian

class Indexer:
    __db = None
    __indexer = None
    
    __server_idx = 0
    __filepath_idx = 1
    __filename_idx = 2
    
    def __init__(self, dbname):
        self.__db = xapian.WritableDatabase(dbname, xapian.DB_CREATE_OR_OPEN)
        
        self.__indexer = xapian.TermGenerator()
        self.__indexer.set_stemmer(xapian.Stem('english'))
    
    def flush(self):
        if self.__db is not None:
            self.__db.flush()
            
    def add_content(self, server, fileid, filepath, filename, fcontent):
        with open(fcontent) as fd:
            content = fd.read()
        
        # Prepare document
        document = xapian.Document()
        document.set_data(content)
        
        # Store metadata
        document.add_value(self.__server_idx, server)
        document.add_value(self.__filepath_idx, filepath)
        document.add_value(self.__filename_idx, filename)
        
        # Index document
        self.__indexer.set_document(document)
        self.__indexer.index_text(content)
        
        self.__db.replace_document(fileid, document)

    