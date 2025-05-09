# -*- coding: utf-8 -*-
# from odoo import http


# class PeasAdvanceDashboard(http.Controller):
#     @http.route('/peas_advance_dashboard/peas_advance_dashboard', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/peas_advance_dashboard/peas_advance_dashboard/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('peas_advance_dashboard.listing', {
#             'root': '/peas_advance_dashboard/peas_advance_dashboard',
#             'objects': http.request.env['peas_advance_dashboard.peas_advance_dashboard'].search([]),
#         })

#     @http.route('/peas_advance_dashboard/peas_advance_dashboard/objects/<model("peas_advance_dashboard.peas_advance_dashboard"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('peas_advance_dashboard.object', {
#             'object': obj
#         })

