# -*- coding: utf-8 -*-
# from odoo import http


# class EmployeeCommissionCustom(http.Controller):
#     @http.route('/employee_commission_custom/employee_commission_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_commission_custom/employee_commission_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_commission_custom.listing', {
#             'root': '/employee_commission_custom/employee_commission_custom',
#             'objects': http.request.env['employee_commission_custom.employee_commission_custom'].search([]),
#         })

#     @http.route('/employee_commission_custom/employee_commission_custom/objects/<model("employee_commission_custom.employee_commission_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_commission_custom.object', {
#             'object': obj
#         })

