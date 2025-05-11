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
        Override the create method to set the is_peas_employee field to True
        when creating a new employee.
        """
        employees = super(HrEmployee, self).create(vals_list)
        for employee in employees:
            # Check if the employee is a PEAS employee
            if employee.is_peas_employee:
                # Perform any additional actions needed for PEAS employees
                _logger.info("PEAS employee created: %s", employee.name)
                
                # Create an internal user for the employee if it doesn't exist
                if not employee.user_id and employee.work_email:
                    user_vals = {
                        'name': employee.name,
                        'login': employee.work_email,
                        'email': employee.work_email,
                        'employee_ids': [(4, employee.id)],
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
                    }
                    user = self.env['res.users'].create(user_vals)
                    # Log the creation of the user
                    _logger.info("User created for PEAS employee: %s", user.name)
                    
                # Create a vendor and customer for the employee with the same name
                # and link them to the employee
                # the vendor and cutomer are both individuals
                vendor_vals = {
                    'name': employee.name,
                    'is_company': False,
                    'supplier_rank': 1,
                    'customer_rank': 0,
                    'user_id': employee.user_id.id if employee.user_id else False,
                    'buyer_id': employee.user_id.id if employee.user_id else False,
                    'email': employee.work_email,
                    'phone': employee.work_phone,
                    'mobile': employee.mobile_phone,
                }
                
                # Add address information from work_contact_id if it exists
                if employee.work_contact_id:
                    vendor_vals.update({
                        'street': employee.work_contact_id.street,
                        'street2': employee.work_contact_id.street2,
                        'city': employee.work_contact_id.city,
                        'state_id': employee.work_contact_id.state_id.id if employee.work_contact_id.state_id else False,
                        'zip': employee.work_contact_id.zip,
                        'country_id': employee.work_contact_id.country_id.id if employee.work_contact_id.country_id else False,
                    })
                
                customer_vals = {
                    'name': employee.name,
                    'is_company': False,
                    'supplier_rank': 0,
                    'customer_rank': 1,
                    'user_id': employee.user_id.id if employee.user_id else False,
                    'buyer_id': employee.user_id.id if employee.user_id else False,
                    'email': employee.work_email,
                    'phone': employee.work_phone,
                    'mobile': employee.mobile_phone,
                }
                
                # Add address information from work_contact_id if it exists
                if employee.work_contact_id:
                    customer_vals.update({
                        'street': employee.work_contact_id.street,
                        'street2': employee.work_contact_id.street2,
                        'city': employee.work_contact_id.city,
                        'state_id': employee.work_contact_id.state_id.id if employee.work_contact_id.state_id else False,
                        'zip': employee.work_contact_id.zip,
                        'country_id': employee.work_contact_id.country_id.id if employee.work_contact_id.country_id else False,
                    })
                
                vendor = self.env['res.partner'].create(vendor_vals)
                customer = self.env['res.partner'].create(customer_vals)
                # Link the vendor and customer to the employee
                employee.vendor_id = vendor.id
                employee.customer_id = customer.id
                # Log the creation of the vendor and customer
                _logger.info("Vendor created for PEAS employee: %s", vendor.name)
                _logger.info("Customer created for PEAS employee: %s", customer.name)
        return employees
   
   
    def write(self, vals):
        """
        Override the write method to set the is_peas_employee field to True
        when creating a new employee.
        """
        res = super(HrEmployee, self).write(vals)
        # Check if the employee is a PEAS employee
        if 'is_peas_employee' in vals:
            for employee in self:
                if employee.is_peas_employee:
                # check if the partner accounts exisit for this employee
                    if not employee.vendor_id:
                        # Create a vendor and customer for the employee with the same name
                        # and link them to the employee
                        # the vendor and cutomer are both individuals
                        vendor_vals = {
                            'name': employee.name,
                            'is_company': False,
                            'supplier_rank': 1,
                            'customer_rank': 0,
                        }
                        customer_vals = {
                            'name': employee.name,
                            'is_company': False,
                            'supplier_rank': 0,
                            'customer_rank': 1,
                        }
                        vendor = self.env['res.partner'].create(vendor_vals)
                        customer = self.env['res.partner'].create(customer_vals)
                        # Link the vendor and customer to the employee
                        employee.vendor_id = vendor.id
                        employee.customer_id = customer.id
                        # Log the creation of the vendor and customer
                        _logger.info("Vendor created for PEAS employee: %s", vendor.name)
                        _logger.info("Customer created for PEAS employee: %s", customer.name)
                    else:
                        # Update existing vendor and customer details if needed
                        
                        employee.vendor_id.name = employee.name
                        employee.customer_id.name = employee.name
                        
                    
                        # Perform any additional actions needed for PEAS employees
                        _logger.info("PEAS employee updated: %s", employee.name)
        return res

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

