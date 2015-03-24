#!/usr/bin/env python

"""
LabManager
"""
import os
import re
import glob
import logging.config

if os.name =='nt':
    import win32pipe
elif os.name =='posix':
    from subprocess import Popen
    from subprocess import PIPE

from common.base import *
from orm import Session

logging.config.fileConfig(exepath('../logging_config.txt'))

PROCEDURE_REPOSITORY_PATH = exepath('../procedures/repository')
RE_PROCEDURE_NAME = re.compile(r'class\s*(\w+?)\(Procedure\):')
RE_COMPRESS = re.compile(r'[\n ]+')

def run_cmd(cmd):
    """
    Executes the supplied command on the OS and returns an 
    array of the lines that the command returned.
    """
    if os.name =='nt':
        f = win32pipe.popen(cmd)
    elif os.name =='posix':
        f = Popen(cmd.split(), stdout=PIPE).communicate()[0]
        f = f.split('\n')
    return f

def svn_update(filepath):
    """Runs SVN update on the designated filepath."""
    # http://svnbook.red-bean.com/en/1.1/re28.html
    cmd = 'svn update %s' % filepath
    run_cmd(cmd)

def svn_last_modified_revision(filepath):
    """
    Returns an integer coresponding to the 'Last Changed Revision' of 
    the item at the designated filepath.
    """
    cmd = 'svn info %s' % filepath
    for line in run_cmd(cmd):
        if 'Not a versioned resource' in line:
            return 0
        m = re.match(r'Last Changed Rev:\s(\d*)', line.strip())
        if m:
            return int(m.group(1))
    return 0

def retrieve_procedure_class_name(filepath):
    """
    Parses a procedure file, extracting metadata, which is then 
    stored in the procedure repository.
    """
    # Get the data from the file and close ASAP
    f = open(filepath)
    try:
        procedure_name = None
        lines=open(filepath, 'rU').readlines()
        for line in lines:
            m = re.match(RE_PROCEDURE_NAME, line)
            if m:
                procedure_name = m.group(1)
                break
    finally:
        f.close()

    return procedure_name


from lab.procedure_definition import LabAsset, ProcedureDefinition, ProcedureInitialCondition, ProcedureRequiredSetupItem

class LabManager(object):
    """
    Controls the activities of a lab.
    """

    def __init__(self):
        """Creates a LabManager object"""
        self.log = logging.getLogger('root')

    def update_procedure_definitions(self):
        """
        Performs an inspection of the procedure repository, and 
        updates the procedure_definitions in the database.
        """
        dbs = Session()

        # Create a reference to lookup existing procedures
        procedure_ref = {}
        stored_procedures = dbs.query(ProcedureDefinition).all()
        for procedure in stored_procedures:
            procedure_ref[procedure.name.upper()] = procedure

        # Create a reference to lookup existing assets
        lab_assets_ref = {}
        stored_assets = dbs.query(LabAsset).all()
        for asset in stored_assets:
            lab_assets_ref[asset.identity] = asset

        # Get an inventory of the procedure repository
        detected_procedures = self.inspect_procedure_repository()

        # Reconcile the inventory against the records in the database
        for procedure in detected_procedures:
            key = procedure['name'].upper()
            if procedure_ref.has_key(key):
                # Procedure found in database, check for changes
                p = procedure_ref[key]
                if procedure['last_modified_rev'] > p.last_modified_rev:
                    # Changes, detected, so update
                    p.name              = procedure['name']
                    p.description       = procedure['description']
                    p.file              = procedure['file']
                    p.class_name        = procedure['class_name']
                    p.module_name       = procedure['module_name']
                    p.last_modified_rev = procedure['last_modified_rev']

                    # Check that existing required values are still required, delete if not
                    for ic in p.initial_conditions:
                        if ic.variable_name not in procedure['required_values']:
                            dbs.delete(ic)
                        else:
                            procedure['required_values'].remove(ic.variable_name)

                    # Add new values
                    for value in procedure['required_values']:
                        ic = ProcedureInitialCondition()
                        ic.variable_name = value
                        p.initial_conditions.append(ic)

                    # Check that existing required items are still required, delete if not
                    for ri in p.required_setup_items:
                        if ri.identity not in procedure['required_setup']:
                            p.required_setup_items.remove(ri)
                        else:
                            procedure['required_setup'].remove(ri.identity)

                    # Add new values
                    for item in procedure['required_setup']:
                        if lab_assets_ref.has_key(item):
                            if lab_assets_ref[item] not in p.required_setup_items:
                                ri = lab_assets_ref[item]
                                p.required_setup_items.append(ri)
                        else:
                            raise ValueError("Unknown asset '%s' required for %s procedure." % (item, p.name))

                    dbs.update(p)
                    dbs.commit()
                else:
                    # No changes
                    pass
            else:
                # New procedure
                p = ProcedureDefinition()
                p.name              = procedure['name']
                p.description       = procedure['description']
                p.file              = procedure['file']
                p.class_name        = procedure['class_name']
                p.module_name       = procedure['module_name']
                p.last_modified_rev = procedure['last_modified_rev']

                for value in procedure['required_values']:
                    ic = ProcedureInitialCondition()
                    ic.variable_name = value
                    p.initial_conditions.append(ic)
                
                for item in procedure['required_setup']:
                    if lab_assets_ref.has_key(item):
                        ri = lab_assets_ref[item]
                    else:
                        raise ValueError("Unknown asset '%s' required for %s procedure." % (item, p.name))
                    p.required_setup_items.append(ri)

                dbs.save(p)
                dbs.commit()

        dbs.close()

    def inspect_procedure_repository(self):
        """
        Loops over all of the python files located in the 
        procedures/repository directory, looking for new procedures.
        If a new procedure is found, it is inspected and inserted into
        the procedure repository.
        """
        # Run SVN Update to get new files
        svn_update(PROCEDURE_REPOSITORY_PATH)

        procedures = []

        # Loop over each file, and check files under version control
        files = glob.glob('%s/*.py' % PROCEDURE_REPOSITORY_PATH)
        for filepath in files:

            # If the file is under version control, inspect it
            last_modified_ver = svn_last_modified_revision(filepath)
            if last_modified_ver > 0:
                # Retrieve the procedure name
                procedure_class_name = retrieve_procedure_class_name(filepath)                
                
                # If the name is present, import the module and collect the prodcedure's metadata
                if procedure_class_name:
                    # Import
                    module_name = os.path.basename(filepath).split('.')[0]
                    p = __import__('procedures.repository.%s' % module_name)
                    
                    # Get a reference to the class level attributes
                    klass_atts = []
                    exec('klass_atts = p.repository.%s.%s.__dict__' % (module_name, procedure_class_name))
                    
                    # Collect the necesary values
                    metadata = {}
                    metadata['name']             = klass_atts.get('name')
                    metadata['required_values']  = klass_atts.get('required_values')
                    metadata['required_setup']   = klass_atts.get('required_setup')
                    doc = klass_atts.get('__doc__', '').strip()
                    metadata['description'] = re.sub(RE_COMPRESS, ' ', doc)
                    metadata['file']             = filepath
                    metadata['class_name']       = procedure_class_name
                    metadata['module_name']      = 'procedures.repository.%s' % module_name
                    metadata['last_modified_rev']= last_modified_ver

                    procedures.append(metadata)
                
        # Return all of the identified procedures
        return procedures


if __name__ == '__main__':
    #lm = LabManager()
    #lm.update_procedure_definitions()
    pass