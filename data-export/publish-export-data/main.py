import os
import asyncio
import logging
import sys
import time
import math
import json
from dapr.clients import DaprClient
import grpc

# Configure these parameter according to your environment
# Needs to start with `export.` as this is the global export subject
EXPORT_SUBJECT = "export.acceleration"
NETWORK_NAME = "data-export-network"
# Configurations for data generation
SLEEPTIME_SECS = 0.013
# Configure logging
LOG_STATISTICS_AFTER_ITERATIONS = 1000


async def error_cb(e):
    """ This function is called when an error occurs in NATS context. """
    logging.info(e)


async def main():
    # Initialize dapr client
    dapr_client = DaprClient(address=os.getenv(
        "DAPR_GRPC_ADDRESS", "localhost:3500"))

    node_name = os.getenv("NODE_NAME")

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
            "sensor1": {"x": x, "y": y, "z": z},
            "sensor2": {"x": x, "y": y, "z": z},
        }

        # Create a typed message with content type and body
        try:
            resp = dapr_client.publish_event(
                pubsub_name=NETWORK_NAME,
                topic_name=node_name+"."+EXPORT_SUBJECT,
                data=json.dumps(payload),
                data_content_type='application/json',
            )
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                logging.info(
                    "GRPC connection to dapr unavailable. Retrying...")
                time.sleep(1)
                continue
            else:
                logging.error("Received unknown RPC error: %s", rpc_error)
                break

        # print(resp.get_headers())
        if len(resp.get_headers()) != 0:
            logging.error("Unexpected response received: %s",
                          resp.get_headers())

        # Just do some calculations to see sent data size
        counter += 1
        total_size += sys.getsizeof(payload)
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
