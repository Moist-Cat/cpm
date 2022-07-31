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
        command.json.load = Mock()
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
                return {
                    "name": name,
                    "file": "https://file.com/file",
                    "image": "",
                    "deps": [],
                }
            return self.pkg

        command.client.get_item = test_items

    def tearDown(self):
        pass

    def test_dump_file(self):
        res = command._dump_file(self.image_url, self.image_name)

        self.open.assert_called()
        self.mock_client.get.assert_called()

        self.assertEqual(res._mock_name, self.mock_client.content._mock_name)

    def test_dump_file_bad_url(self):
        res = command._dump_file(
            self.image_url.replace("https", "fpt"), self.image_name
        )

        assert not self.open.called
        assert not self.mock_client.get.called

        assert not res

    def test_download_low(self):
        res = command._download(self.pkg)

        # the test package doesn't have an image url, therefore
        # 1 call to dump the json
        # 1 call to dump the file
        # 2 * (parent + dependencies)
        self.assertEqual(self.open.call_count, 2 * (1 + len(self.pkg["deps"])))
        self.assertEqual(set((self.pkg["name"], *self.pkg["deps"])), res.keys())
        for el in res.values():
            # they are all the return value of res.content
            self.assertEqual(el._mock_name, self.mock_client.content._mock_name)

    def test_get_data(self):
        # Here we rely on the fact that lists are mutable in Python
        # the funtion will be yielding values from an external list
        # mimicking an user providing a different input every time
        els = ["remilia", "", "a,b", "", "", "", ""]

        def data(inpt):
            return els.pop(0)

        command.input = data
        data = command._get_data(None)
        self.assertEqual(data, {"name": "remilia", "tags": ["a", "b"]})

        pkg = self.pkg
        pkg["deps"] = ",".join(self.pkg["deps"])

        command.yaml.safe_load = Mock(return_value=self.pkg)
        data = command._get_data("mock.yaml")
        self.assertEqual(data, self.pkg)

    def test_compile(self):
        template = {"entries": [], "categories": []}
        packages = {
            "remlia": '{"entries": ["dummy_entry"], "categories": []}',
            "sakuya": '{"entries": ["dummy_entry2"], "categories": ["dummy_category"]}',
        }
        res = command._compile(template, packages)

        self.assertEqual(len(res["entries"]), 2, res["entries"])
        self.assertEqual(len(res["categories"]), 1, res["categories"])
