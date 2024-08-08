from odoo import models, api
import logging
import traceback


_logger = logging.getLogger(__name__)

class BaseModelExtension(models.AbstractModel):
    _name = 'base.model.extension'
    _description = 'Base Model Extension'

    
    def _trigger_alerts(self, record, action, method_name=None, exception=None):
        _logger.info('Triggering alerts for model: %s, action: %s', self._name, action)
        
        alert_model = self.env['teams.alert']
        model_id = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        
        if not model_id:
            _logger.warning('No matching model found for: %s', self._name)
            return

        alerts = alert_model.search([('model_id', '=', model_id.id)])
        
        for alert in alerts:
            trigger_event_names = alert.trigger_events.mapped('name')
            
            if action == 'exception':
                if 'On Exception' in trigger_event_names:
                    _logger.info('On Exception event found, sending alert')
                    tb = traceback.format_exc()
                    additional_data = {
                        'method_name': method_name,
                        'exception_type': type(exception).__name__,
                        'exception_message': str(exception),
                        'traceback': tb
                    }
                    alert._send_alert(record, action, additional_data)
                else:
                    _logger.info('On Exception event not found in trigger events')
            else:
                
                _logger.info('Evaluating alert: %s for action: %s', alert.name, action)
                
                if action in trigger_event_names or 'Custom Condition' in trigger_event_names:
                    _logger.info('Action %s found in trigger events for alert %s', action, alert.name)
                    if 'Custom Condition' in trigger_event_names and not alert._evaluate_custom_condition(record):
                        _logger.info('Custom condition not met for alert %s', alert.name)
                        continue
                    _logger.info('Sending alert %s for action %s', alert.name, action)
                    alert._send_alert(record, action)
                    

    

    @api.model
    def create(self, vals):
        _logger.info('Calling create method')
        try:
            record = super(BaseModelExtension, self).create(vals)
            self._trigger_alerts(record, 'On Create')
            return record
        except Exception as e:
            _logger.error('Exception during create: %s', str(e))
            self._trigger_alerts(self, 'exception', method_name='create', exception=e)
            raise

    def write(self, vals):
        _logger.info('Calling write method')
        try:
            result = super(BaseModelExtension, self).write(vals)
            self._trigger_alerts(self, 'On Update')
            return result
        except Exception as e:
            _logger.error('Exception during update: %s', str(e))
            self._trigger_alerts(self, 'exception', method_name='write', exception=e)
            raise

    def unlink(self):
        _logger.info('Calling unlink method')
        try:
            for record in self:
                self._trigger_alerts(record, 'On Delete')
            return super(BaseModelExtension, self).unlink()
        except Exception as e:
            _logger.error('Exception during delete: %s', str(e))
            self._trigger_alerts(self, 'exception', method_name='unlink', exception=e)
            raise
