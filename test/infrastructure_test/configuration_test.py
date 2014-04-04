import unittest
import os
import sys
import json
import hashlib
from StringIO import StringIO

from mock import patch, MagicMock

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from infrastructure.configuration import ConfigurationManager

class ConfigurationManagerTests(unittest.TestCase):
    default_config = {
            'name' : "Unnamed Printer",
            'output_bit_depth' : 16,
            'output_sample_frequency' : 48000,
            'on_modulation_frequency' : 12000,
            'off_modulation_frequency' : 8000,
            'input_bit_depth' : 16,
            'input_sample_frequency' : 48000,
            'sublayer_height_mm' : 0.1,
            'configurationbounds_mm' : [
                    [1.0,1.0,0.0],[1.0,-1.0,0.0],[-1.0,-1.0,0.0],[-1.0,1.0,0.0],
                    [1.0,1.0,1.0],[1.0,-1.0,1.0],[-1.0,-1.0,1.0],[-1.0,1.0,1.0]
                ],
            }
    def test_new_creates_a_new_configution_dict_with_sane_values(self):
        cm = ConfigurationManager()

        actual =  cm.new()
        expected = self.default_config
        self.assertEquals(expected, actual)

    @patch.object(os.path, 'exists')
    @patch.object(os, 'makedirs')
    def test_save_printers_configuration_dictionary_to_peachyprintertools_folder_in_home(self,mock_makedirs,mock_exists):
        mock_exists.return_value = True
        printer_name = "Test1"
        printer_name_hash = hashlib.md5(printer_name).hexdigest()
        expected_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools', printer_name_hash + '.cfg' )

        with patch('infrastructure.configuration.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=file)
            cm = ConfigurationManager()
            data = cm.new()
            data['name'] = printer_name
            cm.save(data)

        self.assertFalse(mock_makedirs.called)
        mock_open.assert_called_with(expected_path, 'w')
        file_handle = mock_open.return_value.__enter__.return_value
        file_handle.write.assert_called_with(json.dumps(data))

    @patch.object(os.path, 'exists')
    @patch.object(os, 'makedirs')
    def test_save_should_create_data_folder_if_it_does_not_exist(self,mock_makedirs,mock_exists):
        mock_exists.return_value = False
        expected_path =  expected_path = os.path.join(os.path.expanduser('~'), '.peachyprintertools')
        with patch('infrastructure.configuration.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=file)
            cm = ConfigurationManager()
            data = cm.new()
            data['name'] = "Test1"
            cm.save(data)

        mock_makedirs.assert_called_with(expected_path)

    @patch.object(os.path, 'exists')
    @patch.object(os, 'makedirs')
    def test_save_should_throw_exception_when_missing_fields(self,mock_makedirs,mock_exists):
        with patch('infrastructure.configuration.open', create=True) as mock_open:
            cm = ConfigurationManager()
            data = cm.new()
            data['name'] = "Test1"
            del data['output_bit_depth']
            with self.assertRaises(Exception): 
                cm.save(data)

    @patch.object(os.path, 'exists')
    def test_list_should_return_empty_list_when_folder_doesnt_exist(self, mock_exists):
        mock_exists.return_value = False
        with patch('infrastructure.configuration.open', create=True) as mock_open:
            cm = ConfigurationManager()
            self.assertEquals([] , cm.list())

    @patch.object(os.path, 'exists')
    @patch.object(os, 'listdir')
    def test_list_should_return_empty_list_when_folder_contains_no_configurations(self, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = []
        with patch('infrastructure.configuration.open', create=True) as mock_open:
            cm = ConfigurationManager()
            self.assertEquals([] , cm.list())

    @patch.object(os.path, 'exists')
    @patch.object(os, 'listdir')
    def test_list_should_return_name_of_configurations(self, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = [ 'blabla.cfg' ]
        expected = [ self.default_config['name'] ]
        with patch('infrastructure.configuration.open', create=True) as mock_open:
            mock_open.return_value = StringIO(json.dumps(self.default_config))
            cm = ConfigurationManager()
            actual = cm.list()
            self.assertEquals(expected, actual)

if __name__ == '__main__':
    unittest.main()