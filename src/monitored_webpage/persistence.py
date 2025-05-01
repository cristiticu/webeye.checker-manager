from datetime import datetime
from monitored_webpage.exceptions import MonitoredWebpageNotFound
from monitored_webpage.model import MonitoredWebpage
import settings
from shared.dynamodb import dynamodb_table


class MonitoredWebpagePersistence():
    def __init__(self):
        self.webpages = dynamodb_table(settings.MONITORED_WEBPAGES_TABLE_NAME)

    def get(self, u_guid: str, url: str):
        response = self.webpages.get_item(
            Key={"u_guid": u_guid, "url": url})
        item = response.get("Item")

        if item is None:
            raise MonitoredWebpageNotFound()

        return MonitoredWebpage.from_db_item(item)

    def patch_screenshot_m_at(self, u_guid: str, url: str, screenshot_m_at: datetime):
        self.webpages.update_item(
            Key={"u_guid": u_guid, "url": url},
            UpdateExpression='SET screenshot_m_at = :val',
            ExpressionAttributeValues={
                ':val': screenshot_m_at.isoformat().replace("+00:00", "Z")
            })
