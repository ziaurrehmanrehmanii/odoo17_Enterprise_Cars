# -*- coding: utf-8 -*-
# from odoo import http


# class PeasPaymentDashboard(http.Controller):
#     @http.route('/peas_payment_dashboard/peas_payment_dashboard', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/peas_payment_dashboard/peas_payment_dashboard/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('peas_payment_dashboard.listing', {
#             'root': '/peas_payment_dashboard/peas_payment_dashboard',
#             'objects': http.request.env['peas_payment_dashboard.peas_payment_dashboard'].search([]),
#         })

#     @http.route('/peas_payment_dashboard/peas_payment_dashboard/objects/<model("peas_payment_dashboard.peas_payment_dashboard"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('peas_payment_dashboard.object', {
#             'object': obj
#         })

 