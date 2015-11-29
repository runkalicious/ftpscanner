import sys
from indexer import Indexer
from database import Database

def print_results(num_match, num_return, matches, db):
    '''
    Print the results provided by xapian
    match = {rank=, docid=, text=}
    '''
    for match in matches:
        servername = db.get_server_from_file(match['docid'])
        filename = db.get_full_filepath(match['docid'])
        
        print '\n==================='
        print 'rank=%s, server=%s, file=%s' % (match['rank'], servername, filename)
        print '-------------------'
        print match['text']
        
    print '==================='
    print 'Number of documents matching query: %s' % num_match
    print 'Number of documents returned: %s' % num_return
    print

def main(search_terms):
    dbname = 'ftp_files.db'
    db = Database(dbname)
    
    xname = 'xapian.db'
    corpus = Indexer(xname)
    
    result = corpus.search(str(search_terms))
    print_results(result[0], result[1], result[2], db)
    
    # clean up
    corpus.close()
    db.close()
    
if __name__ == "__main__":
    main(sys.argv[1:])
