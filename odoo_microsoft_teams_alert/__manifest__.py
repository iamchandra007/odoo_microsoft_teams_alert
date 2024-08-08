{
    'name': 'Odoo Teams Alert System',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Send alerts to Microsoft Teams based on model events, custom conditions, and exceptions',
    'description': """
    <p>This module allows users to configure alerts for various Odoo models and send notifications
    to Microsoft Teams via webhooks. Alerts can be triggered based on standard events like create,
    update, delete, custom conditions defined by the user, or when exceptions occur in any method
    of the models.</p>
    <p>Key Features:</p>
    <ul>
        <li>Customizable alert conditions</li>
        <li>Seamless integration with Microsoft Teams</li>
        <li>Alerts for model create, update, and delete operations</li>
        <li>Alerts for exceptions occur in any method of the models</li>
        <li>Send alerts based on any custom condition</li>
        <li>Easy setup and configuration</li>
    </ul>
    """,
    'author': 'Chandra Prakash Buda',
    'website': 'https://github.com/iamchandra007/odoo_microsoft_teams_alert',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/teams_alert_views.xml',
        'data/trigger_event_data.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/cover.png',
        #"static/description/banner.png",
    ],
    'installable': True,
    'application': True,
}