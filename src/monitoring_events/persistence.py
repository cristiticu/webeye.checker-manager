from monitoring_events.model import CurrentStatus
from shared.dynamodb import dynamodb_table
import settings


class MonitoringEventsPersistence():
    def __init__(self):
        self.events = dynamodb_table(settings.MONITORING_EVENTS_TABLE_NAME)

    def get_current_status(self, u_guid: str, url: str, region: str):
        h_key = f"{u_guid}#{url}"
        s_key = f"CURRENT#{region}"

        response = self.events.get_item(
            Key={"h_key": h_key, "s_key": s_key})
        item = response.get("Item")

        if item is not None:
            return CurrentStatus.from_db_item(item)
