import ftplib
import socket
import tempfile

class FTPScanner:
    __conn = None
    is_connected = False
    
    def __init__(self, siteurl, port=21):
        try:
            self.__conn = ftplib.FTP()
            self.__conn.connect(siteurl, port)
            self.__conn.login() # user anonymous, passwd anonymous@
            self.__conn.set_pasv(False)
            self.is_connected = True
            
        except ftplib.error_perm as e:
            print "Server Error (%s): %s" % (siteurl, e)
            
        except socket.error as e:
            print e
        
    def close(self):
        if self.__conn is not None:
            self.__conn.quit()
            self.is_connected = False
    
    def get_welcome(self):
        if self.__conn is not None:
            return self.__conn.getwelcome()
        return ""
    
    def change_working_dir(self, path):
        if self.__conn is not None:
            self.__conn.cwd(path)
        
    def get_directory_list(self):
        if self.__conn is None:
            return []
        
        dirs = []
        
        def append_dirs_mlsd(item):
            parts = item.split(';')
            filename = parts[-1]
            for part in parts:
                if part.startswith('type') and part.split('=')[-1] == 'dir':
                    dirs.append(filename.strip())
        
        def append_dirs(item):
            if item.startswith('d'):
                parts = item.split()
                if parts[-1] not in ['.', '..']:
                    dirs.append(' '.join(parts[8:]))
        
        try:
            try:
                self.__conn.retrlines('MLSD', append_dirs_mlsd)
            except ftplib.error_perm as e:
                # MLSD likely not supported, fallback to LIST
                self.__conn.retrlines('LIST', append_dirs)
        except ftplib.error_temp as e:
            print e
            
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
            try:
                self.__conn.retrlines('NLIST', files.append)
            except ftplib.error_perm as e:
                # NLIST likely not supported, fallback to LIST
                self.__conn.retrlines('LIST', append_files)
        except ftplib.error_temp as e:
            print e
        
        return files

    def download_file(self, filepath, binary=True):
        if self.__conn is None:
            return None
        
        if filepath.startswith('/'):
            filepath = filepath[1:]
        
        try:
            if binary:
                tmp = tempfile.NamedTemporaryFile(mode='w+b', delete=False)
                self.__conn.retrbinary('RETR ' + filepath, tmp.write)
            else:
                tmp = tempfile.NamedTemporaryFile(mode='w+', delete=False)
                self.__conn.storlines('RETR ' + filepath, tmp.write)
                
        except ftplib.error_temp as e:
            print e
            
        except ftplib.error_perm as e:
            print e
        
        tmpname = tmp.name
        tmp.close()
        
        return tmpname
