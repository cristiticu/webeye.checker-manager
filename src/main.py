from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from typing import TYPE_CHECKING
import boto3
from context import ApplicationContext
from monitored_webpage.exceptions import MonitoredWebpageNotFound
import settings
from shared.utils import is_after_24_hours

if TYPE_CHECKING:
    from aws_lambda_typing.context import Context
    from aws_lambda_typing.events import SQSEvent

application_context = ApplicationContext()


def process_record(check_request):
    print(f"Processing record {check_request}")

    try:
        u_guid: str = check_request["u_guid"]
        w_guid: str = check_request["w_guid"]
        configuration = check_request["configuration"]

        url: str = configuration["url"]
        zones: list[str] = configuration["zones"]
        save_screenshot = configuration["save_screenshot"] if "save_screenshot" in configuration else False
        timeout = configuration["timeout"] if "timeout" in configuration else None
        accepted_status = configuration["accepted_status"] if "accepted_status" in configuration else None
        check_string = configuration["check_string"] if "check_string" in configuration else None

        try:
            webpage = application_context.monitored_webpages.get(u_guid, url)
        except MonitoredWebpageNotFound:
            print("User does not have requested webpage")
            return None

        datetime_now = datetime.now(timezone.utc)
        screenshot_saved = False

        for zone in zones:
            print(f"Checking from {zone}")

            for region in settings.AVAILABLE_REGIONS[zone]:
                print(f"Checking from {region}")

                lambda_client = boto3.client("lambda", region_name=region)

                should_save_screenshot = save_screenshot and not screenshot_saved and (
                    not webpage.screenshot_m_at or is_after_24_hours(webpage.screenshot_m_at, datetime_now))

                payload = {
                    "u_guid": u_guid,
                    "w_guid": w_guid,
                    "url": url,
                    "c_str": check_string,
                    "accepted_status": accepted_status,
                    "timeout": timeout,
                    "screenshot": should_save_screenshot,
                }

                lambda_client.invoke(
                    FunctionName=f"{settings.LAMBDA_PREFIX}_{settings.SPEED_CHECKER_LAMBDA_NAME}-{region}",
                    InvocationType="Event",
                    Payload=json.dumps(payload)
                )

                if should_save_screenshot:
                    application_context.monitored_webpages.patch_screenshot_m_at(
                        u_guid, url, datetime_now)

                screenshot_saved = True

    except Exception as e:
        print(f"Exception when processing request {check_request}: {e}")
        return None


def lambda_handler(event: "SQSEvent", context: "Context"):
    records = event.get("Records")

    with ThreadPoolExecutor() as executor:
        executor.map(process_record, [json.loads(record.get(
            "body", "")) for record in records], timeout=20)
