from ftpscanner import FTPScanner

def main():
    url = 'ftp.winzip.com'
    
    ftpconn = FTPScanner(url)
    if not ftpconn.is_connected:
        return
    
    # list all files on the server in the root directory
    files = ftpconn.get_directory_list()
    
    for f in files:
        print f
    
    ftpconn.close()
    

if __name__ == "__main__":
    main()
