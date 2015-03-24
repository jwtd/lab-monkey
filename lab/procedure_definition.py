#!/usr/bin/env python

"""
ProcedureDefinition
"""

from sqlalchemy.orm import mapper, relation, synonym
from orm import Session
from orm.models import lab_assets_table, procedure_definitions_table, procedure_initial_conditions_table, procedure_required_setup_items_table


class LabAsset(object):
    @property
    def identity(self):
        """
        Returns a string containing the manufacturer, model, part code of the asset
        """
        return ('%s %s %s' % (self.manufacturer, self.model, self.part_code)).strip()


class ProcedureDefinition(object): pass
class ProcedureInitialCondition(object): pass
class ProcedureRequiredSetupItem(object): pass

mapper(LabAsset, lab_assets_table)
mapper(ProcedureDefinition, procedure_definitions_table, 
       properties={
       'initial_conditions':relation(ProcedureInitialCondition, cascade="all, delete, delete-orphan"),
       'required_setup_items':relation(LabAsset, secondary = procedure_required_setup_items_table)
})
mapper(ProcedureInitialCondition, procedure_initial_conditions_table)


if __name__ == '__main__':
    pass