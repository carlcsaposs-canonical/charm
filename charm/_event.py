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
