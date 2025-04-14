from datetime import datetime
from typing import Mapping
from pydantic import UUID4, BaseModel


class CurrentStatus(BaseModel):
    u_guid: UUID4
    url: str
    region: str
    status: str
    downtime_s_at: datetime | None = None

    @classmethod
    def from_db_item(cls, item: Mapping):
        split_h_key = item["h_key"].split("#")
        split_s_key = item["s_key"].split("#")

        item_payload = {
            **item,
            "u_guid": split_h_key[0],
            "url": split_h_key[1],
            "region": split_s_key[1]
        }

        return CurrentStatus.model_validate(item_payload)
