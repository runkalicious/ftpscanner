from ftpscanner import FTPScanner

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
    url = 'readyshare'
    #url = 'arnold.c64.org'
    #url = 'ftp.winzip.com'
    
    ftpconn = FTPScanner(url)
    if not ftpconn.is_connected:
        return
    
    # list all files on the server in the root directory
    #files = ftpconn.get_directory_list()
    
    files = []
    depth_first_search(ftpconn, files=files)
    
    for path, f in files:
        print path + '/' + f
    
    ftpconn.close()
    
if __name__ == "__main__":
    main()
