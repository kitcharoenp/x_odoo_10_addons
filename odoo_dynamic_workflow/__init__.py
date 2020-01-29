# -*- coding: utf-8 -*-
##########################################################
###                 Disclaimer                         ###
##########################################################
### Lately, I started to get very busy after I         ###
### started my new position and I couldn't keep up     ###
### with clients demands & requests for customizations ###
### & upgrades, so I decided to publish this module    ###
### for community free of charge. Building on that,    ###
### I expect respect from whoever gets his/her hands   ###
### on my code, not to copy nor rebrand the module &   ###
### sell it under their names.                         ###
##########################################################

import re
import models
import wizards
from odoo import api, modules
from odoo.models import BaseModel, check_pg_name
from odoo.tools import OrderedSet, LastOrderedSet

# Backup original function for any later use
_build_model_old = BaseModel._build_model

regex = r"^_unknown$|odoo\.workflo.+|res\..+|ir\..+" + \
        "|bus\..+|base\..+|base\_.+|^base$"


def update_workflow(self):
    """
    Updates Odoo model and registry to apply new workflow changes.
    :return:
    """
    # Variables
    wkf_obj = self.env['odoo.workflow'].sudo()
    t_models = [model.model for model in wkf_obj.search([]).mapped('model_id')]
    # Update
    self.env.cr.commit()
    api.Environment.reset()
    reg = modules.registry.Registry.new(self.env.cr.dbname, update_module=True)
    reg.init_models(self.env.cr, t_models, {})
    self.env.cr.commit()
    # Reload client
    return {
        'type': 'ir.actions.client',
        'tag': 'reload',
    }

def inherit_workflow_manager(cr, model):
    """
    This method inherits new workflow engine
    if assigned for current model.

    :param cr: Database cursor
    :param model: Current model instance
    :return: List of inherited models
    """

    # Variables
    model_name = model._name
    is_transient = model._transient
    is_abstract = model._abstract
    parents = model._inherit
    parents = [parents] if isinstance(parents, basestring) else (parents or [])
    if isinstance(model_name, str):
        # Check model
        if not re.match(regex, model_name) and not is_transient and not is_abstract:
            # Validate that workflow table created in database
            sql = """SELECT EXISTS (
SELECT 1 FROM information_schema.tables 
WHERE table_schema = 'public' 
AND   table_name = 'odoo_workflow');"""
            cr.execute(sql)
            res = cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                # Check for model's workflow
                sql = """SELECT * FROM odoo_workflow wkf, ir_model im 
WHERE wkf.model_id = im.id 
AND   im.model = '%s';""" % model_name
                cr.execute(sql)
                for rec in cr.dictfetchall():
                    # Apply inheritance
                    if rec.get('model', False) == model_name:
                        if 'odoo.workflow.model' not in parents:
                            if hasattr(model, 'state'):
                                delattr(model, 'state')
                            parents.insert(0, 'odoo.workflow.model')
                        if rec.get('mail_thread_add', False):
                            if 'mail.thread' not in parents:
                                parents.append('mail.thread')
                            if 'ir.needaction_mixin' not in parents:
                                parents.append('ir.needaction_mixin')
    return parents

# Monkey Patched _build_model method
@classmethod
def _build_model_new(cls, pool, cr):
    """ Instantiate a given model in the registry.

        This method creates or extends a "registry" class for the given model.
        This "registry" class carries inferred model metadata, and inherits (in
        the Python sense) from all classes that define the model, and possibly
        other registry classes.

    """

    # Keep links to non-inherited constraints in cls; this is useful for
    # instance when exporting translations
    cls._local_constraints = cls.__dict__.get('_constraints', [])
    cls._local_sql_constraints = cls.__dict__.get('_sql_constraints', [])

    # determine inherited models
    parents = inherit_workflow_manager(cr, cls)
    parents = [parents] if isinstance(parents, basestring) else (parents or [])

    # determine the model's name
    name = cls._name or (len(parents) == 1 and parents[0]) or cls.__name__

    # all models except 'base' implicitly inherit from 'base'
    if name != 'base':
        parents = list(parents) + ['base']

    # create or retrieve the model's class
    if name in parents:
        if name not in pool:
            raise TypeError("Model %r does not exist in registry." % name)
        ModelClass = pool[name]
        ModelClass._build_model_check_base(cls)
        check_parent = ModelClass._build_model_check_parent
    else:
        ModelClass = type(name, (BaseModel,), {
            '_name': name,
            '_register': False,
            '_original_module': cls._module,
            '_inherit_children': OrderedSet(),  # names of children models
            '_inherits_children': set(),  # names of children models
            '_fields': {},  # populated in _setup_base()
        })
        check_parent = cls._build_model_check_parent

    # determine all the classes the model should inherit from
    bases = LastOrderedSet([cls])
    for parent in parents:
        if parent not in pool:
            raise TypeError("Model %r inherits from non-existing model %r." % (name, parent))
        parent_class = pool[parent]
        if parent == name:
            for base in parent_class.__bases__:
                bases.add(base)
        else:
            check_parent(cls, parent_class)
            bases.add(parent_class)
            parent_class._inherit_children.add(name)
    ModelClass.__bases__ = tuple(bases)

    # determine the attributes of the model's class
    ModelClass._build_model_attributes(pool)

    check_pg_name(ModelClass._table)

    # Transience
    if ModelClass._transient:
        assert ModelClass._log_access, \
            "TransientModels must have log_access turned on, " \
            "in order to implement their access rights policy"

    # link the class to the registry, and update the registry
    ModelClass.pool = pool
    pool[name] = ModelClass

    # backward compatibility: instantiate the model, and initialize it
    model = object.__new__(ModelClass)
    model.__init__(pool, cr)

    return ModelClass

BaseModel._build_model = _build_model_new
