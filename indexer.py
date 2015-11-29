import xapian
from textmachine import TextMachine

class Indexer:
    '''
    Text Indexer built on xapian. 
    It supports updating the corpus and querying for values

    A lot of this is based on an incredibly useful article at:
    http://invisibleroads.com/tutorials/xapian-search-pylons.html
    '''
    __db = None
    __indexer = None
    __queryparser = None
    
    __server_idx = 0
    __filepath_idx = 1
    __filename_idx = 2
    
    def __init__(self, dbname, writeable=False):
        if writeable:
            self.__db = xapian.WritableDatabase(dbname, xapian.DB_CREATE_OR_OPEN)
            
            self.__indexer = xapian.TermGenerator()
            self.__indexer.set_stemmer(xapian.Stem('english'))
        
        else:
            self.__db = xapian.Database(dbname)
            
        self.__queryparser = xapian.QueryParser()
        self.__queryparser.set_stemmer(xapian.Stem('english'))
        self.__queryparser.set_database(self.__db)
        self.__queryparser.set_stemming_strategy(xapian.QueryParser.STEM_SOME)
    
    def flush(self):
        if self.__db is not None:
            self.__db.flush()
    
    def close(self):
        if self.__db is not None:
            if type(self.__db) is xapian.WritableDatabase:
                self.__db.flush()
            self.__db.close()
    
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

    def search(self, searchterm, extractlength=32):
        # Parse query string
        query = self.__queryparser.parse_query(searchterm)
        
        # Set offset and limit for pagination
        offset, limit = 0, self.__db.get_doccount()
        
        # Start query session
        enquire = xapian.Enquire(self.__db)
        enquire.set_query(query)
        
        # Display matches
        matches = enquire.get_mset(offset, limit)
        
        results = []
        for match in matches:
            content = match.document.get_data()
            extract = TextMachine(extractlength, '*%s*').process(searchterm, content)
            
            result = {
                "rank": match.rank,
                "docid": match.docid,
                "text": extract
            }
            
            results.append(result)
        
        return (matches.get_matches_estimated(), matches.size(), results)
