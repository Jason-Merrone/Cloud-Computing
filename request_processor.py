import json
import logging
from widget_storage import Storage

def process_request(data, storage_strategy, resource_name):
    logger = logging.getLogger(__name__)
    try:
        request = json.loads(data)
        request_type = request.get('type')
        if request_type == 'create':
            widget = create_widget(request)
            storage = Storage(storage_strategy, resource_name)
            storage.store_widget(widget)
            logger.info(f'Widget {widget["widgetId"]} created successfully.')
        elif request_type == 'delete':
            logger.warning('Delete request received, but delete functionality is not implemented yet.')
        elif request_type == 'update':
            logger.warning('Update request received, but update functionality is not implemented yet.')
        else:
            logger.error(f'Unknown request type: {request_type}')
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON data: {e}')

def create_widget(request):
    widget = {
        'widgetId': request['widgetId'],
        'owner': request['owner'],
        'label': request.get('label'),
        'description': request.get('description'),
    }
    if 'otherAttributes' in request:
        for attr in request['otherAttributes']:
            name = attr['name']
            value = attr['value']
            widget[name] = value
    return widget
