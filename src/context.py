from monitored_webpage.persistence import MonitoredWebpagePersistence


class ThreadSafeApplicationContext():
    def __init__(self):
        self.monitored_webpages = MonitoredWebpagePersistence()
