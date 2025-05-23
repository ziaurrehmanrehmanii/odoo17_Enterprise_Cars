# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """Initialize required parameters after module installation"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Initialize CRM parameters
    try:
        # Create or update the crm.pls_fields parameter
        param = env['ir.config_parameter'].sudo().get_param('crm.pls_fields')
        if not param:
            env['ir.config_parameter'].sudo().set_param('crm.pls_fields', 'phone_state,email_state,source_id,tag_ids')
            _logger.info("Initialized crm.pls_fields parameter")
    except Exception as e:
        _logger.warning("Failed to initialize CRM parameters: %s", str(e))
