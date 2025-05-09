odoo.define('peas_payment_dashboard.dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var _t = core._t;
    odoo.define(
        'peas_payment_dashboard.dashboard',
        ['web.core', 'web.AbstractAction', 'web.rpc'],
        function (require) {
            "use strict";
            var core = require('web.core');
            var AbstractAction = require('web.AbstractAction');
            var rpc = require('web.rpc');
            var QWeb = core.qweb;
            var _t = core._t;
            /* … rest of your code … */
            core.action_registry.add('peas_dashboard_action', PeasDashboard);
            return PeasDashboard;
        }
    );
    // Dashboard widget
    var PeasDashboard = AbstractAction.extend({
        template: 'PeasDashboard',
        events: {
            'click .o_peas_view_all': '_onClickViewAll',
            'click .o_peas_open_payment': '_onClickOpenPayment',
            'click .o_peas_load_users': '_onClickLoadUsers',
        },

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.actionManager = parent;
            this.action = action;
        },

        willStart: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return self._fetchDashboardData();
            });
        },

        _fetchDashboardData: function () {
            var self = this;
            return rpc.query({
                model: 'peas.payment',
                method: 'get_dashboard_data',
                args: [],
            }).then(function (result) {
                self.dashboardData = result;
            });
        },

        _onClickViewAll: function (ev) {
            ev.preventDefault();
            this.do_action({
                name: _t('PEAS Payments'),
                type: 'ir.actions.act_window',
                res_model: 'peas.payment',
                views: [[false, 'list'], [false, 'form']],
                target: 'current',
            });
        },

        _onClickOpenPayment: function (ev) {
            ev.preventDefault();
            var paymentId = $(ev.currentTarget).data('id');
            if (paymentId) {
                this.do_action({
                    name: _t('Payment'),
                    type: 'ir.actions.act_window',
                    res_model: 'peas.payment',
                    res_id: paymentId,
                    views: [[false, 'form']],
                    target: 'current',
                });
            }
        },

        _onClickLoadUsers: function (ev) {
            ev.preventDefault();
            var self = this;

            rpc.query({
                model: 'peas.dashboard',
                method: 'load_peas_employees',
                args: [],
            }).then(function () {
                self.do_action({
                    name: _t('PEAS Users'),
                    type: 'ir.actions.act_window',
                    res_model: 'peas.dashboard',
                    views: [[false, 'list'], [false, 'form']],
                    target: 'current',
                });
            });
        }
    });

    core.action_registry.add('peas_dashboard_action', PeasDashboard);
    return PeasDashboard;
});