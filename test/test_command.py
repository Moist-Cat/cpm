import unittest
from unittest.mock import patch, Mock, mock_open

from cpm import command

class TestCommand(unittest.TestCase):

    def setUp(self):
        # mocks
        command.input = Mock()
        self.mock_input = command.input
        command.client = Mock()
        self.mock_client = command.client

        command.open = mock_open()
        self.open = command.open
        command.json = Mock()
        command.yaml = Mock()

        # mocking zipfile is more trouble than what is
        # worth and we don't have much to test here
        command._package = Mock() 

        self.image_url = "https://imgur.io/dwdqw22"
        self.image_name = "image.png"

        self.pkg = {
                "name": "remilia",
                "file": "https://files.catbox.moe/fwefw22",
                "image": "",
                "deps": ["gensokio", "scarlet devil mansion"],
        }
        def test_items(name):
            if name in self.pkg["deps"]:
                return {"name": name, "file": "https://file.com/file", "image": "", "deps": []}
            return self.pkg
        command.client.get_item = test_items 
    
    def tearDown(self):
        pass

    def test_dump_file(self):
        command._dump_file(self.image_url, self.image_name)

        self.open.assert_called()
        self.mock_client.get.assert_called()

    def test_dump_file_bad_url(self):
        command._dump_file(self.image_url.replace("https", "fpt"), self.image_name)

        assert not self.open.called
        assert not self.mock_client.get.called

    def test_download_low(self):
        command._download(self.pkg)

        # the test package doesn't have an image url, therefore
        # 1 call to dump the json
        # 1 call to dump the file
        # 2 * (parent + dependencies)
        self.assertEqual(self.open.call_count, 2*(1 + len(self.pkg["deps"])))
   
    def test_download(self):
       assert False

    def test_get_data(self):
        assert False

    def test_compile(self):
        assert False

    def test_tail(self):
        assert False
