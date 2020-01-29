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

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval as eval
from odoo.exceptions import ValidationError, UserError, Warning
from datetime import datetime, date, time, timedelta
import random
import string
import logging

_logger = logging.getLogger(__name__)

CONDITION_CODE_TEMP = """# Available locals:
#  - time, date, datetime, timedelta: Python libraries.
#  - env: Odoo Environement.
#  - model: Model of the record on which the action is triggered.
#  - obj: Record on which the action is triggered if there is one, otherwise None.
#  - user, Current user object.
#  - workflow: Workflow engine.
#  - syslog : syslog(message), function to log debug information to Odoo logging file or console.
#  - warning: warning(message), Warning Exception to use with raise.


result = True"""

PYTHON_CODE_TEMP = """# Available locals:
#  - time, date, datetime, timedelta: Python libraries.
#  - env: Odoo Environement.
#  - model: Model of the record on which the action is triggered.
#  - obj: Record on which the action is triggered if there is one, otherwise None.
#  - user, Current user object.
#  - workflow: Workflow engine.
#  - syslog : syslog(message), function to log debug information to Odoo logging file or console.
#  - warning: warning(message), Warning Exception to use with raise.
# To return an action, assign: action = {...}


"""

MODEL_DOMAIN = """[
        ('state', '=', 'base'),
        ('transient', '=', False),
        '!',
        '|',
        '|',
        '|',
        '|',
        '|',
        '|',
        '|',
        ('model', '=ilike', 'res.%'),
        ('model', '=ilike', 'ir.%'),
        ('model', '=ilike', 'odoo.workflow%'),
        ('model', '=ilike', 'bus.%'),
        ('model', '=ilike', 'base.%'),
        ('model', '=ilike', 'base_%'),
        ('model', '=', 'base'),
        ('model', '=', '_unknown'),
    ]"""


