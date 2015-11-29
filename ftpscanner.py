import ftplib
import socket

class FTPScanner:
    __conn = None
    is_connected = False
    
    def __init__(self, siteurl, port=21):
        try:
            self.__conn = ftplib.FTP()
            self.__conn.connect(siteurl, port)
            self.__conn.login() # user anonymous, passwd anonymous@
            self.is_connected = True
            
        except ftplib.error_perm as e:
            print "Server Error (%s): %s" % (siteurl, e)
            
        except socket.error as e:
            print e
        
    def close(self):
        if self.__conn is not None:
            self.__conn.quit()
            self.is_connected = False
        
    def change_working_dir(self, path):
        if self.__conn is not None:
            self.__conn.cwd(path)
        
    def get_directory_list(self):
        if self.__conn is None:
            return []
        
        dirs = []
        
        def append_dirs_mlsd(item):
            parts = item.split(';')
            if parts[-1] not in ['.', '..']:
                dirs.append(parts[-1].trim())
        
        def append_dirs(item):
            if item.startswith('d'):
                parts = item.split()
                if parts[-1] not in ['.', '..']:
                    dirs.append(' '.join(parts[8:]))
        
        try:
            self.__conn.retrlines('MLSD', append_dirs_mlsd)
        except ftplib.error_perm as e:
            # MLSD likely not supported, fallback to LIST
            self.__conn.retrlines('LIST', append_dirs)
            
        return dirs
        
    def get_file_list(self):
        if self.__conn is None:
            return []
        
        files = []
        
        def append_files(item):
            if not item.startswith('d'):
                parts = item.split()
                files.append(' '.join(parts[8:]))
        
        try:
            self.__conn.retrlines('NLIST', files.append)
        except ftplib.error_perm as e:
            # NLIST likely not supported, fallback to LIST
            self.__conn.retrlines('LIST', append_files)
        
        return files
