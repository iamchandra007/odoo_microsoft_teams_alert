from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)

class TeamsAlert(models.Model):
    _name = 'teams.alert'
    _description = 'Teams Alert'

    name = fields.Char(string='Name', required=True)
    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade', required=True, 
                               domain="[('transient', '=', False), ('model', 'not like', 'ir.%')]")
    trigger_events = fields.Many2many('trigger.event', 'teams_alert_trigger_event_rel', 
                                      'alert_id', 'event_id', string='Trigger Events', required=True)
    message_template = fields.Text(string='Message Template', required=True)
    custom_condition = fields.Char(string='Custom Condition')
    webhook_urls = fields.One2many('teams.alert.webhook', 'alert_id', string='Webhook URLs', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string='Status', readonly=True, default='draft')

    def action_draft(self):
        for record in self:
            record.state = 'draft'
        return True

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
        return True
    
            

    def _send_alert(self, record, action, additional_data=None):
        # Ensure the record exists and has data
        if not record:
            _logger.error('Record not found or is empty')
            return

        # Initialize default values for record attributes
        record_id = record.get('id') if isinstance(record, dict) else record.id
        model_name = record.get('_name') if isinstance(record, dict) else record._name

        # Check if record is a dictionary or an Odoo record object
        if isinstance(record, dict):
            # For dictionary, simulate the `read` method
            record_data = {field: 'N/A' for field in self._fields}
        else:
            # For Odoo record object, use the `read` method
            record_data = record.read()[0]  # Get the first item of the record data

        # Build facts for the MessageCard
        facts = [
            {"name": "Alert Type:", "value": action.title()},
            {"name": "Record ID:", "value": str(record_id)},
            {"name": "Model:", "value": model_name}
        ]

        # Include specific fields from the record data
        specific_fields = [
            'name', 'display_name', 'create_uid', 'create_date', 
            'write_uid', 'write_date'
        ]
        for field in specific_fields:
            value = record_data.get(field, 'N/A')
            if isinstance(value, tuple):
                value = value[1]  # Get the display name for Many2one fields
            facts.append({"name": f"{field.replace('_', ' ').title()}:", "value": str(value)})

        # Include additional data if present
        if additional_data:
            for key, value in additional_data.items():
                facts.append({"name": f"{key.replace('_', ' ').title()}:", "value": str(value)})

        # Fetch base URL and logo from the configuration
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        logo_url = self.env['ir.config_parameter'].sudo().get_param('web.company.logo_url') or "https://your-default-logo-url.com/logo.png"

        # MessageCard payload for Microsoft Teams
        message_card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": "Alert from Odoo System",
            "themeColor": "0076D7",
            "title": f"Odoo Teams Alert: {self.name}",
            "sections": [
                {
                    "activityTitle": "New Alert Notification",
                    "activitySubtitle": "Odoo System",
                    "activityImage": logo_url,  # Dynamically fetched logo URL
                    "facts": facts,
                    "markdown": True
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "View Record",
                    "targets": [
                        {
                            "os": "default",
                            "uri": f"{base_url}/web#id={record_id}&model={model_name}"  # Dynamically fetched base URL
                        }
                    ]
                },
                {
                    "@type": "HttpPOST",
                    "name": "Acknowledge Alert",
                    "target": f"{base_url}/api/acknowledge_alert",  # Dynamically fetched base URL
                    "body": f"{{\"alert_id\": \"{record_id}\"}}"
                }
            ]
        }

        for webhook in self.webhook_urls:
            try:
                requests.post(webhook.url, json=message_card)
            except Exception as e:
                _logger.error('Error sending alert: %s', e)





                

    def _evaluate_custom_condition(self, record):
        if self.custom_condition:
            try:
                # Define a safe environment for eval
                safe_locals = {
                    'record': record,
                    'fields': fields
                }
                # Evaluate the custom condition
                result = eval(self.custom_condition, {"__builtins__": None}, safe_locals)
                _logger.info('Condition %s result: %s', self.custom_condition, result)
                return result
            except Exception as e:
                _logger.error('Error evaluating custom condition: %s', e)
                return False
        return False


class TeamsAlertWebhook(models.Model):
    _name = 'teams.alert.webhook'
    _description = 'Teams Alert Webhook'

    alert_id = fields.Many2one('teams.alert', string='Alert')
    url = fields.Char(string='Webhook URL', required=True)
