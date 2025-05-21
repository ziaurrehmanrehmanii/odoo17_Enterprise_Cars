# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    @api.model_create_multi
    def create(self, vals_list):
        # Check if security groups exist to avoid errors
        group_car_sales_purchase_user = self.env.ref('car_sales_purchase.group_car_sales_purchase_user', raise_if_not_found=False)
        group_car_sales_purchase_manager = self.env.ref('car_sales_purchase.group_car_sales_purchase_manager', raise_if_not_found=False)
        
        if self.env.user.has_group('peas_employee.group_peas_employee_user'):
            if group_car_sales_purchase_user and group_car_sales_purchase_user.id not in self.env.user.groups_id.ids:
                self.env.user.write({'groups_id': [(4, group_car_sales_purchase_user.id)]})
            if group_car_sales_purchase_manager and group_car_sales_purchase_manager.id not in self.env.user.groups_id.ids:
                self.env.user.write({'groups_id': [(4, group_car_sales_purchase_manager.id)]})

        # Call the super method to create the employees
        employees = super().create(vals_list)
        
        # Add employee users to both groups if they exist
        for employee in employees:
            if employee.user_id and employee.user_id.has_group('peas_employee.group_peas_employee_user'):
                if group_car_sales_purchase_user and group_car_sales_purchase_user.id not in employee.user_id.groups_id.ids:
                    employee.user_id.write({'groups_id': [(4, group_car_sales_purchase_user.id)]})
                if group_car_sales_purchase_manager and group_car_sales_purchase_manager.id not in employee.user_id.groups_id.ids:
                    employee.user_id.write({'groups_id': [(4, group_car_sales_purchase_manager.id)]})
        # Log the employee creation  
        return employees

    def write(self, vals):
        # Check if security groups exist to avoid errors
        group_car_sales_purchase_user = self.env.ref('car_sales_purchase.group_car_sales_purchase_user', raise_if_not_found=False)
        group_car_sales_purchase_manager = self.env.ref('car_sales_purchase.group_car_sales_purchase_manager', raise_if_not_found=False)
        
        # Add current user to both groups if they belong to peas_employee_user
        if self.env.user.has_group('peas_employee.group_peas_employee_user'):
            if group_car_sales_purchase_user and group_car_sales_purchase_user.id not in self.env.user.groups_id.ids:
                self.env.user.write({'groups_id': [(4, group_car_sales_purchase_user.id)]})
            if group_car_sales_purchase_manager and group_car_sales_purchase_manager.id not in self.env.user.groups_id.ids:
                self.env.user.write({'groups_id': [(4, group_car_sales_purchase_manager.id)]})
        
        # Call the super method
        result = super().write(vals)
        
        # Update group membership for employee users if they belong to peas_employee_user
        for employee in self:
            if employee.user_id and employee.user_id.has_group('peas_employee.group_peas_employee_user'):
                if group_car_sales_purchase_user and group_car_sales_purchase_user.id not in employee.user_id.groups_id.ids:
                    employee.user_id.write({'groups_id': [(4, group_car_sales_purchase_user.id)]})
                if group_car_sales_purchase_manager and group_car_sales_purchase_manager.id not in employee.user_id.groups_id.ids:
                    employee.user_id.write({'groups_id': [(4, group_car_sales_purchase_manager.id)]})
        
        return result

    def unlink(self):
        # Check if security groups exist to avoid errors
        group_car_sales_purchase_user = self.env.ref('car_sales_purchase.group_car_sales_purchase_user', raise_if_not_found=False)
        group_car_sales_purchase_manager = self.env.ref('car_sales_purchase.group_car_sales_purchase_manager', raise_if_not_found=False)
        
        # Add current user to both groups if they belong to peas_employee_user
        if self.env.user.has_group('peas_employee.group_peas_employee_user'):
            if group_car_sales_purchase_user and group_car_sales_purchase_user.id not in self.env.user.groups_id.ids:
                self.env.user.write({'groups_id': [(4, group_car_sales_purchase_user.id)]})
            if group_car_sales_purchase_manager and group_car_sales_purchase_manager.id not in self.env.user.groups_id.ids:
                self.env.user.write({'groups_id': [(4, group_car_sales_purchase_manager.id)]})
        
        # No need to update the employees' users as they're being deleted
        return super().unlink()