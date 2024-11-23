import unittest
from request_processor import create_widget

class TestRequestProcessor(unittest.TestCase):
    def test_create_widget_with_other_attributes(self):
        request = {
            'widgetId': 'w123',
            'owner': 'John Doe',
            'label': 'Test Widget',
            'description': 'A widget for testing',
            'otherAttributes': [
                {'name': 'color', 'value': 'blue'},
                {'name': 'size', 'value': 'medium'}
            ]
        }
        widget = create_widget(request)
        self.assertEqual(widget['widgetId'], 'w123')
        self.assertEqual(widget['owner'], 'John Doe')
        self.assertEqual(widget['label'], 'Test Widget')
        self.assertEqual(widget['description'], 'A widget for testing')
        self.assertEqual(widget['color'], 'blue')
        self.assertEqual(widget['size'], 'medium')

    def test_create_widget_without_other_attributes(self):
        request = {
            'widgetId': 'w456',
            'owner': 'Jane Smith',
            'label': 'Another Widget',
            'description': 'Another widget for testing',
        }
        widget = create_widget(request)
        self.assertEqual(widget['widgetId'], 'w456')
        self.assertEqual(widget['owner'], 'Jane Smith')
        self.assertEqual(widget['label'], 'Another Widget')
        self.assertEqual(widget['description'], 'Another widget for testing')
        self.assertNotIn('color', widget)
        self.assertNotIn('size', widget)

    def test_create_widget_missing_required_fields(self):
        request = {
            'widgetId': 'w789',
            'owner': 'Alice Johnson',
            'otherAttributes': [
                {'name': 'weight', 'value': '1kg'}
            ]
        }
        widget = create_widget(request)
        self.assertEqual(widget['widgetId'], 'w789')
        self.assertEqual(widget['owner'], 'Alice Johnson')
        self.assertIsNone(widget.get('label'))
        self.assertIsNone(widget.get('description'))
        self.assertEqual(widget['weight'], '1kg')

if __name__ == '__main__':
    unittest.main()
