# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrCommissionHistory(models.Model):
    _name = 'hr.commission.history'
    _description = 'Employee Commission History'
    _order = 'active_from desc, id desc'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade'
    )
    commission_rate = fields.Float(
        string='Commission Rate',
        required=True,
        help="The commission rate for the employee."
    )
    active_from = fields.Date(
        string='Active From',
        required=True,
        default=lambda self: fields.Date.context_today(self),
        help="The date from which the commission rate is active."
    )
    active_to = fields.Date(
        string='Active To',
        help="The date until which the commission rate is active."
    )
    currently_active = fields.Boolean(
        string='Currently Active',
        compute='_compute_currently_active',
        store=True,
        help="Indicates if this commission rate is currently active."
    )

    @api.depends('active_to')
    def _compute_currently_active(self):
        for record in self:
            record.currently_active = not record.active_to

    @api.constrains('active_from', 'active_to')
    def _check_dates(self):
        for record in self:
            if record.active_to and record.active_from > record.active_to:
                raise models.ValidationError(_('The "Active From" date cannot be after the "Active To" date.'))
