import os
from ftpscanner import FTPScanner
from database import Database
from indexer import Indexer

def enumerate_files(ftp_server_uri, database):
    '''
    Connect to a remote public FTP server and enumerate all files present.
    This uses a depth-first approach to finding all files.
    All items founds are recorded in the provided database.
    
    Returns True if successful, otherwise False
    '''
    def depth_first_search(ftpconn, path="", files=[]):
        dirs = ftpconn.get_directory_list()
        for d in dirs:
            path += "/" + d
            ftpconn.change_working_dir(d)
            
            depth_first_search(ftpconn, path, files)
            
            path = '/'.join(path.split('/')[:-1])
            ftpconn.change_working_dir('../')
            
        curr_files = ftpconn.get_file_list()
        for f in curr_files:
            files.append((path, f))

    # Connect to the remote server
    ftpconn = FTPScanner(ftp_server_uri)
    if not ftpconn.is_connected:
        return False
    
    # Get welcome banner, if any
    welcome = "" #TODO
    
    # Record server and get server id
    sid = database.add_server(ftp_server_uri, "")
    
    # Map all files on the server
    files = []
    depth_first_search(ftpconn, files=files)
    
    # Store all found files in our local database
    for path, f in files:
        database.add_file(sid, path, f)
    
    ftpconn.close()
    return True
    
def index_content(ftp_server_uri, indexer, database):
    '''
    Connects to a remote public FTP server and downloads all text files.
    This assumes the server was already catalogued previously. The contents
    of the downloaded files are loaded into the xapian corpus for indexing.
    
    Returns True if successful, otherwise False
    '''
    # Connect to the remote server
    ftpconn = FTPScanner(ftp_server_uri)
    if not ftpconn.is_connected:
        return False
    
    for id, path, fname in database.get_files_for_server(ftp_server_uri):
        if fname.endswith('.txt'):
            tmp = ftpconn.download_file(path + '/' + fname)
            indexer.add_content(ftp_server_uri, id, path, fname, tmp)
            os.remove(tmp)
    
    indexer.flush()
    ftpconn.close()
    return True
    
def main(dbname='ftp_files.db', xname='xapian.db'):
    '''
    Main method: dispatches tasks to catalogue and index remote FTP servers.
    '''
    db = Database(dbname)
    indexer = Indexer(xname, writeable=True)
    
    # test ftp servers
    url = 'readyshare'
    #url = 'arnold.c64.org'
    #url = 'ftp.winzip.com'
    
    # Record all files on a remote server
    if not enumerate_files(url, db):
        print "Could not enumerate files on %s" % url
    
    # Download text and add to corpus
    if not index_content(url, indexer, db):
        print "Could not index %s" % url
    
    # cleanup
    indexer.close()
    db.close()
    
if __name__ == "__main__":
    main()
