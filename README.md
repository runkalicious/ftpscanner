# ftpscanner
Scans open FTP servers and indexes their contents

## Requirements
- Xapian with python bindings: http://xapian.org/download

## Usage
### Indexing FTP Servers
scanner.py -f \<ftp sites\> [-p \<prefixes\>] [-d \<database\>] [-x \<xapian\>] [-v]

\- Required \-  
\-f \<ftp sites\>  
  The name of the newline-delimited file of FTP server addresses

\- Optional -  
\-p \<prefixes\>  
  The name of the newline-delimited file of URL prefixes. Default: prefix.conf  
  
\-d \<database\>  
  Determines the name of the database (or filename with sqlite). Default: ftp_files.db  
  
\-x \<xapian\>  
  Determines the name of the xapian database to use or create. Default: xapian.db  
  
\-v  
  Enables verbose logging

### Searching Indexed Files
searcher.py \<search terms\>

\- Required \-  
\<search terms\>  
  Any number of keywords to find within the text files indexed by the scanner
