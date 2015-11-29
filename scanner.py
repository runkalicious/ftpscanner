import os
from ftpscanner import FTPScanner
from database import Database
from indexer import Indexer

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

def main():
    dbname = 'ftp_files.db'
    xname = 'xapian.db'
    db = Database(dbname)
    indexer = Indexer(xname, writeable=True)
    
    # test ftp servers
    url = 'readyshare'
    #url = 'arnold.c64.org'
    #url = 'ftp.winzip.com'
    
    ftpconn = FTPScanner(url)
    if not ftpconn.is_connected:
        return
    
    # Record server and get server id
    sid = db.add_server(url, "")
    
    # Map all files on the server
    files = []
    depth_first_search(ftpconn, files=files)
    
    # Store all found files in our local database
    for path, f in files:
        db.add_file(sid, path, f)
    
    for id, path, fname in db.get_files_for_server(url):
        if fname.endswith('.txt'):
            tmp = ftpconn.download_file(path + '/' + fname)
            indexer.add_content(url, id, path, fname, tmp)
            os.remove(tmp)
    
    indexer.flush()
    
    # cleanup
    indexer.close()
    ftpconn.close()
    db.close()
    
if __name__ == "__main__":
    main()
