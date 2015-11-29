import xapian

class Indexer:
    __db = None
    __indexer = None
    
    __filename_idx = 0
    
    def __init__(self, dbname):
        self.__db = xapian.WritableDatabase(dbname, xapian.DB_CREATE_OR_OPEN)
        
        self.__indexer = xapian.TermGenerator()
        self.__indexer.set_stemmer(xapian.Stem('english'))
    
    def flush(self):
        if self.__db is not None:
            self.__db.flush()
            
    def add_content(self, fileid, filename, content):
        # Prepare document
        document = xapian.Document()
        document.set_data(content)
        
        # Store metadata
        fileName = os.path.basename(filePath)
        document.add_value(self.__filename_idx, filename)
        
        # Index document
        self.__indexer.set_document(document)
        self.__indexer.index_text(content)
        
        self.__db.replace_document(fileid, document)
