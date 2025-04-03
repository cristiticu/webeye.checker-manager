from downtime.model import CurrentStatus
from shared.dynamodb import dynamodb_table
import settings


class DowntimePersistence():
    def __init__(self):
        self.downtimes = dynamodb_table(settings.DOWNTIMES_TABLE_NAME)

    def get_current_status(self, user_guid: str, url: str, type: str):
        h_key = f"{user_guid}#{url}#{type}"

        response = self.downtimes.get_item(
            Key={"h_key": h_key, "s_key": "CURRENT"})
        item = response.get("Item")

        if item is not None:
            return CurrentStatus.from_db_item(item)
