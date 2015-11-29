import os, sys, getopt
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
    welcome = ftpconn.get_welcome()
    
    # Record server and get server id
    sid = database.add_server(ftp_server_uri, welcome)
    
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
    
def main(flist, dbname='ftp_files.db', xname='xapian.db', verbose=False):
    '''
    Main method: dispatches tasks to catalogue and index remote FTP servers.
    '''
    db = Database(dbname)
    indexer = Indexer(xname, writeable=True)
    
    # Read list of remote FTP servers
    servers = []
    with open(flist) as f:
        servers = f.read().splitlines()
    
    for server in servers:
        if verbose: print "Scanning: %s" % server
        
        # Record all files on a remote server
        if not enumerate_files(server, db):
            print "Could not enumerate files on %s" % server
        
        # Download text and add to corpus
        if not index_content(server, indexer, db):
            print "Could not index %s" % server
    
    if verbose: print "\nCataloguing and indexing complete."
    
    # cleanup
    indexer.close()
    db.close()

def help():
    '''
    Prints script help documentation
    '''
    print 'scanner.py -f <ftp sites> [-d <database>] [-x <xapian>] [-v]'
    print
    print '- Required -'
    print '-f <ftp sites>'
    print '\tThe name of the newline-delimited file of FTP server addresses'
    print
    print '- Optional -'
    print '-d <database>'
    print '\tDetermines the name of the database (or filename with sqlite). Default: ftp_files.db'
    print '-x <xapian>'
    print '\tDetermines the name of the xapian database to use or create. Default: xapian.db'
    print '-v'
    print '\tEnables verbose logging'
    print
    
if __name__ == "__main__":
    params = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:],'hf:d:x:v',['ftpservers=','database=','xapian='])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ('-f', '--ftpservers'):
            params['flist'] = arg
        elif opt in ('-d', '--database'):
            params['dbname'] = arg
        elif opt in ('-x', '--xapian'):
            params['xname'] = arg
        elif opt == '-v':
            params['verbose'] = True
    
    if 'flist' not in params:
        print "You must specify a file containing FTP server addresses!"
        sys.exit(1)
    
    main(**params)
