from datetime import datetime
from typing import Mapping
from pydantic import UUID4, BaseModel


class CurrentStatus(BaseModel):
    user_guid: UUID4
    url: str
    check_type: str
    last_checked_from: str
    status: str
    added_at: datetime | None = None

    @classmethod
    def from_db_item(cls, item: Mapping):
        split_h_key = item["h_key"].split("#")

        item_payload = {
            **item,
            "user_guid": split_h_key[0],
            "url": split_h_key[1],
            "check_type": split_h_key[2],
        }

        return CurrentStatus.model_validate(item_payload)
