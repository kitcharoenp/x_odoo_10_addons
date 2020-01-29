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
from odoo.osv.orm import setup_modifiers
from odoo.tools.safe_eval import safe_eval as eval
from odoo.exceptions import UserError, Warning
from datetime import datetime, date, time, timedelta
from lxml import etree
import logging

_logger = logging.getLogger(__name__)


class odoo_workflow_model(models.Model):
    _name = 'odoo.workflow.model'
    _description = 'Odoo Workflow Model'

    @api.model
    def _compute_default_state(self):
        # Objects
        wkf_obj = self.env['odoo.workflow']
        rec_model = self._name
        # Get Flow Start
        wkf_recs = wkf_obj.search([('model_id', '=', rec_model)])
        for wkf_rec in wkf_recs:
            for node in wkf_rec.node_ids:
                if node.flow_start:
                    return node.node_name

    @api.model
    def _load_state(self):
        # Objects
        wkf_obj = self.env['odoo.workflow']
        # Variables
        rec_model = self._name
        ret = []
        # Get Status
        wkf_recs = wkf_obj.search([('model_id', '=', rec_model)])
        for rec in wkf_recs:
            for node in rec.node_ids:
                ret.append((node.node_name, node.name))
        return ret

    state = fields.Selection(selection='_load_state', string='Status', default=_compute_default_state, track_visibility='onchange')

    @api.multi
    def btn_exec_action(self):
        """
            Got invoked when a workflow button is called.
            :return: button action return value.
        """
        # Variables
        cx = self.env.context.copy() or {}
        cx.update({'active_id': self.id, 'active_ids': self.ids})
        wkf_btn_obj = self.env['odoo.workflow.node.button']
        btn_rec = wkf_btn_obj.search([('btn_key', '=', cx.get('btn_key', False))])
        if btn_rec:
            return btn_rec.with_context(cx).run()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        # Code Start
        res = super(odoo_workflow_model, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type in ['tree', 'form']:
            if res.get('fields', False):
                res = self._remove_default_header(view_type, res)
                res = self._remove_default_modifiers(view_type, res)
                res = self._load_buttons_view(view_type, res)
                res = self._load_state_view(view_type, res)
                res = self._update_fields_view(view_type, res)
                res = self._add_state_tree_view(view_type, res)
                res = self._add_mail_thread_view(view_type, res)
        return res

    def _remove_default_header(self, view_type, res):
        """
            Removes default header element from form view.
            :param view_type: Type of view now rendering.
            :param res: View resource data.
            :return: Updated view resource.
        """
        # Variables
        arch = etree.XML(res['arch'])
        # Find Default Header Element & Remove it
        if view_type == 'form':
            header_el = arch.xpath("//form/header")
            header_el = header_el[0] if header_el else False
            if header_el is not False:
                header_el.getparent().remove(header_el)
        res['arch'] = etree.tostring(arch, encoding="utf-8")
        return res

    def _remove_default_modifiers(self, view_type, res):
        """
            Removed fields default modifiers & attributes in form view.
            :param view_type: Type of view now rendering.
            :param res: View resource data.
            :return: Updated view resource.
        """
        # Variables
        model = self._name
        wkf_obj = self.env['odoo.workflow']
        wkf_rec = wkf_obj.search([('model_id', '=', model)])
        arch = etree.XML(res['arch'])
        # Validation
        if not wkf_rec.remove_default_attrs_mod:
            return res
        # Find Field & Remove Modifiers
        if view_type == 'form':
            for field in arch.iter("field"):
                field_name = field.attrib.get('name', False)
                if not field_name:
                    continue
                for attr in field.attrib.keys():
                    if attr != 'name':
                        field.attrib.pop(attr)
        res['arch'] = etree.tostring(arch, encoding="utf-8")
        return res

    def _load_buttons_view(self, view_type, res):
        """
            Adds buttons to state bar in form view.
            :param view_type: Type of view now rendering.
            :param res: View resource data.
            :return: Updated view resource.
        """
        # Variables
        this = self
        model = self._name
        wkf_obj = self.env['odoo.workflow']
        arch = etree.XML(res['arch'])
        # Helper Functions
        def _check_condition_code(btn):
            locals_dict = {
                'env': this.env,
                'model': this.env[model],
                'obj': None,
                'user': this.env['res.users'].browse(this.env.uid),
                'datetime': datetime,
                'time': time,
                'date': date,
                'timedelta': timedelta,
                'workflow': this.env['odoo.workflow'],
                'warning': this.warning,
                'syslog': this.syslog,
            }
            try:
                eval(btn.condition_code, locals_dict=locals_dict, mode='exec', nocopy=True)
                result = 'result' in locals_dict and locals_dict['result'] or False
                return result
            except Warning as ex:
                raise ex
            except:
                raise UserError(_("Wrong python condition defined."))
        #
        if view_type == 'form':
            # Get Some Elements
            form_el = arch.xpath("//form")
            form_el = form_el[0] if form_el else False
            header_el = arch.xpath("//form/header")
            header_el = header_el[0] if header_el else False
            # Create Header Element If not Exists
            if not header_el:
                header_el = etree.Element('header')
                form_el.insert(0, header_el)
            # Construct Buttons & Fields Tags
            wkf_rec = wkf_obj.search([('model_id', '=', model)])
            for node in wkf_rec.node_ids:
                for button in node.button_ids:
                    # Check Condition Code
                    if button.btn_hide:
                        if not _check_condition_code(button):
                            continue
                    # Add Button to View
                    btn_exec_action_el = etree.SubElement(header_el, "button")
                    btn_exec_action_el.set('name', 'btn_exec_action')
                    btn_exec_action_el.set('string', button.name)
                    btn_exec_action_el.set('type', 'object')
                    if button.is_highlight:
                        btn_exec_action_el.set('class', 'oe_highlight')
                    if button.has_icon:
                        btn_exec_action_el.set('icon', button.icon)
                    btn_exec_action_el.set('attrs', "{'invisible':[('state','!=','%s')]}" % node.node_name)
                    btn_exec_action_el.set('context', "{'btn_key':'%s','active_model':'%s'}" % (button.btn_key, self._name))
                    setup_modifiers(btn_exec_action_el)
            res['arch'] = etree.tostring(arch, encoding="utf-8")
        return res

    def _load_state_view(self, view_type, res):
        """
            Adds state bar to form view.
            :param view_type: Type of view now rendering.
            :param res: View resource data.
            :return: Updated view resource.
        """
        # Variables
        wkf_obj = self.env['odoo.workflow']
        model = self._name
        model_obj = self.env[model]
        visible_seq = []
        arch = etree.XML(res['arch'])
        wkf_rec = wkf_obj.search([('model_id', '=', model)])
        # Helper Functions
        def _add_field_def_to_view(resource, field_name, field_node):
            resource['fields'].update(model_obj.fields_get(allfields=[field_name]))
            setup_modifiers(field_node, resource['fields'][field_name])
        #
        if view_type == 'form':
            # Get Header Element
            header_el = arch.xpath("//form/header")
            header_el = header_el[0] if header_el else False
            # Create State Element If not Exists
            if header_el is not False:
                state_el = etree.Element('field')
                state_el.set('name', 'state')
                state_el.set('widget', 'statusbar')
                # Loop all nodes
                for node in wkf_rec.node_ids:
                    # Read Visible States
                    if node.is_visible:
                        visible_seq.append(node.node_name)
                # Set Attributes & Setup Modifiers for State Field
                if visible_seq:
                    state_el.set('statusbar_visible', ','.join(visible_seq))
                _add_field_def_to_view(res, 'state', state_el)
                header_el.append(state_el)
        res['arch'] = etree.tostring(arch, encoding="utf-8")
        return res

    def _update_fields_view(self, view_type, res):
        """
            Updates fields attributes.
            :param view_type: Type of view now rendering.
            :param res: View resource data.
            :return: Updated view resource.
        """
        # Objects
        wkf_obj = self.env['odoo.workflow']
        user_obj = self.env['res.users']
        # Variables
        model = self._name
        uid = self._uid
        wkf_rec = wkf_obj.search([('model_id', '=', model)])
        arch = etree.XML(res['arch'])
        # Helper Functions
        def _get_external_id(group):
            arr = []
            ext_ids = group._get_external_ids()
            for ext_id in ext_ids:
                arr.append(ext_ids[ext_id][0])
            return arr
        # Read fields of view
        for field in res['fields']:
            # Get Fields Instance
            field_inst = arch.xpath("//field[@name='%s']" % str(field))
            field_inst = field_inst[0] if field_inst else False
            # Scope Variables
            readonly_arr = []
            required_arr = []
            invisible_arr = []
            readonly_domain = []
            required_domain = []
            invisible_domain = []
            attrs_dict = {}
            # Loop all nodes
            for node in wkf_rec.node_ids:
                # Loop Other Nodes
                for field_attrs in node.field_ids:
                    # Record all states for each attribute
                    if field_inst is not False and field_attrs.name.name == field_inst.attrib['name']:
                        flag_show = True
                        if field_attrs.readonly:
                            readonly_arr.append(node.node_name)
                        if field_attrs.required:
                            required_arr.append(node.node_name)
                        if field_attrs.invisible:
                            invisible_arr.append(node.node_name)
                        # Check Users & Groups
                        if field_attrs.user_ids:
                            user_rec = user_obj.browse(uid)
                            if user_rec not in field_attrs.user_ids:
                                flag_show = False
                        if field_attrs.group_ids:
                            has_group = False
                            user_rec = user_obj.browse(uid)
                            ext_ids = _get_external_id(field_attrs.group_ids)
                            for ext_id in ext_ids:
                                has_group = user_rec.has_group(ext_id)
                            if not has_group:
                                flag_show = False
                        if not flag_show and (field_attrs.group_ids or field_attrs.user_ids):
                                invisible_arr.append(node.node_name)
            # Construct XML attribute
            if readonly_arr:
                readonly_domain.append(('state', 'in', readonly_arr))
                attrs_dict.update({'readonly': readonly_domain})
            if required_arr:
                required_domain.append(('state', 'in', required_arr))
                attrs_dict.update({'required': required_domain})
            if invisible_arr:
                invisible_domain.append(('state', 'in', invisible_arr))
                attrs_dict.update({'invisible': invisible_domain})
            # Set Attributes & Setup Modifiers
            if field_inst is not False and attrs_dict:
                field_inst.set('attrs', str(attrs_dict))
                setup_modifiers(field_inst, res['fields'][str(field)])
        res['arch'] = etree.tostring(arch, encoding="utf-8")
        return res

    def _add_state_tree_view(self, view_type, res):
        """
            Adds state field to tree view.
            :param view_type: Type of view now rendering.
            :param res: View resource data.
            :return: Updated view resource.
        """
        # Variables
        model = self._name
        model_obj = self.env[model]
        arch = etree.XML(res['arch'])
        # Helper Functions
        def _add_field_def_to_view(resource, field_name, field_node):
            resource['fields'].update(model_obj.fields_get(allfields=[field_name]))
            setup_modifiers(field_node, resource['fields'][field_name])
        # Add State Field to Tree View if not Exists
        if view_type == 'tree':
            # Get Header Element
            tree_el = arch.xpath("//tree")
            tree_el = tree_el[0] if tree_el else False
            # Get State Element
            state_el = arch.xpath("//field[@name='state']")
            state_el = state_el[0] if state_el else False
            if state_el is False:
                state_el = etree.Element('field')
                state_el.set('name', 'state')
                _add_field_def_to_view(res, 'state', state_el)
                tree_el.append(state_el)
        res['arch'] = etree.tostring(arch, encoding="utf-8")
        return res

    def _add_mail_thread_view(self, view_type, res):
        """
            Adds messaging area to model in form view.
            :param view_type: Type of view now rendering.
            :param res: View resource data.
            :return: Updated view resource.
        """
        # Variables
        model = self._name
        model_obj = self.env[model]
        wkf_obj = self.env['odoo.workflow']
        wkf_rec = wkf_obj.search([('model_id', '=', model)])
        arch = etree.XML(res['arch'])
        # Helper Functions
        def _add_field_def_to_view(resource, field_name, field_node):
            resource['fields'].update(model_obj.fields_get(allfields=[field_name]))
            setup_modifiers(field_node, resource['fields'][field_name])
        # Add Mail Tread to Form View
        if view_type == 'form' and wkf_rec.mail_thread_add:
            # Get Form Element
            form_el = arch.xpath("//form")
            form_el = form_el[0] if form_el else False
            # Add Mail Thread
            mail_thread_root_el = etree.Element('div', attrib={'class': 'oe_chatter'})
            if wkf_rec.followers_add:
                followers_el = etree.Element('field', attrib={'name': 'message_follower_ids', 'widget': 'mail_followers'})
                _add_field_def_to_view(res, 'message_follower_ids', followers_el)
                mail_thread_root_el.append(followers_el)
            message_el = etree.Element('field', attrib={'name': 'message_ids', 'widget': 'mail_thread'})
            _add_field_def_to_view(res, 'message_ids', message_el)
            mail_thread_root_el.append(message_el)
            form_el.append(mail_thread_root_el)
        res['arch'] = etree.tostring(arch, encoding="utf-8")
        return res

    def warning(self, msg):
        if not isinstance(msg, (str, unicode)):
            msg = str(msg)
        raise Warning(msg)

    def syslog(self, msg):
        if not isinstance(msg, (str, unicode)):
            msg = str(msg)
        _logger.info(msg)