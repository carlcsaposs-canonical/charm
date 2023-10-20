import subprocess
import typing

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



unit_status = _FooExample().unit_status
app_status: typing.Optional[Status] = None
