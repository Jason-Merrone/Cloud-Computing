import json
import logging
from widget_storage import Storage

def process_request(data, storage_strategy, resource_name):
    logger = logging.getLogger(__name__)
    try:
        request = json.loads(data)
        request_type = request.get('type')

        storage = Storage(storage_strategy, resource_name)

        if request_type == 'create':
            widget = create_widget(request)
            storage.store_widget(widget)
            logger.info(f'Widget {widget["widgetId"]} created successfully.')
        elif request_type == 'delete':
            widget_id = request.get('widgetId')
            if widget_id:
                storage.delete_widget(widget_id)
                logger.info(f'Widget {widget_id} deleted successfully.')
            else:
                logger.error('Delete request missing widgetId.')
        elif request_type == 'update':
            widget = create_widget(request)
            storage.update_widget(widget)
            logger.info(f'Widget {widget["widgetId"]} updated successfully.')
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
