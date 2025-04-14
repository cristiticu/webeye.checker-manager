from monitored_webpage.persistence import MonitoredWebpagePersistence
from monitoring_events.persistence import MonitoringEventsPersistence


class ApplicationContext():
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(ApplicationContext, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.monitored_webpages = MonitoredWebpagePersistence()
        self.events = MonitoringEventsPersistence()
