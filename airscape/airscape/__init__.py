"""Module for Controlling AirScape Whole House Fans."""
__version__ = "0.1.2"

import re
import json
from time import sleep

import requests
from . import exceptions as ex

DEFAULT_TIMEOUT = 5


class Fan:
    """Class representing a fan.

    Constructor has one required parameter.
    IP or host name of fan to control.
    """

    def __init__(self, host, timeout=DEFAULT_TIMEOUT):
        """Initialize a fan."""
        self._command_api = "http://" + host + "/fanspd.cgi"
        self._status_api = "http://" + host + "/status.json.cgi"
        self._timeout = timeout
        self._data = {}
        self.get_device_state()

    @property
    def is_on(self) -> bool:
        """Get the fan state.

        True if on. False if off.
        """
        return bool(self._data["fanspd"])

    @is_on.setter
    def is_on(self, state: bool) -> None:
        """Set the fan state.

        True on. False off.
        """
        if state and self._data["fanspd"] == 0:
            self.set_device_state(1)
        elif not state:
            self.set_device_state(4)

    @property
    def speed(self) -> int:
        """Get the fan speed.

        Returns int between 1 and 6.
        """
        return self._data["fanspd"]

    @speed.setter
    def speed(self, speed: int) -> None:
        """Set the fan speed to a specific rate."""
        command = 1
        if speed < self._data["fanspd"]:
            command = 3
        while self._data["fanspd"] != speed:
            self.set_device_state(command)
            sleep(0.75)

    def speed_up(self):
        """Increase fan speed by 1."""
        if 1 <= self._data["fanspd"] <= 9:
            self.set_device_state(1)

    def slow_down(self):
        """Decrease fan speed by 1."""
        if 2 <= self._data["fanspd"] <= 10:
            self.set_device_state(3)

    def get_device_state(self):
        """Get refresh data from fan.

        Function returns Dict of fan state data.
        """
        try:
            api = requests.get(self._status_api)
        except requests.exceptions.ConnectionError:
            raise ex.ConnectionError from requests.exceptions.ConnectionError
        except requests.exceptions.ReadTimeout:
            raise ex.Timeout from requests.exceptions.ReadTimeout
        else:
            clean_text = re.sub(r".*server_response.*", "", api.text)
            self._data = json.loads(clean_text)
            return self._data

    def set_device_state(self, payload) -> None:
        """Set state of fan.

        Calls the fan API via GET the only supported parameter.
        """
        try:
            requests.get(
                self._command_api,
                params={"dir": payload},
                timeout=self._timeout
            )
        except requests.exceptions.ConnectionError:
            raise ex.ConnectionError from requests.exceptions.ConnectionError
        except requests.exceptions.ReadTimeout:
            raise ex.Timeout from requests.exceptions.ReadTimeout
        else:
            self.get_device_state()
