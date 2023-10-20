import json
import subprocess
import typing

from ._event import *
from ._status import *


class _FooExample:
    # example getter/setter for module property

    _STATUS_CODES: dict[type[Status], str] = {
        ActiveStatus: "active",
        WaitingStatus: "waiting",
        MaintenanceStatus: "maintenance",
        BlockedStatus: "blocked",
    }

    @property
    def unit_status(self) -> typing.Optional[Status]:
        result = json.loads(
            subprocess.run(
                ["status-get", "--include-data" "--format", "json"],
                check=True,
                capture_output=True,
            ).stdout
        )
        status_types: dict[str, type[Status]] = {
            code: status for status, code in self._STATUS_CODES.items()
        }
        if status_type := status_types.get(result["status"]):
            return status_type(result["message"])

    @unit_status.setter
    def unit_status(self, value: Status) -> None:
        subprocess.run(
            ["status-set", self._STATUS_CODES[type(value)], str(value)], check=True
        )


class Unit(str):
    @property
    def app(self):
        return self.split("/")[0]


class Relation(dict[str, dict[str, str]]):
    @property
    def my_unit(self):
        return self[_unit]

    @my_unit.setter
    def my_unit(self, value):
        self[_unit] = value

    @my_unit.deleter
    def my_unit(self):
        self[_unit].clear()

    @property
    def my_app(self):
        return self[_app]

    @my_app.setter
    def my_app(self, value):
        self[_app] = value

    @my_app.deleter
    def my_app(self):
        self[_app].clear()

    def _get_app_units(self, app: str) -> dict[Unit, dict[str, str]]:
        return {
            unit_or_app: data
            for unit_or_app, data in self.items()
            if isinstance(unit_or_app, Unit) and unit_or_app.app == app
        }

    @property
    def my_units(self):
        return self._get_app_units(_app)


class RemoteRelation(Relation):
    """Relation with remote app"""

    @property
    def _remote_app_name(self):
        remote_apps = {
            unit_or_app
            for unit_or_app in self.keys()
            if not isinstance(unit_or_app, Unit) and unit_or_app != _app
        }
        assert len(remote_apps) == 1
        return remote_apps.pop()

    @property
    def remote_app(self):
        return self[self._remote_app_name]

    @property
    def remote_units(self):
        return self._get_app_units(self._remote_app_name)


_unit = Unit("foo/0")
_app = "foo"
event: Event
is_leader: bool
unit_status = _FooExample().unit_status
app_status: typing.Optional[Status] = None
config = None
juju_version = None
endpoints: dict[str, set[Relation]] = {}
