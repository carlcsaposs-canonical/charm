import os

from . import _status
from ._status import (
    Status,
    ActiveStatus,
    WaitingStatus,
    MaintenanceStatus,
    BlockedStatus,
)


class Unit(str):
    @property
    def app(self):
        return self.split("/")[0]


class Relation:
    def __init__(self, *, data: dict[str, dict[str, str]], id_: int):
        self.data = data
        self.id = id_
        """Unique within a Juju model"""

    @property
    def my_unit(self):
        return self.data[state.unit]

    @my_unit.setter
    def my_unit(self, value):
        self.data[state.unit] = value

    @my_unit.deleter
    def my_unit(self):
        self.data[state.unit].clear()

    @property
    def my_app(self):
        return self.data[state.app]

    @my_app.setter
    def my_app(self, value):
        self.data[state.app] = value

    @my_app.deleter
    def my_app(self):
        self.data[state.app].clear()

    def _get_app_units(self, app_: str) -> dict[Unit, dict[str, str]]:
        return {
            unit_or_app: data
            for unit_or_app, data in self.data.items()
            if isinstance(unit_or_app, Unit) and unit_or_app.app == app_
        }

    @property
    def my_units(self):
        return self._get_app_units(state.app)

    @property
    def breaking(self):
        event = state.event
        return isinstance(event, RelationBrokenEvent) and event.relation == self


class RemoteRelation(Relation):
    """Relation with remote app"""

    @property
    def _remote_app_name(self):
        remote_apps = {
            unit_or_app
            for unit_or_app in self.data.keys()
            if not isinstance(unit_or_app, Unit) and unit_or_app != state.app
        }
        assert len(remote_apps) == 1
        return remote_apps.pop()

    @property
    def remote_app(self):
        return self.data[self._remote_app_name]

    @property
    def remote_units(self):
        return self._get_app_units(self._remote_app_name)


class Event:
    pass


class ConfigChangedEvent(Event):
    pass


class InstallEvent(Event):
    pass


class LeaderElectedEvent(Event):
    pass


class LeaderSettingsChangedEvent(Event):
    pass


class PostSeriesUpgradeEvent(Event):
    pass


class PreSeriesUpgradeEvent(Event):
    pass


class RemoveEvent(Event):
    pass


class StartEvent(Event):
    pass


class StopEvent(Event):
    pass


class UpdateStatusEvent(Event):
    pass


class UpgradeCharmEvent(Event):
    pass


# todo secrets, actions, pebble ready, storage


class _DynamicallyNamedEvent(Event):
    def __init__(self, *, dynamic_name: str):
        self._dynamic_name = dynamic_name


class RelationEvent(_DynamicallyNamedEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # todo: confirm correct env var for endpoint name
        relations = [
            relation
            for relation in state.endpoints[os.environ["JUJU_RELATION"]]
            if relation.id == os.environ["JUJU_RELATION_ID"]
        ]
        assert len(relations) == 1
        self.relation = relations[0]


class RelationBrokenEvent(RelationEvent):
    pass


class RelationCreatedEvent(RelationEvent):
    pass


class _RelationUnitEvent(RelationEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remote_unit = Unit(os.environ["JUJU_REMOTE_UNIT"])


class RelationChangedEvent(_RelationUnitEvent):
    pass


class RelationDepartedEvent(_RelationUnitEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.departing_unit = Unit(os.environ["JUJU_DEPARTING_UNIT"])


class RelationJoinedEvent(_RelationUnitEvent):
    pass


_STATICALLY_NAMED_EVENT_TYPES: dict[str, type[Event]] = {
    "config-changed": ConfigChangedEvent,
    "install": InstallEvent,
    "leader-elected": LeaderElectedEvent,
    "leader-settings-changed": LeaderSettingsChangedEvent,
    "post-series-upgrade": PostSeriesUpgradeEvent,
    "pre-series-upgrade": PreSeriesUpgradeEvent,
    "remove": RemoveEvent,
    "start": StartEvent,
    "stop": StopEvent,
    "update-status": UpdateStatusEvent,
    "upgrade-charm": UpgradeCharmEvent,
}
_DYNAMICALLY_NAMED_EVENT_TYPES: dict[str, type[_DynamicallyNamedEvent]] = {
    # todo secrets, actions, pebble ready, storage
    "-relation-broken": RelationBrokenEvent,
    "-relation-changed": RelationChangedEvent,
    "-relation-created": RelationCreatedEvent,
    "-relation-departed": RelationDepartedEvent,
    "-relation-joined": RelationJoinedEvent,
}


class State:
    @property
    def event(self) -> Event:
        _name = os.environ["JUJU_HOOK_NAME"]
        try:
            return _STATICALLY_NAMED_EVENT_TYPES[_name]()
        except KeyError:
            for suffix, type_ in _DYNAMICALLY_NAMED_EVENT_TYPES.items():
                if _name.endswith(suffix):
                    return type_(dynamic_name=_name.removesuffix(suffix))
            raise

    @property
    def unit(self) -> Unit:
        return Unit(os.environ["JUJU_UNIT_NAME"])

    @property
    def app(self) -> str:
        return self.unit.app

    @property
    def model(self) -> str:
        return os.environ["JUJU_MODEL_NAME"]

    @property
    def model_uuid(self) -> str:
        return os.environ["JUJU_MODEL_UUID"]

    @property
    def juju_version(self) -> str:
        # todo: add type (e.g. has_secrets property)
        return os.environ["JUJU_VERSION"]

    @property
    def is_leader(self) -> bool:
        raise NotImplementedError

    @property
    def config(self):
        raise NotImplementedError

    @property
    def endpoints(self) -> dict[str, list[Relation]]:
        return {}

    @property
    def unit_status(self):
        return _status.get_status()

    @unit_status.setter
    def unit_status(self, value: Status):
        _status.set_status(value)

    @property
    def app_status(self):
        return _status.get_status(app=True)

    @app_status.setter
    def app_status(self, value: Status):
        _status.set_status(value, app=True)


state = State()
