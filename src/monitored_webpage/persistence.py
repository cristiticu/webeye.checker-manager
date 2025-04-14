import settings
from shared.dynamodb import dynamodb_table


class MonitoredWebpagePersistence():
    def __init__(self):
        self.webpages = dynamodb_table(settings.MONITORED_WEBPAGES_TABLE_NAME)

    def has_monitored_webpage(self, u_guid: str, url: str):
        response = self.webpages.get_item(
            Key={"u_guid": u_guid, "url": url})
        item = response.get("Item")

        if item is None:
            return False

        return True
