# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    salary_type = fields.Selection([
        ('commission', 'Commission-based'),
        ('salary', 'Salary-based'),
        ('salary_commission', 'Salary + Commission')
    ], string="Salary Type", required=True, default='salary')
    
    is_peas = fields.Boolean(string="Is PEAS")
    commission_percentage = fields.Float(string="Commission Percentage (%)")
    vendor_partner_id = fields.Many2one('res.partner', string="Vendor Record", readonly=True)
    customer_partner_id = fields.Many2one('res.partner', string="Customer Record", readonly=True)
    commission_history_ids = fields.One2many('hr.commission.history', 'employee_id', string="Commission History", readonly=True)
    current_salary = fields.Float(string="Current Salary", default=0.0)
    current_month_commission = fields.Float(string="Current Month Commission", compute="_compute_current_month_commission", store=False)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    
    def _compute_current_month_commission(self):
        today = date.today()
        current_month = today.month
        current_year = today.year
        
        for employee in self:
            try:
                current_month_records = self.env['hr.commission.history'].search([
                    ('employee_id', '=', employee.id),
                    ('start_date', '>=', date(current_year, current_month, 1)),
                    ('start_date', '<=', date(current_year, current_month, 31) if current_month != 2 else date(current_year, current_month, 28))
                ])
                employee.current_month_commission = sum(record.amount for record in current_month_records)
            except Exception as e:
                _logger.error(f"Error computing commission: {str(e)}")
                employee.current_month_commission = 0.0
    
    @api.onchange('salary_type')
    def _onchange_salary_type(self):
        if self.salary_type == 'salary':
            self.commission_percentage = 0.0
    
    @api.constrains('salary_type', 'commission_percentage')
    def _check_commission_percentage(self):
        for record in self:
            if record.salary_type in ['commission', 'salary_commission'] and not record.commission_percentage:
                raise models.ValidationError(_("Commission percentage is required when salary type includes commission"))
    
    @api.model
    def create(self, vals):
        employee = super(HrEmployee, self).create(vals)
        
        # Create commission history record if commission percentage is set
        if employee.commission_percentage and employee.salary_type in ['commission', 'salary_commission']:
            self.env['hr.commission.history'].create({
                'employee_id': employee.id,
                'percentage': employee.commission_percentage,
                'start_date': fields.Date.today(),
            })
        
        # Create vendor and customer records if is_peas is checked
        if employee.is_peas:
            self._create_partner_records(employee)
        
        # Create contract and salary structure if salary type is set
        if vals.get('salary_type'):
            try:
                employee._create_or_update_contract()
                employee._create_salary_structure()
            except Exception as e:
                _logger.error(f"Error creating payroll records: {str(e)}")
            
        return employee
    
    def write(self, vals):
        # Check if commission percentage is changing
        if 'commission_percentage' in vals and any(vals['commission_percentage'] != emp.commission_percentage for emp in self):
            # Close current commission history records
            for employee in self:
                current_history = self.env['hr.commission.history'].search([
                    ('employee_id', '=', employee.id),
                    ('end_date', '=', False)
                ], limit=1)
                
                if current_history:
                    current_history.write({'end_date': fields.Date.today()})
            
            # Create new commission history records
            if vals.get('commission_percentage', 0) > 0:
                for employee in self:
                    self.env['hr.commission.history'].create({
                        'employee_id': employee.id,
                        'percentage': vals['commission_percentage'],
                        'start_date': fields.Date.today(),
                    })
        
        # Check if any fields that affect partner records are changing
        partner_fields = ['name', 'work_email', 'work_phone', 'mobile_phone', 
                         'address_id', 'private_street', 'private_street2',
                         'private_city', 'private_state_id', 'private_zip', 
                         'private_country_id', 'private_email', 'private_phone']
                         
        should_update_partners = any(field in vals for field in partner_fields)
        
        result = super(HrEmployee, self).write(vals)
        
        # Handle is_peas change
        if 'is_peas' in vals and vals['is_peas']:
            for employee in self:
                if not (employee.vendor_partner_id and employee.customer_partner_id):
                    self._create_partner_records(employee)
        
        # Update partner records if needed
        if should_update_partners:
            for employee in self.filtered(lambda e: e.is_peas):
                self._update_partner_records(employee)
        
        # Update contract if salary type or salary changed
        if 'salary_type' in vals or 'current_salary' in vals:
            for employee in self:
                try:
                    employee._create_or_update_contract()
                    employee._create_salary_structure()
                except Exception as e:
                    _logger.error(f"Error updating payroll records: {str(e)}")
                
        return result
    
    def _create_partner_records(self, employee):
        """Create vendor and customer records for PEAS employee"""
        partner_obj = self.env['res.partner']
        
        # Get employee address information
        work_address = employee.address_id
        
        # Common values for both vendor and customer
        common_values = {
            'street': work_address and work_address.street or employee.private_street or False,
            'street2': work_address and work_address.street2 or employee.private_street2 or False,
            'city': work_address and work_address.city or employee.private_city or False,
            'state_id': work_address and work_address.state_id.id or employee.private_state_id.id if employee.private_state_id else False,
            'zip': work_address and work_address.zip or employee.private_zip or False,
            'country_id': work_address and work_address.country_id.id or employee.private_country_id.id if employee.private_country_id else False,
            'email': employee.work_email or employee.private_email or False,
            'phone': employee.work_phone or employee.mobile_phone or employee.private_phone or False,
            'company_id': employee.company_id.id,
            'ref': f"EMP-{employee.id}",
            'employee_id': employee.id,  # Store reference to employee
            'user_id': employee.user_id.id if employee.user_id else False,  # Assign salesperson if available
        }
        
        # Create vendor record
        if not employee.vendor_partner_id:
            vendor = partner_obj.create({
                'name': f"{employee.name} (Vendor)",
                'company_type': 'company',
                'supplier_rank': 1,
                'customer_rank': 0,
                'comment': f"Created automatically for PEAS employee {employee.name}",
                'is_employee_vendor': True,
                **common_values
            })
            employee.sudo().vendor_partner_id = vendor.id
        else:
            # Update existing vendor record
            employee.vendor_partner_id.sudo().write({
                'name': f"{employee.name} (Vendor)",
                **common_values
            })
        
        # Create customer record
        if not employee.customer_partner_id:
            customer = partner_obj.create({
                'name': f"{employee.name} (Customer)",
                'company_type': 'person',
                'supplier_rank': 0,
                'customer_rank': 1,
                'comment': f"Created automatically for PEAS employee {employee.name}",
                'is_employee_customer': True,
                **common_values
            })
            employee.sudo().customer_partner_id = customer.id
        else:
            # Update existing customer record
            employee.customer_partner_id.sudo().write({
                'name': f"{employee.name} (Customer)",
                **common_values
            })
            
    def _update_partner_records(self, employee):
        """Update existing vendor and customer records"""
        if employee.vendor_partner_id or employee.customer_partner_id:
            self._create_partner_records(employee)  # Reuse create method which handles updates
    
    def action_pay_advance(self):
        """Pay advance to PEAS employee"""
        self.ensure_one()
        
        if not self.is_peas:
            return
            
        return {
            'name': _('Pay Advance to %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'hr.advance.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
                'default_company_id': self.company_id.id,
            }
        }
    def _create_or_update_contract(self):
        """Create or update employee contract based on their salary type"""
        contract_obj = self.env['hr.contract']
        
        # Look for existing active contract
        existing_contract = contract_obj.search([
            ('employee_id', '=', self.id),
            ('state', 'in', ['draft', 'open'])
        ], limit=1)
        
        # Get appropriate structure type - use a better mapping for names
        structure_type_mapping = {
            'salary': 'Salary Based',
            'commission': 'Commission Based',
            'salary_commission': 'Salary + Commission'
        }
        
        structure_type = self.env['hr.payroll.structure.type'].search([
            ('name', '=', structure_type_mapping.get(self.salary_type))
        ], limit=1)
        
        # If no matching structure type exists, create default ones
        if not structure_type:
            # Create structure types for each employee type
            structure_type = self.env['hr.payroll.structure.type'].create({
                'name': structure_type_mapping.get(self.salary_type),
                'default_schedule_pay': 'monthly',
            })
        
        # Determine wage based on salary type
        wage = 0
        if self.salary_type in ['salary', 'salary_commission']:
            wage = self.current_salary if self.current_salary else 0
        
        contract_vals = {
            'name': f"{self.name}'s {self.salary_type} Contract",
            'employee_id': self.id,
            'structure_type_id': structure_type.id,
            'wage': wage,
            'date_start': fields.Date.today(),
            'state': 'draft',
        }
        
        # Create or update contract
        if existing_contract:
            existing_contract.write(contract_vals)
            return existing_contract
        else:
            return contract_obj.create(contract_vals)    

    def _create_salary_structure(self):
        """Create or get appropriate salary structure for employee type"""
        structure_obj = self.env['hr.payroll.structure']
        rule_obj = self.env['hr.salary.rule']
        category_obj = self.env['hr.salary.rule.category']
        
        # Use same mapping as in _create_or_update_contract
        structure_type_mapping = {
            'salary': 'Salary Based',
            'commission': 'Commission Based',
            'salary_commission': 'Salary + Commission'
        }
        
        # Structure names should match the structure type name exactly
        structure_name_mapping = {
            'salary': 'Salary Structure',
            'commission': 'Commission Structure',
            'salary_commission': 'Salary + Commission Structure'
        }
        
        # First get the structure type we created earlier - use the mapped name
        structure_type_name = structure_type_mapping.get(self.salary_type)
        structure_type = self.env['hr.payroll.structure.type'].search([
            ('name', '=', structure_type_name)
        ], limit=1)
        
        if not structure_type:
            # If not found, create it
            structure_type = self.env['hr.payroll.structure.type'].create({
                'name': structure_type_name,
                'default_schedule_pay': 'monthly',
            })
        
        # Find or create salary rule categories - MISSING CODE SECTION
        basic_category = category_obj.search([('code', '=', 'BASIC')], limit=1) or category_obj.create({
            'name': 'Basic',
            'code': 'BASIC',
        })
        
        commission_category = category_obj.search([('code', '=', 'COM')], limit=1) or category_obj.create({
            'name': 'Commission',
            'code': 'COM',
        })
        
        # Get structure name from mapping
        structure_name = structure_name_mapping.get(self.salary_type)
        
        # Continue with the rest of your method...
        # Get structure name from mapping
        structure_name = structure_name_mapping.get(self.salary_type)
        
        # Search for structure by name and type_id
        structure = structure_obj.search([
            ('name', '=', structure_name),
            ('type_id', '=', structure_type.id)
        ], limit=1)
        
        if not structure:
            # Create new structure with the type_id included
            structure = structure_obj.create({
                'name': structure_name,
                'type_id': structure_type.id,
                'country_id': self.env.company.country_id.id,
            })
        
        # Check for rules across ALL structures to avoid duplicates
        if self.salary_type in ['salary', 'salary_commission']:
            basic_rule = rule_obj.search([
                ('code', '=', 'BASIC'), 
                ('struct_id', '=', structure.id)
            ], limit=1)
            
            if not basic_rule:
                basic_rule = rule_obj.create({
                    'name': 'Basic Salary',
                    'code': 'BASIC',
                    'category_id': basic_category.id,
                    'sequence': 1,
                    'amount_select': 'code',
                    'amount_python_compute': 'result = contract.wage',
                    'struct_id': structure.id,
                    'appears_on_payslip': True,
                })
        # Initialize commission_rule to None/False before the conditional code
        commission_rule = False
        if self.salary_type in ['commission', 'salary_commission']:
            commission_rule = rule_obj.search([
                ('code', '=', 'COM'), 
                ('struct_id', '=', structure.id)
            ], limit=1)

            if not commission_rule:
                # Fixed Python code for commission calculation - without using hasattr
                commission_code = """# Calculate commission based on sales and purchases
result = 0
# Get sales orders
sales = employee.env['sale.order'].search([
    ('user_id', '=', employee.user_id.id),
    ('state', 'in', ['sale', 'done']),
    ('date_order', '>=', payslip.date_from),
    ('date_order', '<=', payslip.date_to)
])
# Get purchase orders
purchases = employee.env['purchase.order'].search([
    ('user_id', '=', employee.user_id.id),
    ('state', 'in', ['purchase', 'done']),
    ('date_order', '>=', payslip.date_from),
    ('date_order', '<=', payslip.date_to)
])
# Calculate totals
sales_total = sum(order.amount_total for order in sales)
purchase_total = sum(order.amount_total for order in purchases)
# Apply commission percentage safely
commission_pct = employee.commission_percentage if employee.commission_percentage else 0
result = (sales_total + purchase_total) * (commission_pct / 100)
"""
                # Create the commission rule inside the if not commission_rule block
                commission_rule = rule_obj.create({
                    'name': 'Commission',
                    'code': 'COM',
                    'category_id': commission_category.id,
                    'sequence': 2,
                    'amount_select': 'code',
                    'amount_python_compute': commission_code,
                    'struct_id': structure.id,
                    'appears_on_payslip': True,
                })  
            
        return structure
    

    def generate_payslip(self):
        """Generate a draft payslip for the employee"""
        self.ensure_one()
        
        # Check for active contract
        contract = self.env['hr.contract'].search([
            ('employee_id', '=', self.id),
            ('state', 'in', ['open', 'draft']),  # Include draft contracts too
        ], limit=1)
        
        if not contract:
            # Create a contract if none exists
            try:
                contract = self._create_or_update_contract()
                # Set contract to running state to use it for payslip
                contract.state = 'open'
            except Exception as e:
                raise UserError(_("Could not create contract: %s") % str(e))
        
        # Get appropriate structure
        structure = self._create_salary_structure()
        
        # Create payslip
        payslip_obj = self.env['hr.payslip']
        
        # Get date range (current month)
        today = fields.Date.today()
        start_date = today.replace(day=1)
        end_date = (start_date + relativedelta(months=1, day=1, days=-1))
        
        payslip = payslip_obj.create({
            'name': f"Payslip for {self.name} - {today.strftime('%B %Y')}",
            'employee_id': self.id,
            'contract_id': contract.id,
            'struct_id': structure.id,
            'date_from': start_date,
            'date_to': end_date,
        })
        
        # Compute the payslip
        payslip.compute_sheet()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip',
            'view_mode': 'form',
            'res_id': payslip.id,
            'target': 'current',
        }


