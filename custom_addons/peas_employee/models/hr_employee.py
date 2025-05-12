# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    is_peas_employee = fields.Boolean(string='Is Peas Employee', default=False)
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier_rank', '>', 0)], help="Select the vendor associated with this employee.")
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('customer_rank', '>', 0)], help="Select the customer associated with this employee.")
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        Override the create method to create or update vendor and customer partners 
        when creating a PEAS employee.
        """
        employees = super(HrEmployee, self).create(vals_list)
        for employee in employees:
            # Check if the employee is a PEAS employee
            if employee.is_peas_employee:
                _logger.info("PEAS employee created: %s", employee.name)
                
                # Create or update associated user, vendor and customer
                self._create_or_update_peas_employee_data(employee)
                
        return employees
   
    def write(self, vals):
        """
        Override the write method to update vendor and customer information
        when employee data changes or is_peas_employee is toggled.
        """
        res = super(HrEmployee, self).write(vals)
        
        # Check if we need to update vendor/customer info
        update_partner_info = False
        if 'is_peas_employee' in vals and vals['is_peas_employee']:
            update_partner_info = True
        elif any(field in vals for field in ['name', 'work_email', 'work_phone', 'mobile_phone']):
            update_partner_info = True
            
        if update_partner_info:
            for employee in self:
                if employee.is_peas_employee:
                    # Create or update associated user, vendor and customer
                    self._create_or_update_peas_employee_data(employee)
        
        return res
        
    def _create_or_update_peas_employee_data(self, employee):
        """
        Helper method to create or update user, vendor and customer for PEAS employees
        """
        # STEP 1: Create or update user account
        if not employee.user_id and employee.work_email:
            # First check if a user with this login already exists
            existing_user = self.env['res.users'].sudo().search([
                ('login', '=', employee.work_email)
            ], limit=1)
            
            if existing_user:
                # Link the existing user to this employee
                employee.user_id = existing_user.id
                _logger.info("Linked existing user to PEAS employee: %s", existing_user.name)
            else:
                # Create a new user
                user_vals = {
                    'name': employee.name,
                    'login': employee.work_email,
                    'email': employee.work_email,
                    'employee_ids': [(4, employee.id)],
                    'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
                }
                user = self.env['res.users'].sudo().create(user_vals)
                employee.user_id = user.id
                _logger.info("User created for PEAS employee: %s", user.name)
        
        # STEP 2: Prepare common partner values
        partner_vals = {
            'name': employee.name,
            'is_company': False,
            'email': employee.work_email,
            'phone': employee.work_phone,
            'mobile': employee.mobile_phone,
            'user_id': employee.user_id.id if employee.user_id else False,
        }
        
        # Add address info if work_contact_id exists
        if employee.work_contact_id:
            partner_vals.update({
                'street': employee.work_contact_id.street,
                'street2': employee.work_contact_id.street2,
                'city': employee.work_contact_id.city,
                'state_id': employee.work_contact_id.state_id.id if employee.work_contact_id.state_id else False,
                'zip': employee.work_contact_id.zip,
                'country_id': employee.work_contact_id.country_id.id if employee.work_contact_id.country_id else False,
            })
        
        # STEP 3: Handle vendor - update existing or create new
        if employee.vendor_id:
            # Update existing vendor
            employee.vendor_id.write(partner_vals)
            _logger.info("Vendor updated for PEAS employee: %s", employee.name)
        else:
            # Search for existing vendor with same email (if email exists)
            existing_vendor = False
            if employee.work_email:
                existing_vendor = self.env['res.partner'].sudo().search([
                    ('email', '=', employee.work_email),
                    ('supplier_rank', '>', 0),
                    ('is_company', '=', False)
                ], limit=1)
            
            if existing_vendor:
                # Update the existing vendor
                existing_vendor.write(partner_vals)
                employee.vendor_id = existing_vendor.id
                _logger.info("Linked existing vendor to PEAS employee: %s", existing_vendor.name)
            else:
                # Create a new vendor
                vendor_vals = dict(partner_vals)
                vendor_vals.update({
                    'supplier_rank': 1,
                    'customer_rank': 0,
                })
                vendor = self.env['res.partner'].sudo().create(vendor_vals)
                employee.vendor_id = vendor.id
                _logger.info("Vendor created for PEAS employee: %s", vendor.name)
        
        # STEP 4: Handle customer - update existing or create new
        if employee.customer_id:
            # Update existing customer
            employee.customer_id.write(partner_vals)
            _logger.info("Customer updated for PEAS employee: %s", employee.name)
        else:
            # Search for existing customer with same email (if email exists)
            existing_customer = False
            if employee.work_email:
                existing_customer = self.env['res.partner'].sudo().search([
                    ('email', '=', employee.work_email),
                    ('customer_rank', '>', 0),
                    ('is_company', '=', False)
                ], limit=1)
            
            if existing_customer:
                # Update the existing customer
                existing_customer.write(partner_vals)
                employee.customer_id = existing_customer.id
                _logger.info("Linked existing customer to PEAS employee: %s", existing_customer.name)
            else:
                # Create a new customer
                customer_vals = dict(partner_vals)
                customer_vals.update({
                    'supplier_rank': 0,
                    'customer_rank': 1,
                })
                customer = self.env['res.partner'].sudo().create(customer_vals)
                employee.customer_id = customer.id
                _logger.info("Customer created for PEAS employee: %s", customer.name)
        
        _logger.info("PEAS employee data updated: %s", employee.name)

    @api.onchange('is_peas_employee', 'work_email')
    def _onchange_is_peas_employee(self):
        """When is_peas_employee is true, ensure work_email is set and user_id has login"""
        if self.is_peas_employee and not self.work_email:
            return {
                'warning': {
                    'title': _("Required Field"),
                    'message': _("Work email is required for PEAS employees and will be used as login.")
                }
            }
    
    @api.constrains('is_peas_employee', 'work_email', 'user_id')
    def _check_peas_employee_requirements(self):
        for employee in self:
            if employee.is_peas_employee and not employee.work_email:
                raise ValidationError(_("Work email is required for PEAS employees"))
                
    def create_user(self):
        """Create user for the employee with work_email as login"""
        self.ensure_one()
        if not self.work_email:
            raise ValidationError(_("Cannot create user without an email address"))
            
        user_vals = {
            'name': self.name,
            'login': self.work_email,  # Set login to work_email
            'email': self.work_email,
            'partner_id': self.address_id.id if self.address_id else False,
        }
        
        user = self.env['res.users'].sudo().create(user_vals)
        self.user_id = user
        return user

