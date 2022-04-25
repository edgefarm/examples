import os
import asyncio
import logging
import sys
import time
import math
import json
from nats.aio.client import Client as Nats

# Configure these parameter according to your environment
# Needs to start with `EXPORT.` as this is the global export subject
EXPORT_SUBJECT = "EXPORT.acceleration"
# Configurations for data generation
SLEEPTIME_SECS = 0.013
# Configure logging
LOG_STATISTICS_AFTER_ITERATIONS = 1000


async def error_cb(e):
    """ This function is called when an error occurs in NATS context. """
    logging.info(e)


async def main():
    # Connect to nats
    nc = Nats()
    nats_server = os.getenv("NATS_SERVER", "nats://nats.nats:4222")
    credsfile_path = os.getenv("NATS_CREDS_PATH", None)
    options = {
        "servers": [nats_server],
        "ping_interval": 1,
        "max_outstanding_pings": 5,
        "user_credentials": credsfile_path,
        "error_cb": error_cb,
        "max_reconnect_attempts": 10,
    }

    logging.info("Connecting to NATS server: %s", nats_server)
    try:
        await nc.connect(**options)
    except Exception as e:
        logging.error("Error connecting to NATS server: %s", e)
        return

    # Local parameters required for statistics calculation and logging
    counter = 0
    total_size = 0
    timestamp_start = int(time.time())

    # Endless loop
    while True:

        # Genertate data content
        timestamp_ms = int(time.time()*1000.0)
        x = 2 * math.sin(2*timestamp_ms/1000)+2
        y = 1.5 * math.sin(4 * timestamp_ms/1000)+1.5
        z = 2 * math.sin(3 * timestamp_ms/1000)+2

        # Generate an payload
        payload = {
            "timestamp_ms": timestamp_ms,
            "msg_id": counter,
            "sensor1": {
                "x": x,
                "y": y,
                "z": z
            },
            "sensor2": {
                "x": x,
                "y": y,
                "z": z
            },
        }

        # Convert to byte
        bytes_payload = json.dumps(payload).encode('utf-8')

        # Publish to nats
        await nc.publish(EXPORT_SUBJECT, bytes_payload)

        # Just do some calculations to see sent data size
        counter += 1
        total_size += sys.getsizeof(bytes_payload)
        if counter % LOG_STATISTICS_AFTER_ITERATIONS == 0:
            timestamp_now = int(time.time())
            logging.info("Published %d messages in %d seconds. Total size: %d. Byte per Second: %6d.",
                         LOG_STATISTICS_AFTER_ITERATIONS, timestamp_now - timestamp_start, total_size,
                         total_size/(timestamp_now-timestamp_start))
            total_size = 0
            timestamp_start = timestamp_now

        # Sleep between to sends
        await asyncio.sleep(SLEEPTIME_SECS)


if __name__ == "__main__":
    logging.basicConfig(
        level=os.environ.get("LOGLEVEL", "INFO").upper(),
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    asyncio.run(main())
