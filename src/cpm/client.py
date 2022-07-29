from functools import wraps
import time

import requests

from cpm.logging import logged
from cpm import settings

def check_errors(request):
    """
    VERSION: 1.0.1
    Properly handles HTTP and other comms related errors.
    """
    @wraps(request)
    def inner_func(cls, method, url, **kwargs):
        request_success = False
        retries = 0
        while not request_success:
            try:
                response = request(cls, method, url, **kwargs)
                response.raise_for_status()
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.SSLError,
            ) as exc:
                cls.logger_error.exception(exc)

                cls.logger.info("Network unstable. Retrying...")
                cls.logger_error.error(
                    "Server URL: %s, failed while trying to connect.", url
                )
                if retries > 60*60*24: # a day
                    # avoid memory leaks
                    raise exc

            except requests.exceptions.HTTPError as exc:
                try:
                    payload = kwargs["data"]
                except KeyError:
                    payload = "none"
                error_message = f"""
                    Server URL: {response.url}, 
                    failed with status code ({response.status_code}).
                    Raw response: {response.content[:50]} 
                    Request payload: {payload}
                """
                cls.logger.error(error_message)
                with open(settings.BASE_DIR / "logs/debug.html", "w+b") as file:
                    file.write(response.content)
                raise exc
            else:
                request_success = True
            time.sleep(1)
            retries += 1
        return response
    return inner_func

@logged
class Client(requests.Session):
    """Main client for the Card Package Manager. Handles a basic CRUD for packages"""
    URL: str = settings.URL
    SCHEME: dict = settings.ITEM_SCHEME
    _last_response: requests.Response = None # for testing and debugging

    DOCS_URL = URL + "docs"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers["Authorization"] = settings.get_keys()
        self._test_scheme()

    @check_errors
    def request(self, *args, **kwargs):
        res = super().request(*args, **kwargs)
        _last_response = res
        return res

    def _test_scheme(self):
        """
        Tests the internal item scheme against the server's (also checking if it's up).
        Doesn't chech types.
        """
        res = self.get(self.DOCS_URL)
        try:
            scheme = res.json()["urls"]["/"]["scheme"]
        except KeyError:
            raise AssertionError("The sheme has been updated.")
        del scheme["id"] # we don't use id
        assert scheme.keys() == self.SCHEME.keys(), set(scheme.keys()).difference(set(self.SCHEME))

    def list_item(self, page: int = 0, tags: list = None, name: str = None):
        """
        List the catalog.

        :data page: page number
        :data tags: list of tags to query (AND)
        :data name: name to search for (%name%)
        """
        url: str = self.URL
        args: list = []

        if page != 0:
            args.append("page=" + str(page))
        if tags is not None:
            args.append(" ".join(tags))
        if name is not None:
            args.append("name=" + name)
        if args:
            url = f"{url}?{'&'.join(args)}"

        res = self.get(url)

        return res.json()

    def get_item(self, name):
        """Get the details of a package"""
        res = self.get(self.URL + name)
        return res.json()

    def create_item(self, data: dict):
        """Create a package. The scheme is enforced."""
        for key in data.keys():
            assert key in self.SCHEME.keys(), key

        res = self.post(self.URL, json=data)
        return res.json()

    def update_item(self, data: dict, name: str):
        """
        Update an item.
        Could be a partial update so we don't enforce the scheme
        however, all keys must be valid.
        """
        for key in data.keys():
            assert key in self.SCHEME.keys(), key
        res = self.post(self.URL + name, json=data)
        assert any(res.json()["tags"])
        return res.json()