class odoo_workflow(models.Model):
    _name = 'odoo.workflow'
    _description = 'Odoo Workflow'

    name = fields.Char(string='Name')
    model_id = fields.Many2one('ir.model', string='Model', domain=MODEL_DOMAIN)
    node_ids = fields.One2many('odoo.workflow.node', 'workflow_id', string='Nodes')
    remove_default_attrs_mod = fields.Boolean(string='Remove Default Attributes & Modifiers', default=True)
    mail_thread_add = fields.Boolean(string='Add Mailthread/Messaging to Model')
    followers_add = fields.Boolean(string='Add Followers to Model')

    _sql_constraints = [
        ('uniq_name', 'unique(name)', _("Workflow name must be unique.")),
        ('uniq_model', 'unique(model_id)', _("Model must be unique.")),
    ]

    @api.constrains('node_ids')
    def validate_nodes(self):
        # Objects
        wkf_node_obj = self.env['odoo.workflow.node']
        for rec in self:
            # Must have one flow start node
            res = rec.node_ids.search_count([
                ('workflow_id', '=', rec.id),
                ('flow_start', '=', True),
            ])
            if res > 1:
                raise ValidationError(_("Workflow must have only one start node."))
            # Nodes' sequence must be unique per workflow
            for node in rec.node_ids:
                res = wkf_node_obj.search_count([
                    ('id', '!=', node.id),
                    ('workflow_id', '=', rec.id),
                    ('sequence', '=', node.sequence),
                ])
                if res:
                    raise ValidationError(_("Nodes' sequence must be unique per workflow."))

    @api.multi
    def btn_reload_workflow(self):
        from odoo.addons import odoo_dynamic_workflow
        return odoo_dynamic_workflow.update_workflow(self)

    @api.multi
    def btn_nodes(self):
        for rec in self:
            act = {
                'name': _('Nodes'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'odoo.workflow.node',
                'domain': [('workflow_id', '=', rec.id)],
                'context': {'default_workflow_id': rec.id},
                'type': 'ir.actions.act_window',
            }
            return act

    @api.multi
    def btn_buttons(self):
        for rec in self:
            act = {
                'name': _('Buttons'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'odoo.workflow.node.button',
                'domain': [('workflow_id', '=', rec.id)],
                'context': {'default_workflow_id': rec.id},
                'type': 'ir.actions.act_window',
            }
            return act

    @api.multi
    def btn_links(self):
        for rec in self:
            act = {
                'name': _('Links'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'odoo.workflow.link',
                'domain': [
                    '|',
                    ('node_from.workflow_id', '=', rec.id),
                    ('node_to.workflow_id', '=', rec.id),
                ],
                'context': {},
                'type': 'ir.actions.act_window',
            }
            return act

class odoo_workflow_node(models.Model):
    _name = 'odoo.workflow.node'
    _description = 'Odoo Workflow Nodes'
    _order = 'sequence'

    name = fields.Char(string='Name', translate=True)
    node_name = fields.Char(string='Technical Name')
    sequence = fields.Integer(string='Sequence', default=10)
    flow_start = fields.Boolean(string='Flow Start')
    flow_end = fields.Boolean(string='Flow End')
    is_visible = fields.Boolean(string='Appear in Statusbar', default=True)
    out_link_ids = fields.One2many('odoo.workflow.link', 'node_from', string='Outgoing Transitions')
    in_link_ids = fields.One2many('odoo.workflow.link', 'node_to', string='Incoming Transitions')
    field_ids = fields.One2many('odoo.workflow.node.field', 'node_id', string='Fields')
    button_ids = fields.One2many('odoo.workflow.node.button', 'node_id', string='Buttons')
    workflow_id = fields.Many2one('odoo.workflow', string='Workflow Ref.', ondelete='cascade', required=True)
    model_id = fields.Many2one('ir.model', string='Model Ref.', related='workflow_id.model_id', required=True)

    @api.onchange('name')
    def _compute_node_name(self):
        for rec in self:
            if rec and rec.name:
                name = rec.name.lower().strip().replace(' ', '_')
                rec.node_name = name

    @api.multi
    def btn_load_fields(self):
        # Variables
        field_obj = self.env['ir.model.fields']
        for rec in self:
            # Clear Fields List
            rec.field_ids.unlink()
            # Load Fields
            fields = field_obj.search([('model_id', '=', rec.model_id.id)])
            for field in fields:
                rec.field_ids.create({
                    'model_id': rec.model_id.id,
                    'node_id': rec.id,
                    'name': field.id,
                })

class odoo_workflow_link(models.Model):
    _name = 'odoo.workflow.link'
    _description = 'Odoo Workflow Links'

    name = fields.Char(string='Name')
    condition_code = fields.Text(string='Condition Code', default=CONDITION_CODE_TEMP)
    node_from = fields.Many2one('odoo.workflow.node', 'Source Node', ondelete='cascade', required=True)
    node_to = fields.Many2one('odoo.workflow.node', 'Destination Node', ondelete='cascade', required=True)

    @api.constrains('node_from', 'node_to')
    def check_nodes(self):
        for rec in self:
            if rec.node_from == rec.node_to:
                raise ValidationError(_("Sorry, source & destination nodes can't be the same."))

    @api.onchange('node_from', 'node_to')
    def onchange_nodes(self):
        for rec in self:
            if rec.node_from and rec.node_to:
                rec.name = "%s -> %s" % (rec.node_from.name, rec.node_to.name)

    @api.multi
    def trigger_link(self):
        # Variables
        cx = self.env.context
        model_name = cx.get('active_model')
        rec_id = cx.get('active_id')
        model_obj = self.env[model_name].sudo()
        rec = model_obj.browse(rec_id)
        # Validation
        if rec.state == self.node_from.node_name:
            rec.state = self.node_to.node_name
        return True

class odoo_workflow_node_button(models.Model):
    _name = 'odoo.workflow.node.button'
    _description = 'Odoo Workflow Node Buttons'
    _order = 'sequence'

    def _generate_key(self):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

    name = fields.Char(string='Button String', translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    is_highlight = fields.Boolean(string='Is Highlighted', default=True)
    has_icon = fields.Boolean(string='Has Icon')
    icon = fields.Char(string='Icon')
    btn_key = fields.Char(string='Button Key', default=_generate_key)
    btn_hide = fields.Boolean(string="Hide Button if Condition isn't fulfilled")
    condition_code = fields.Text(string='Condition Code', default=CONDITION_CODE_TEMP)
    action_type = fields.Selection([
        ('link', 'Trigger Link'),
        ('code', 'Python Code'),
        ('action', 'Server Action'),
        ('win_act', 'Window Action'),
    ], string='Action Type', default='link')
    link_id = fields.Many2one('odoo.workflow.link', string='Link')
    code = fields.Text(string='Python Code', default=PYTHON_CODE_TEMP)
    server_action_id = fields.Many2one('ir.actions.server', string='Server Action')
    win_act_id = fields.Many2one('ir.actions.act_window', string='Window Action')
    node_id = fields.Many2one('odoo.workflow.node', string='Workflow Node Ref.', ondelete='cascade', required=True)
    workflow_id = fields.Many2one('odoo.workflow', string='Workflow Ref.', required=True)

    @api.onchange('node_id')
    def change_workflow(self):
        for rec in self:
            if isinstance(rec.id, int) and rec.node_id and rec.node_id.workflow_id:
                rec.workflow_id = rec.node_id.workflow_id.id
            elif self.env.context.get('default_node_id', 0):
                model_id = self.env['odoo.workflow.node'].sudo().browse(
                    self.env.context.get('default_node_id')).model_id.id
                rec.workflow_id = self.env['odoo.workflow'].sudo().search([('model_id', '=', model_id)])

    @api.constrains('btn_key')
    def validation(self):
        for rec in self:
            # Check if there is no duplicate button key
            res = self.search_count([
                ('id', '!=', rec.id),
                ('btn_key', '=', rec.btn_key),
            ])
            if res:
                rec.btn_key = self._generate_key()

    @api.multi
    def run(self):
        for rec in self:
            # Check Condition Before Executing Action
            result = False
            cx = self.env.context.copy() or {}
            locals_dict = {
                'env': self.env,
                'model': self.env[cx.get('active_model', False)],
                'obj': self.env[cx.get('active_model', False)].browse(cx.get('active_id', 0)),
                'user': self.env.user,
                'datetime': datetime,
                'time': time,
                'date': date,
                'timedelta': timedelta,
                'workflow': self.env['odoo.workflow'],
                'warning': self.warning,
                'syslog': self.syslog,
            }
            try:
                eval(rec.condition_code, locals_dict=locals_dict, mode='exec', nocopy=True)
                result = 'result' in locals_dict and locals_dict['result'] or False
            except ValidationError as ex:
                raise ex
            except SyntaxError as ex:
                raise UserError(_("Wrong python code defined.\n\nError: %s\nLine: %s, Column: %s\n\n%s" % (
                ex.args[0], ex.args[1][1], ex.args[1][2], ex.args[1][3])))
            if result:
                # Run Proper Action
                func = getattr(self, "_run_%s" % rec.action_type)
                return func()

    @api.multi
    def _run_win_act(self):
        # Variables
        cx = self.env.context.copy() or {}
        win_act_obj = self.env['ir.actions.act_window']
        # Run Window Action
        for rec in self:
            action = win_act_obj.with_context(cx).browse(rec.win_act_id.id).read()[0]
            action['context'] = cx
            return action
        return False

    @api.multi
    def _run_action(self):
        # Variables
        srv_act_obj = self.env['ir.actions.server']
        # Run Server Action
        for rec in self:
            srv_act_rec = srv_act_obj.browse(rec.server_action_id.id)
            return srv_act_rec.run()

    @api.multi
    def _run_code(self):
        # Variables
        cx = self.env.context.copy() or {}
        locals_dict = {
            'env': self.env,
            'model': self.env[cx.get('active_model', False)],
            'obj': self.env[cx.get('active_model', False)].browse(cx.get('active_id', 0)),
            'user': self.env.user,
            'datetime': datetime,
            'time': time,
            'date': date,
            'timedelta': timedelta,
            'workflow': self.env['odoo.workflow'],
            'warning': self.warning,
            'syslog': self.syslog,
        }
        # Run Code
        for rec in self:
            try:
                eval(rec.code, locals_dict=locals_dict, mode='exec', nocopy=True)
                action = 'action' in locals_dict and locals_dict['action'] or False
                if action:
                    return action
            except Warning as ex:
                raise ex
            except SyntaxError as ex:
                raise UserError(_("Wrong python code defined.\n\nError: %s\nLine: %s, Column: %s\n\n%s" % (ex.args[0], ex.args[1][1], ex.args[1][2], ex.args[1][3])))
        return True

    @api.multi
    def _run_link(self):
        for rec in self:
            # Check Condition Before Executing Action
            result = False
            cx = self.env.context.copy() or {}
            locals_dict = {
                'env': self.env,
                'model': self.env[cx.get('active_model', False)],
                'obj': self.env[cx.get('active_model', False)].browse(cx.get('active_id', 0)),
                'user': self.env.user,
                'datetime': datetime,
                'time': time,
                'date': date,
                'timedelta': timedelta,
                'workflow': self.env['odoo.workflow'],
                'warning': self.warning,
                'syslog': self.syslog,
            }
            try:
                eval(rec.link_id.condition_code, locals_dict=locals_dict, mode='exec', nocopy=True)
                result = 'result' in locals_dict and locals_dict['result'] or False
            except ValidationError as ex:
                raise ex
            except SyntaxError as ex:
                raise UserError(_("Wrong python code defined.\n\nError: %s\nLine: %s, Column: %s\n\n%s" % (
                ex.args[0], ex.args[1][1], ex.args[1][2], ex.args[1][3])))
            if result:
                # Trigger link function
                return rec.link_id.trigger_link()

    def warning(self, msg):
        if not isinstance(msg, (str, unicode)):
            msg = str(msg)
        raise Warning(msg)

    def syslog(self, msg):
        if not isinstance(msg, (str, unicode)):
            msg = str(msg)
        _logger.info(msg)

class odoo_workflow_node_field(models.Model):
    _name = 'odoo.workflow.node.field'
    _description = 'Odoo Workflow Node Fields'

    name = fields.Many2one('ir.model.fields', string='Field')
    model_id = fields.Many2one('ir.model', string='Model')
    readonly = fields.Boolean(string='Readonly')
    required = fields.Boolean(string='Required')
    invisible = fields.Boolean(string='Invisible')
    group_ids = fields.Many2many('res.groups', string='Groups')
    user_ids = fields.Many2many('res.users', string='Users')
    node_id = fields.Many2one('odoo.workflow.node', string='Node Ref.', ondelete='cascade', required=True)
