from odoo import models, fields

class TriggerEvent(models.Model):
    _name = 'trigger.event'
    _description = 'Trigger Event'

    name = fields.Char(string='Name', required=True)
