import sqlite3

class Database:
    __conn = None
    __cursor = None
    
    def __init__(self, db):
        self.__conn = sqlite3.connect(db)
        if self.__conn is not None:
            self.__cursor = self.__conn.cursor()
            self.__setup()
    
    def __setup(self):
        if self.__cursor is None:
            return
            
        self.__cursor.execute('create table if not exists server \
            (id integer primary key, uri text, welcome text)')
        self.__cursor.execute('create table if not exists file \
            (id integer primary key, serverid integer, path text, \
            filename text, unique(serverid, path, filename) on conflict ignore)')
    
    def close(self):
        self.__cursor = None
        if self.__conn is not None:
            self.__conn.close()

    def add_server(self, uri, welcome_msg):
        '''
        Insert a new FTP server address, if it doesn't exist.
        Return the server id of the already existing server or the newly added one.
        '''
        if self.__cursor is None:
            return
        
        server_id = self.get_server_id(uri)
        if server_id is None:
            self.__cursor.execute('insert into server values (NULL, ?, ?)', (uri, welcome_msg))
            self.__conn.commit()
            return self.__cursor.lastrowid
        
        return server_id
    
    def get_server_id(self, uri):
        if self.__cursor is None:
            return None
            
        self.__cursor.execute('select rowid from server where uri=?', (uri,))
        id = self.__cursor.fetchone()
        return None if (id is None) else id[0]
    
    def get_server_from_file(self, fid):
        if self.__cursor is None:
            return None
            
        self.__cursor.execute('select uri from server join file on server.id=file.serverid where file.id=?', (fid,))
        row = self.__cursor.fetchone()
        return None if (row is None) else row[0]
        
    def add_file(self, serverid, filepath, filename):
        if self.__cursor is None:
            return
            
        self.__cursor.execute('insert into file values (NULL, ?, ?, ?)', (serverid, filepath, filename))
        self.__conn.commit()
        return self.__cursor.lastrowid
    
    def get_full_filepath(self, fid):
        if self.__cursor is None:
            return None
            
        self.__cursor.execute('select path, filename from file where file.id=?', (fid,))
        row = self.__cursor.fetchone()
        ret = None
        if row is not None:
            ret = row[0] + '/' + row[1]
        return ret
    
    def get_files_for_server(self, uri):
        if self.__cursor is None:
            return []
            
        sid = self.get_server_id(uri)
        if sid is None:
            return []
        
        self.__cursor.execute('select id, path, filename from file where serverid=?', (sid,))
        return self.__cursor.fetchall()
