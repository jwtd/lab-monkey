import sys
import datetime
import time

from common.base import *

from sqlalchemy import Table, Column, UniqueConstraint, Integer, String, DateTime, Date, Time, Boolean, MetaData, func, ForeignKey
from sqlalchemy.orm import mapper, relation

from orm import engine

REBUILD = False
arg_rebuild = False
try:
    if int(sys.argv[1]) == 1:
        arg_rebuild = True
except:
    pass

# Get ready to specify a Table's metadata
metadata = MetaData()

# Bind the metadata to the engine to allow direct operations
metadata.bind = engine


# Dimensions
dimensions_table = Table('dimensions', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False),
    Column('name_aliases', String(100)),
    Column('weight', Integer, nullable=False, default=0),
    Column('best_worst', String(200))
)

# Dimension Values
dimension_values_table = Table('dimension_values', metadata,
    Column('id', Integer, primary_key=True),
    Column('dimension_id', Integer, ForeignKey('dimensions.id')),
    Column('value', String(100), nullable=False),
    Column('value_aliases', String(100)),
    Column('default', Boolean, nullable=False, default=False)
)



# Specifications
procedure_definitions_table = Table('specifications', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False),
    Column('description', String(), nullable=False),
    Column('document', String(255)),
    Column('created_at', DateTime, default  = func.now()),
    Column('updated_at', DateTime, onupdate = func.current_timestamp()),
    UniqueConstraint('name', 'file')
)

# Specification Tests
procedure_definitions_table = Table('specification_tests', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False),
    Column('description', String(), nullable=False),
    Column('pass_condition', String()),
    Column('created_at', DateTime, default  = func.now()),
    Column('updated_at', DateTime, onupdate = func.current_timestamp()),
    UniqueConstraint('name', 'file')
)

# Procedure assignments for specification tests
procedure_required_setup_items_table = Table('specification_test_procedures', metadata,
    Column('specification_id', Integer, ForeignKey('specifications.id')),                      
    Column('procedure_definition_id', Integer, ForeignKey('procedure_definitions.id')),
)




# Procedure Definitions
procedure_definitions_table = Table('procedure_definitions', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False),
    Column('description', String(), nullable=False),
    Column('file', String(255), nullable=False),
    Column('class_name', String(100), nullable=False),
    Column('module_name', String(255), nullable=False),
    Column('last_modified_rev', Integer, nullable=False),  
    Column('created_at', DateTime, default  = func.now()),
    Column('updated_at', DateTime, onupdate = func.current_timestamp()),
    UniqueConstraint('name', 'file')
)

# Procedure initial conditions
procedure_initial_conditions_table = Table('procedure_initial_conditions', metadata,
    Column('id', Integer, primary_key=True),
    Column('procedure_definition_id', Integer, ForeignKey('procedure_definitions.id')),
    Column('variable_name', String(100), nullable=False)
)
# Procedure required items
procedure_required_setup_items_table = Table('procedure_required_setup_items', metadata,
    Column('procedure_definition_id', Integer, ForeignKey('procedure_definitions.id')),
    Column('lab_asset_id', Integer, ForeignKey('lab_assets.id'))
)

# Lab Assets
lab_assets_table = Table('lab_assets', metadata,
    Column('id', Integer, primary_key=True),
    Column('manufacturer', String(100), nullable=False),
    Column('model', String(100), nullable=False),
    Column('type', String(100)),
    Column('part_code', String(30)),
    Column('asset_class', String(100)),
    Column('created_at', DateTime, default  = func.now()),
    Column('updated_at', DateTime, onupdate = func.current_timestamp())
)




