# -*- coding: utf-8 -*-
# from odoo import http


# class HrSalaryCommissionPeas(http.Controller):
#     @http.route('/hr_salary_commission_peas/hr_salary_commission_peas', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_salary_commission_peas/hr_salary_commission_peas/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_salary_commission_peas.listing', {
#             'root': '/hr_salary_commission_peas/hr_salary_commission_peas',
#             'objects': http.request.env['hr_salary_commission_peas.hr_salary_commission_peas'].search([]),
#         })

#     @http.route('/hr_salary_commission_peas/hr_salary_commission_peas/objects/<model("hr_salary_commission_peas.hr_salary_commission_peas"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_salary_commission_peas.object', {
#             'object': obj
#         })

