from odoo.exceptions import UserError
# In utils.py
from functools import wraps
import logging
import traceback

_logger = logging.getLogger(__name__)

def exception_alert(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            result = method(self, *args, **kwargs)
            return result
        except Exception as e:
            tb = traceback.format_exc()
            tb_lines = tb.splitlines()
            line_number = tb_lines[-1] if tb_lines else "Unknown Line"
            
            _logger.error('Exception in method %s: %s', method.__name__, e)
            
            # Trigger alert with minimal data
            if hasattr(self, 'env'):
                model_name = getattr(self, '_name', 'unknown_model')
                record_id = getattr(self, 'id', 'unknown_id')

                # Create a dummy record object to pass to _trigger_alerts
                dummy_record = {
                    'id': record_id,
                    '_name': model_name,
                    'read': lambda fields: {field: 'N/A' for field in fields}
                }
                
                # Trigger alert with method name and exception
                self._trigger_alerts(
                    dummy_record, 
                    'exception', 
                    method_name=method.__name__, 
                    exception=e
                )
            else:
                _logger.error('Self does not have env attribute, cannot trigger alert')
            
            raise
    return wrapper