# Data Requests
data_requests_table = Table('data_requests', metadata,
    Column('id', Integer, primary_key=True),
    Column('created_by', String(100), nullable=False),
    Column('type', String(100), nullable=False),
    Column('subject', String(50), nullable=False),
    Column('initial_conditions', String()),
    Column('execution_status', Integer, nullable=False, default=-1), # TODO: Add notes - Pending, Gated, On Hold, Complete
    Column('priority', Integer, nullable=False, default=0),
    Column('deadline', DateTime),
    Column('estimated_completion_date', DateTime),
    Column('created_at', DateTime, default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    Column('updated_at', DateTime, onupdate=func.current_timestamp())
)

# Data Request Dimension Values
data_request_dimension_values_table = Table('data_request_dimension_values', metadata,
    Column('dimension_value_id', Integer, ForeignKey('dimension_values.id')),
    Column('data_request_id', Integer, ForeignKey('data_requests.id')),
    UniqueConstraint('dimension_value_id', 'data_request_id')
)






# Data Request Elements
data_request_elements_table = Table('data_request_elements', metadata,
    Column('id', Integer, primary_key=True),
    Column('data_request_id', Integer, ForeignKey('data_requests.id')),
    Column('lab_job_id', Integer, ForeignKey('lab_jobs.id')),    
    Column('procedure_definition_id', Integer, ForeignKey('procedure_definitions.id')),
    Column('environmental_requierments', String(100)),
    Column('execution_status', Integer, nullable=False, default=-1), # TODO: Add notes - Pending, Gated, On Hold, Complete
    Column('priority', Integer, nullable=False, default=0)
)

# Data Request Element Dimension Values
data_request_element_dimension_values_table = Table('data_request_element_dimension_values', metadata,
    Column('dimension_value_id', Integer, ForeignKey('dimension_values.id')),
    Column('data_request_element_id', Integer, ForeignKey('data_request_elements.id'))
)

# Data Request Initial Conditions
data_request_element_initial_conditions_table = Table('data_request_element_initial_conditions', metadata,
    Column('id', Integer, primary_key=True),
    Column('data_request_element_id', Integer, ForeignKey('data_request_elements.id')),
    Column('procedure_initial_condition_id', Integer, ForeignKey('procedure_initial_conditions.id')),    
    Column('value', String(100))
)




# Lab Jobs
lab_jobs_table = Table('lab_jobs', metadata,
    Column('id', Integer, primary_key=True),
    Column('procedure_definition_id', Integer, ForeignKey('procedure_definitions.id')),
    Column('environmental_requierments', String(100)),
    Column('execution_status', Integer, nullable=False, default=-1), # TODO: Add notes - Pending, Gated, On Hold, Complete
    Column('priority', Integer, nullable=False, default=0),
    Column('urgency_weight', Integer, nullable=False, default=0),
    Column('by_pass_count', Integer, nullable=False, default=0),
    Column('initial_condition_hash', String(), nullable=False), # TODO: Figure out how to establish identity
    Column('estimated_start_date', Date),
    Column('estimated_start_time', Time)
)



# Event Notification Subscriptions
event_notification_subscriptions_table = Table('event_notification_subscriptions', metadata,
    Column('id', Integer, primary_key=True),
    Column('subject', String(100), nullable=False),
    Column('subject_id', Integer, nullable=False),
    Column('events', String(200), nullable=False),
    Column('user_id', String(100), nullable=False),
    Column('user_email', String(100), nullable=False),
    Column('user_im', String(50)),
    Column('user_phone', String(20)),
    Column('user_sms', String(20)),
    Column('created_at', DateTime, default  = func.now()),
    Column('updated_at', DateTime, onupdate = func.current_timestamp())
)





if REBUILD or arg_rebuild:
    # Rebuild Tables
    engine.execute('SET FOREIGN_KEY_CHECKS=0;') # http://sql-info.de/mysql/referential-integrity.html
    metadata.drop_all()
    metadata.create_all()
    engine.execute('SET FOREIGN_KEY_CHECKS=1;')
    
    # Load initial data
    f = open(exepath('sql/initial_data.sql'))
    try:
        for line in f:
            sql = line.strip()
            if len(sql):
                engine.execute(str(sql))
    finally:
        f.close()
    print 'Rebuilt DB'
