#!/usr/bin/env python

"""
The main package for the Models module.
"""
import sys
import socket

# Get network properties
np = socket.gethostbyaddr(socket.gethostname())
SERVER_NAME = np[0]
SERVER_IP   = np[-1][0]

# Jordan:    10.99.1.128
# WF Server: 10.99.1.51

from sqlalchemy import __version__, create_engine
from sqlalchemy.orm import sessionmaker

# Database container
try:
    # development, test, production
    container = sys.argv[2]
    if container == 'd':
        container = 'development'
    elif container == 'p':
        container = 'production'
    else:
        container = 'test'
except:
    container = 'test'

# Database Credentials
db_engine   = 'mysql'
db_server   = 'localhost'
db_name     = 'lab_automation_%s' % container
db_username = 'lab_app'
db_password = 'YRYql9e2'

#print 'Connecting to %s on %s (%s) using SQLAlchemy %s' % (db_name, SERVER_NAME, SERVER_IP, __version__) # 0.4.1

# MySQL cnn string
cnn_string = '%s://%s:%s@%s/%s' % (db_engine, db_username, db_password, db_server, db_name)

engine = create_engine(cnn_string, echo=False) # Set echo to True for debugging
Session = sessionmaker(autoflush=True, transactional=True)
