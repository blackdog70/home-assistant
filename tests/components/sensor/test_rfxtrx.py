"""The tests for the Rfxtrx sensor platform."""
import unittest

from homeassistant.bootstrap import _setup_component
from homeassistant.components import rfxtrx as rfxtrx_core
from homeassistant.const import TEMP_CELSIUS

from tests.common import get_test_home_assistant


class TestSensorRfxtrx(unittest.TestCase):
    """Test the Rfxtrx sensor platform."""

    def setUp(self):
        """Setup things to be run when tests are started."""
        self.hass = get_test_home_assistant(0)
        self.hass.config.components = ['rfxtrx']

    def tearDown(self):
        """Stop everything that was started."""
        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS = []
        rfxtrx_core.RFX_DEVICES = {}
        self.hass.stop()

    def test_default_config(self):
        """Test with 0 sensor."""
        self.assertTrue(_setup_component(self.hass, 'sensor', {
            'sensor': {'platform': 'rfxtrx',
                       'devices':
                           {}}}))
        self.assertEqual(0, len(rfxtrx_core.RFX_DEVICES))

    def test_one_sensor(self):
        """Test with 1 sensor."""
        self.assertTrue(_setup_component(self.hass, 'sensor', {
            'sensor': {'platform': 'rfxtrx',
                       'devices':
                           {'sensor_0502': {
                               'name': 'Test',
                               'packetid': '0a52080705020095220269',
                               'data_type': 'Temperature'}}}}))

        self.assertEqual(1, len(rfxtrx_core.RFX_DEVICES))
        print(rfxtrx_core.RFX_DEVICES)
        entity = rfxtrx_core.RFX_DEVICES['sensor_0502']
        self.assertEqual('Test', entity.name)
        self.assertEqual(TEMP_CELSIUS, entity.unit_of_measurement)
        self.assertEqual(14.9, entity.state)
        self.assertEqual({'Humidity status': 'normal', 'Temperature': 14.9,
                          'Rssi numeric': 6, 'Humidity': 34,
                          'Battery numeric': 9,
                          'Humidity status numeric': 2},
                         entity.device_state_attributes)

    def test_several_sensors(self):
        """Test with 3 sensors."""
        self.assertTrue(_setup_component(self.hass, 'sensor', {
                'sensor': {'platform': 'rfxtrx',
                           'devices':
                               {'sensor_0502': {
                                   'name': 'Test',
                                   'packetid': '0a52080705020095220269',
                                   'data_type': 'Temperature'},
                                   'sensor_0601': {
                                   'name': 'Bath_Humidity',
                                   'packetid': '0a520802060100ff0e0269',
                                   'data_type': 'Humidity'},
                                   'sensor_0601 2': {
                                   'name': 'Bath',
                                   'packetid': '0a520802060100ff0e0269'}}}}))

        self.assertEqual(3, len(rfxtrx_core.RFX_DEVICES))
        device_num = 0
        for id in rfxtrx_core.RFX_DEVICES:
            entity = rfxtrx_core.RFX_DEVICES[id]
            if entity.name == 'Bath_Humidity':
                device_num = device_num + 1
                self.assertEqual('%', entity.unit_of_measurement)
                self.assertEqual(14, entity.state)
                self.assertEqual({'Battery numeric': 9, 'Temperature': 25.5,
                                  'Humidity': 14, 'Humidity status': 'normal',
                                  'Humidity status numeric': 2,
                                  'Rssi numeric': 6},
                                 entity.device_state_attributes)
                self.assertEqual('Bath_Humidity', entity.__str__())
            elif entity.name == 'Bath':
                device_num = device_num + 1
                self.assertEqual(TEMP_CELSIUS, entity.unit_of_measurement)
                self.assertEqual(25.5, entity.state)
                self.assertEqual({'Battery numeric': 9, 'Temperature': 25.5,
                                  'Humidity': 14, 'Humidity status': 'normal',
                                  'Humidity status numeric': 2,
                                  'Rssi numeric': 6},
                                 entity.device_state_attributes)
                self.assertEqual('Bath', entity.__str__())
            elif entity.name == 'Test':
                device_num = device_num + 1
                self.assertEqual(TEMP_CELSIUS, entity.unit_of_measurement)
                self.assertEqual(14.9, entity.state)
                self.assertEqual({'Humidity status': 'normal',
                                  'Temperature': 14.9,
                                  'Rssi numeric': 6, 'Humidity': 34,
                                  'Battery numeric': 9,
                                  'Humidity status numeric': 2},
                                 entity.device_state_attributes)
                self.assertEqual('Test', entity.__str__())

        self.assertEqual(3, device_num)

    def test_discover_sensor(self):
        """Test with discovery of sensor."""
        self.assertTrue(_setup_component(self.hass, 'sensor', {
            'sensor': {'platform': 'rfxtrx',
                       'automatic_add': True,
                       'devices': {}}}))

        event = rfxtrx_core.get_rfx_object('0a520801070100b81b0279')
        event.data = bytearray(b'\nR\x08\x01\x07\x01\x00\xb8\x1b\x02y')
        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS[0](event)

        entity = rfxtrx_core.RFX_DEVICES['sensor_0701']
        self.assertEqual(1, len(rfxtrx_core.RFX_DEVICES))
        self.assertEqual({'Humidity status': 'normal',
                          'Temperature': 18.4,
                          'Rssi numeric': 7, 'Humidity': 27,
                          'Battery numeric': 9,
                          'Humidity status numeric': 2},
                         entity.device_state_attributes)
        self.assertEqual('sensor_0701 : 0a520801070100b81b0279',
                         entity.__str__())

        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS[0](event)
        self.assertEqual(1, len(rfxtrx_core.RFX_DEVICES))

        event = rfxtrx_core.get_rfx_object('0a52080405020095240279')
        event.data = bytearray(b'\nR\x08\x04\x05\x02\x00\x95$\x02y')
        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS[0](event)
        entity = rfxtrx_core.RFX_DEVICES['sensor_0502']
        self.assertEqual(2, len(rfxtrx_core.RFX_DEVICES))
        self.assertEqual({'Humidity status': 'normal',
                          'Temperature': 14.9,
                          'Rssi numeric': 7, 'Humidity': 36,
                          'Battery numeric': 9,
                          'Humidity status numeric': 2},
                         entity.device_state_attributes)
        self.assertEqual('sensor_0502 : 0a52080405020095240279',
                         entity.__str__())

        event = rfxtrx_core.get_rfx_object('0a52085e070100b31b0279')
        event.data = bytearray(b'\nR\x08^\x07\x01\x00\xb3\x1b\x02y')
        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS[0](event)
        entity = rfxtrx_core.RFX_DEVICES['sensor_0701']
        self.assertEqual(2, len(rfxtrx_core.RFX_DEVICES))
        self.assertEqual({'Humidity status': 'normal',
                          'Temperature': 17.9,
                          'Rssi numeric': 7, 'Humidity': 27,
                          'Battery numeric': 9,
                          'Humidity status numeric': 2},
                         entity.device_state_attributes)
        self.assertEqual('sensor_0701 : 0a520801070100b81b0279',
                         entity.__str__())

        # trying to add a switch
        event = rfxtrx_core.get_rfx_object('0b1100cd0213c7f210010f70')
        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS[0](event)
        self.assertEqual(2, len(rfxtrx_core.RFX_DEVICES))

    def test_discover_sensor_noautoadd(self):
        """Test with discover of sensor when auto add is False."""
        self.assertTrue(_setup_component(self.hass, 'sensor', {
            'sensor': {'platform': 'rfxtrx',
                       'automatic_add': False,
                       'devices': {}}}))

        event = rfxtrx_core.get_rfx_object('0a520801070100b81b0279')
        event.data = bytearray(b'\nR\x08\x01\x07\x01\x00\xb8\x1b\x02y')

        self.assertEqual(0, len(rfxtrx_core.RFX_DEVICES))
        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS[0](event)
        self.assertEqual(0, len(rfxtrx_core.RFX_DEVICES))

        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS[0](event)
        self.assertEqual(0, len(rfxtrx_core.RFX_DEVICES))

        event = rfxtrx_core.get_rfx_object('0a52080405020095240279')
        event.data = bytearray(b'\nR\x08\x04\x05\x02\x00\x95$\x02y')
        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS[0](event)
        self.assertEqual(0, len(rfxtrx_core.RFX_DEVICES))

        event = rfxtrx_core.get_rfx_object('0a52085e070100b31b0279')
        event.data = bytearray(b'\nR\x08^\x07\x01\x00\xb3\x1b\x02y')
        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS[0](event)
        self.assertEqual(0, len(rfxtrx_core.RFX_DEVICES))

    def test_update_of_sensors(self):
        """Test with 3 sensors."""
        self.assertTrue(_setup_component(self.hass, 'sensor', {
                'sensor': {'platform': 'rfxtrx',
                           'devices':
                               {'sensor_0502': {
                                   'name': 'Test',
                                   'packetid': '0a52080705020095220269',
                                   'data_type': 'Temperature'},
                                   'sensor_0601': {
                                   'name': 'Bath_Humidity',
                                   'packetid': '0a520802060100ff0e0269',
                                   'data_type': 'Humidity'},
                                   'sensor_0601 2': {
                                   'name': 'Bath',
                                   'packetid': '0a520802060100ff0e0269'}}}}))

        self.assertEqual(3, len(rfxtrx_core.RFX_DEVICES))

        device_num = 0
        for id in rfxtrx_core.RFX_DEVICES:
            entity = rfxtrx_core.RFX_DEVICES[id]
            if entity.name == 'Bath_Humidity':
                device_num = device_num + 1
                self.assertEqual('%', entity.unit_of_measurement)
                self.assertEqual(14, entity.state)
                self.assertEqual({'Battery numeric': 9, 'Temperature': 25.5,
                                  'Humidity': 14, 'Humidity status': 'normal',
                                  'Humidity status numeric': 2,
                                  'Rssi numeric': 6},
                                 entity.device_state_attributes)
                self.assertEqual('Bath_Humidity', entity.__str__())
            elif entity.name == 'Bath':
                device_num = device_num + 1
                self.assertEqual(TEMP_CELSIUS, entity.unit_of_measurement)
                self.assertEqual(25.5, entity.state)
                self.assertEqual({'Battery numeric': 9, 'Temperature': 25.5,
                                  'Humidity': 14, 'Humidity status': 'normal',
                                  'Humidity status numeric': 2,
                                  'Rssi numeric': 6},
                                 entity.device_state_attributes)
                self.assertEqual('Bath', entity.__str__())
            elif entity.name == 'Test':
                device_num = device_num + 1
                self.assertEqual(TEMP_CELSIUS, entity.unit_of_measurement)
                self.assertEqual(14.9, entity.state)
                self.assertEqual({'Humidity status': 'normal',
                                  'Temperature': 14.9,
                                  'Rssi numeric': 6, 'Humidity': 34,
                                  'Battery numeric': 9,
                                  'Humidity status numeric': 2},
                                 entity.device_state_attributes)
                self.assertEqual('Test', entity.__str__())

        self.assertEqual(3, device_num)

        event = rfxtrx_core.get_rfx_object('0a520802060101ff0f0269')
        event.data = bytearray(b'\nR\x08\x01\x07\x01\x00\xb8\x1b\x02y')
        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS[0](event)

        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS[0](event)
        event = rfxtrx_core.get_rfx_object('0a52080705020085220269')
        event.data = bytearray(b'\nR\x08\x04\x05\x02\x00\x95$\x02y')
        rfxtrx_core.RECEIVED_EVT_SUBSCRIBERS[0](event)

        self.assertEqual(3, len(rfxtrx_core.RFX_DEVICES))

        device_num = 0
        for id in rfxtrx_core.RFX_DEVICES:
            entity = rfxtrx_core.RFX_DEVICES[id]
            if entity.name == 'Bath_Humidity':
                device_num = device_num + 1
                self.assertEqual('%', entity.unit_of_measurement)
                self.assertEqual(15, entity.state)
                self.assertEqual({'Battery numeric': 9, 'Temperature': 51.1,
                                  'Humidity': 15, 'Humidity status': 'normal',
                                  'Humidity status numeric': 2,
                                  'Rssi numeric': 6},
                                 entity.device_state_attributes)
                self.assertEqual('Bath_Humidity', entity.__str__())
            elif entity.name == 'Bath':
                device_num = device_num + 1
                self.assertEqual(TEMP_CELSIUS, entity.unit_of_measurement)
                self.assertEqual(51.1, entity.state)
                self.assertEqual({'Battery numeric': 9, 'Temperature': 51.1,
                                  'Humidity': 15, 'Humidity status': 'normal',
                                  'Humidity status numeric': 2,
                                  'Rssi numeric': 6},
                                 entity.device_state_attributes)
                self.assertEqual('Bath', entity.__str__())
            elif entity.name == 'Test':
                device_num = device_num + 1
                self.assertEqual(TEMP_CELSIUS, entity.unit_of_measurement)
                self.assertEqual(13.3, entity.state)
                self.assertEqual({'Humidity status': 'normal',
                                  'Temperature': 13.3,
                                  'Rssi numeric': 6, 'Humidity': 34,
                                  'Battery numeric': 9,
                                  'Humidity status numeric': 2},
                                 entity.device_state_attributes)
                self.assertEqual('Test', entity.__str__())

        self.assertEqual(3, device_num)

        self.assertEqual(3, len(rfxtrx_core.RFX_DEVICES))
