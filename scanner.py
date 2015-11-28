import ftplib
import socket

def main():
    url = 'ftp.winzip.com'
    
    ftpconn = open_ftp_connection(url)
    if ftpconn == None:
        return
    
    # list all files on the server in the root directory
    ftpconn.retrlines('LIST')
    
    ftpconn.quit() # close connection
    
def open_ftp_connection(siteurl, port=21):
    try:
        conn = ftplib.FTP()
        conn.connect(siteurl, port)
        conn.login() # user anonymous, passwd anonymous@
        return conn
        
    except ftplib.error_perm as e:
        print "Server Error (%s): %s" % (siteurl, e)
        
    except socket.error as e:
        print "Server timeout"
        
    return None
    
if __name__ == "__main__":
    main()