class HrAdvancePaymentWizard(models.TransientModel):
    _name = 'hr.advance.payment.wizard'
    _description = 'Employee Advance Payment'
    
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True)
    company_id = fields.Many2one('res.company', string="Company", required=True)
    amount = fields.Monetary(string="Amount", required=True)
    payment_date = fields.Date(string="Payment Date", required=True, default=fields.Date.today)
    journal_id = fields.Many2one('account.journal', string="Payment Journal", 
                                domain="[('type', 'in', ['bank', 'cash']), ('company_id', '=', company_id)]", 
                                required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                related='journal_id.currency_id', readonly=True)
    
    def action_confirm_payment(self):
        """Create advance payment for employee"""
        self.ensure_one()
        
        if not self.employee_id.vendor_partner_id:
            raise UserError(_("No vendor record found for this employee. Please create one first."))
        
        # Get vendor's company
        vendor_company = self.company_id
        
        # Find expense account in the vendor's company
        expense_account = self.env['account.account'].search([
            ('company_id', '=', vendor_company.id),
            ('account_type', '=', 'expense'),
            ('deprecated', '=', False)
        ], limit=1)
        
        if not expense_account:
            raise UserError(_("No expense account found in company %s. Please configure an expense account.") 
                          % vendor_company.name)
        
        # Get purchase journal
        journal = self.env['account.journal'].search([
            ('company_id', '=', vendor_company.id),
            ('type', '=', 'purchase')
        ], limit=1)
        
        if not journal:
            journal = self.journal_id
        
        # Create bill with explicit company
        invoice_vals = {
            'partner_id': self.employee_id.vendor_partner_id.id,
            'move_type': 'in_invoice',
            'invoice_date': self.payment_date,
            'journal_id': journal.id,
            'company_id': vendor_company.id,
            'invoice_line_ids': [(0, 0, {
                'name': f"Advance payment for {self.employee_id.name}",
                'quantity': 1,
                'price_unit': self.amount,
                'account_id': expense_account.id,
            })],
        }
        
        bill = self.env['account.move'].with_company(vendor_company.id).create(invoice_vals)
        
        return {
            'name': _('Advance Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': bill.id,
            'view_mode': 'form',
            'target': 'current',
        }


class HrCommissionHistory(models.Model):
    _name = 'hr.commission.history'
    _description = 'Employee Commission History'
    _order = 'start_date desc, id desc'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete="cascade")
    percentage = fields.Float(string="Commission (%)", required=True)
    start_date = fields.Date(string="From Date", required=True)
    end_date = fields.Date(string="To Date")
    amount = fields.Monetary(string="Amount", default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency', related='employee_id.currency_id')


