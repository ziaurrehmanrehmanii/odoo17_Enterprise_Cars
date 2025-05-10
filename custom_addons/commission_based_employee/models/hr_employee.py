# -*- coding: utf-8 -*-
import logging
from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    commission_rate = fields.Float(string='Commission Rate', default=0.0, required=True, )
    commission_history = fields.One2many(
        'hr.commission.history',
        'employee_id',
        string='Commission History',
        help='History of commission changes for the employee'
    )
    structure_type = fields.Selection([
        ('commission_based', 'Commission Based'),
        ('salary_based', 'Salary Based'),
        ('salary_and_commission_based', 'Salary and Commission Based'),
    ], string='Structure Type', default='salary_based', required=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        employees = super(HrEmployee, self).create(vals_list)
        print("Employees Created::::::::::::::::::::::::::: ", employees)
        print("Vals List::::::::::::::::::::::::::::::::::: ", vals_list)
        
        # 1. First create rule categories
        commission_rule_catagory = self.env['hr.salary.rule.category'].search([('name', '=', 'Commission')], limit=1)
        salary_rule_catagory = self.env['hr.salary.rule.category'].search([('name', '=', 'Salary')], limit=1)
        if not commission_rule_catagory:
            commission_rule_catagory = self.env['hr.salary.rule.category'].create({
                'name': 'Commission',
                'code': 'COMMISSION',
            })
            _logger.info(f"Commission Rule Category '{commission_rule_catagory.name}' created.")
        else:
            _logger.info(f"Commission Rule Category '{commission_rule_catagory.name}' already exists.")
        if not salary_rule_catagory:
            salary_rule_catagory = self.env['hr.salary.rule.category'].create({
                'name': 'Salary',
                'code': 'SALARY',
            })
            _logger.info(f"Salary Rule Category '{salary_rule_catagory.name}' created.")
        else:
            _logger.info(f"Salary Rule Category '{salary_rule_catagory.name}' already exists.")
            
        # 2. Create structure types
        commission_structure_type = self.env['hr.payroll.structure.type'].search([('name', '=', 'Commission Based')], limit=1)
        salary_structure_type = self.env['hr.payroll.structure.type'].search([('name', '=', 'Salary Based')], limit=1)
        salary_and_commission_structure_type = self.env['hr.payroll.structure.type'].search([('name', '=', 'Salary and Commission Based')], limit=1)
        
        if not commission_structure_type:
            commission_structure_type = self.env['hr.payroll.structure.type'].create({
                'name': 'Commission Based',
                'default_schedule_pay': 'monthly',
                'display_name': 'Commission Based',
                'wage_type': 'monthly',
            })
            _logger.info(f"Commission Based Structure Type '{commission_structure_type.name}' created.")
        else:
            _logger.info(f"Commission Based Structure Type '{commission_structure_type.name}' already exists.")
            
        if not salary_structure_type:
            salary_structure_type = self.env['hr.payroll.structure.type'].create({
                'name': 'Salary Based',
                'default_schedule_pay': 'monthly',
                'display_name': 'Salary Based',
                'wage_type': 'monthly',
            })
            _logger.info(f"Salary Based Structure Type '{salary_structure_type.name}' created.")
        else:
            _logger.info(f"Salary Based Structure Type '{salary_structure_type.name}' already exists.")
            
        if not salary_and_commission_structure_type:
            salary_and_commission_structure_type = self.env['hr.payroll.structure.type'].create({
                'name': 'Salary and Commission Based',
                'default_schedule_pay': 'monthly',
                'display_name': 'Salary and Commission Based',
                'wage_type': 'monthly',
            })
            _logger.info(f"Salary and Commission Based Structure Type '{salary_and_commission_structure_type.name}' created.")
        else:
            _logger.info(f"Salary and Commission Based Structure Type '{salary_and_commission_structure_type.name}' already exists.")
            
        # 3. Create payroll structures first
        commission_based_structure = self.env['hr.payroll.structure'].search([('name', '=', 'Commission Based')], limit=1)
        salary_based_structure = self.env['hr.payroll.structure'].search([('name', '=', 'Salary Based')], limit=1)
        salary_and_commission_based_structure = self.env['hr.payroll.structure'].search([('name', '=', 'Salary and Commission Based')], limit=1)
        
        # Commission Based Structure
        if not commission_based_structure:
            commission_based_structure = self.env['hr.payroll.structure'].create({
                'name': 'Commission Based',
                'code': 'COMMISSION_BASED',
                'type_id': commission_structure_type.id,
                "active": True,
                "note": "Commission Based Structure",
            })
            _logger.info(f"Commission Based Structure '{commission_based_structure.name}' created.")
        else:
            _logger.info(f"Commission Based Structure '{commission_based_structure.name}' already exists.")
            
        # Salary Based Structure
        if not salary_based_structure:
            salary_based_structure = self.env['hr.payroll.structure'].create({
                'name': 'Salary Based',
                'code': 'SALARY_BASED',
                'type_id': salary_structure_type.id,
                "active": True,
                "note": "Salary Based Structure",
            })
            _logger.info(f"Salary Based Structure '{salary_based_structure.name}' created.")
        else:
            _logger.info(f"Salary Based Structure '{salary_based_structure.name}' already exists.")
            
        # Salary and Commission Based Structure
        if not salary_and_commission_based_structure:
            salary_and_commission_based_structure = self.env['hr.payroll.structure'].create({
                'name': 'Salary and Commission Based',
                'code': 'SALARY_AND_COMMISSION_BASED',
                'type_id': salary_and_commission_structure_type.id,
                "active": True,
                "note": "Salary and Commission Based Structure",
            })
            _logger.info(f"Salary and Commission Based Structure '{salary_and_commission_based_structure.name}' created.")
        else:
            _logger.info(f"Salary and Commission Based Structure '{salary_and_commission_based_structure.name}' already exists.")
            
        # 4. Now create the salary rules that reference structures
        commission_rule = self.env['hr.salary.rule'].search([('name', '=', 'Commission')], limit=1)
        salary_rule = self.env['hr.salary.rule'].search([('name', '=', 'Salary')], limit=1)
        commission_and_salary_rule = self.env['hr.salary.rule'].search([('name', '=', 'Commission and Salary')], limit=1)
        
        # Commission Rule
        if not commission_rule:
            commission_rule = self.env['hr.salary.rule'].create({
                'name': 'Commission',
                'code': 'COMMISSION',
                'category_id': commission_rule_catagory.id,
                'struct_id': commission_based_structure.id,
                'sequence': 1,
                'condition_select': 'none',
                'amount_select': 'code',
                'amount_python_compute': 'result = contract.wage * 0.1',
            })
            _logger.info(f"Commission Rule '{commission_rule.name}' created.")
        else:
            _logger.info(f"Commission Rule '{commission_rule.name}' already exists.")
        # Commission and Salary Rule
        if not salary_rule:
            salary_rule = self.env['hr.salary.rule'].create({
                'name': 'Salary',
                'code': 'SALARY',
                'category_id': salary_rule_catagory.id,
                'struct_id': salary_based_structure.id,
                'sequence': 1,
                'condition_select': 'none',
                'amount_select': 'code',
                'amount_python_compute': 'result = contract.wage',
            })
            _logger.info(f"Salary Rule '{salary_rule.name}' created.")
        else:
            _logger.info(f"Salary Rule '{salary_rule.name}' already exists.")
        # Commission and Salary Rule
        if not commission_and_salary_rule:
            commission_and_salary_rule = self.env['hr.salary.rule'].create({
                'name': 'Commission and Salary',
                'code': 'COMMISSION_AND_SALARY',
                'category_id': commission_rule_catagory.id,
                'struct_id': salary_and_commission_based_structure.id,
                'sequence': 1,
                'condition_select': 'none',
                'amount_select': 'code',
                'amount_python_compute': 'result = contract.wage * 0.1 + contract.wage',
            })
            _logger.info(f"Commission and Salary Rule '{commission_and_salary_rule.name}' created.")
        else:
            _logger.info(f"Commission and Salary Rule '{commission_and_salary_rule.name}' already exists.")
        # check if salary structure name 'Commission Based', 'Salary Based' and 'Salary and Commission Based' exists
        # if they do not exist create them
        commission_based_structure = self.env['hr.payroll.structure'].search([('name', '=', 'Commission Based')], limit=1)
        salary_based_structure = self.env['hr.payroll.structure'].search([('name', '=', 'Salary Based')], limit=1)
        salary_and_commission_based_structure = self.env['hr.payroll.structure'].search([('name', '=', 'Salary and Commission Based')], limit=1)
        # Commission Based Structure
        if not commission_based_structure:
            commission_based_structure = self.env['hr.payroll.structure'].create({
                'name': 'Commission Based',
                'code': 'COMMISSION_BASED',
                'type_id': commission_structure_type.id,
                "active": True,
                "note": "Commission Based Structure",
                
            })
            _logger.info(f"Commission Based Structure '{commission_based_structure.name}' created.")
        else:
            _logger.info(f"Commission Based Structure '{commission_based_structure.name}' already exists.")
        # Salary Based Structure
        if not salary_based_structure:
            salary_based_structure = self.env['hr.payroll.structure'].create({
                'name': 'Salary Based',
                'code': 'SALARY_BASED',
                'type_id': salary_structure_type.id,
                "active": True,
                "note": "Salary Based Structure",
                
            })
            _logger.info(f"Salary Based Structure '{salary_based_structure.name}' created.")
        else:
            _logger.info(f"Salary Based Structure '{salary_based_structure.name}' already exists.")
        # Salary and Commission Based Structure
        if not salary_and_commission_based_structure:
            salary_and_commission_based_structure = self.env['hr.payroll.structure'].create({
                'name': 'Salary and Commission Based',
                'code': 'SALARY_AND_COMMISSION_BASED',
                'type_id': salary_and_commission_structure_type.id,
                "active": True,
                "note": "Salary and Commission Based Structure",
                
            })
            _logger.info(f"Salary and Commission Based Structure '{salary_and_commission_based_structure.name}' created.")
        else:
            _logger.info(f"Salary and Commission Based Structure '{salary_and_commission_based_structure.name}' already exists.")
        
        # Create initial commission history for new employees
        for i, employee in enumerate(employees):
            vals = vals_list[i]
            if 'commission_rate' in vals and vals['commission_rate'] is not None:
                self.env['hr.commission.history'].create({
                    'employee_id': employee.id,
                    'commission_rate': vals['commission_rate'],
                    'active_from': fields.Date.context_today(employee),
                    'active_to': False,
                })

        # create a new hr.contract for the employee with the selected salary structure
        for employee in employees:
            # Determine the structure based on employee type
            selected_structure = commission_based_structure if employee.structure_type == 'commission_based' else \
                                salary_based_structure if employee.structure_type == 'salary_based' else \
                                salary_and_commission_based_structure
            
            # Create basic contract values without the structure field
            contract_vals = {
                'name': employee.name,
                'employee_id': employee.id,
                'wage': 0,  # Default wage if contract_id not available
                'department_id': employee.department_id.id,
                'job_id': employee.job_id.id,
            }
            
            # Try to get wage if contract_id exists
            if hasattr(employee, 'contract_id') and employee.contract_id:
                contract_vals['wage'] = employee.contract_id.wage
            
            # Try adding structure field - try both common field names
            try:
                # Try the new field name first (likely to be structure_type_id in Odoo 17)
                contract_vals['structure_type_id'] = selected_structure.type_id.id
            except Exception as e:
                _logger.warning(f"Could not set structure_type_id: {str(e)}")
                
            # Set contract state
            contract_vals['state'] = 'open'
            
            # Create the contract
            try:
                contract = self.env['hr.contract'].create(contract_vals)
                _logger.info(f"Contract '{contract.name}' created for employee '{employee.name}'.")
            except Exception as e:
                _logger.error(f"Failed to create contract for employee {employee.name}: {str(e)}")
        

        
        
        return employees
    
    def write(self, vals):
        # Store old commission rates before updating
        old_commission_rates = {}
        if 'commission_rate' in vals:
            for emp in self:
                old_commission_rates[emp.id] = emp.commission_rate

        employees_res = super(HrEmployee, self).write(vals)

        # if the commission rate is changed, update commission history
        if 'commission_rate' in vals:
            new_commission_rate = vals['commission_rate']
            for employee in self:
                # Check if the rate actually changed for this employee
                if old_commission_rates.get(employee.id) != new_commission_rate:
                    today = fields.Date.context_today(employee)
                    
                    # End previous active commission history record
                    active_history = self.env['hr.commission.history'].search([
                        ('employee_id', '=', employee.id),
                        ('active_to', '=', False)
                    ], limit=1, order='active_from desc')
                    
                    if active_history:
                        end_date_for_old_record = today - timedelta(days=1)
                        # Ensure active_to is not before active_from
                        if end_date_for_old_record < active_history.active_from:
                            end_date_for_old_record = active_history.active_from
                        active_history.write({'active_to': end_date_for_old_record})

                    # Create new commission history record
                    if new_commission_rate is not None: # Only create if new rate is set
                        self.env['hr.commission.history'].create({
                            'employee_id': employee.id,
                            'commission_rate': new_commission_rate,
                            'active_from': today,
                            'active_to': False,
                        })
        
        # if the structure type is changed, update the contract and payslip accordingly
        for employee in self:
            if 'structure_type' in vals:
                structure_type_name = False
                if vals['structure_type'] == 'commission_based':
                    structure_type_name = 'Commission Based'
                elif vals['structure_type'] == 'salary_based':
                    structure_type_name = 'Salary Based'
                elif vals['structure_type'] == 'salary_and_commission_based':
                    structure_type_name = 'Salary and Commission Based'
                
                if structure_type_name:
                    payroll_structure_type = self.env['hr.payroll.structure.type'].search([('name', '=', structure_type_name)], limit=1)
                    if payroll_structure_type and employee.contract_id:
                        employee.contract_id.write({
                            'structure_type_id': payroll_structure_type.id,
                        })
                    elif not payroll_structure_type:
                        _logger.warning(f"Payroll structure type '{structure_type_name}' not found for employee {employee.name}.")
                    elif not employee.contract_id:
                        _logger.warning(f"Employee {employee.name} does not have an active contract to update.")
                else:
                    raise UserError(_('Invalid structure type selected.'))
        # if the commission rate is changed, update the commission rule accordingly
        if 'commission_rate' in vals:
            for employee in self:
                commission_rule = self.env['hr.salary.rule'].search([('name', '=', 'Commission')], limit=1)
                if commission_rule:
                    commission_rule.write({
                        'amount_python_compute': 'result = contract.wage * %s' % vals['commission_rate'],
                    })
                else:
                    raise UserError(_('Commission rule not found.'))
        # if the salary is changed, update the salary rule accordingly
        if 'wage' in vals:
            for employee in self:
                salary_rule = self.env['hr.salary.rule'].search([('name', '=', 'Salary')], limit=1)
                if salary_rule:
                    salary_rule.write({
                        'amount_python_compute': 'result = %s' % vals['wage'],
                    })
                else:
                    raise UserError(_('Salary rule not found.'))
        return employees_res
