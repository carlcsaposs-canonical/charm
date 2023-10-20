import typing

if typing.TYPE_CHECKING:
    import charm


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


class RelationEvent(Event):
    @property
    def relation(self) -> charm.Relation:
        pass


class RelationBrokenEvent(RelationEvent):
    pass


class RelationChangedEvent(RelationEvent):
    pass


class RelationCreatedEvent(RelationEvent):
    pass


class RelationDepartedEvent(RelationEvent):
    departing_unit: charm.Unit


class RelationJoinedEvent(RelationEvent):
    pass
