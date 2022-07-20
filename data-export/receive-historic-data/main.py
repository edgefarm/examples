import os
import asyncio
import logging
import signal
import json
import time
from nats.aio.client import Client as Nats
import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load config file
dotenv_path = Path('..')
load_dotenv()

if os.getenv("NATS_SERVER") is None:
    sys.exit('env variable NATS_SERVER must be set')

# Load nats server from environment variable
NATS_SERVER = os.getenv("NATS_SERVER")

# Configurations for network
NATS_CREDS_PATH = "../natsEndpoint.creds"
EXPORT_SUBJECT = "*.export.acceleration"
CONSUMER = "myconsumer"
STREAM_NAME = "data-export-network_data-export-stream-aggregate"

nc = Nats()
up_to_date = False

# Open csv file in append mode, create if not exists.
csv_file_path = os.getenv("CSV_FILE", "data.csv")
csv_file = open(csv_file_path, "a+")


async def error_cb(e):
    logging.info(e)


async def main():
    loop = asyncio.get_event_loop()

    # Connect to global nats
    credsfile_path = os.getenv("NATS_CREDS_PATH", "../natsEndpoint.creds")
    options = {
        "servers": [NATS_SERVER],
        "ping_interval": 1,
        "max_outstanding_pings": 5,
        "user_credentials": credsfile_path,
        "error_cb": error_cb,
        "max_reconnect_attempts": 10,
    }

    logging.info("Connecting to NATS server: %s", NATS_SERVER)
    try:
        await nc.connect(**options)
    except Exception as e:
        logging.error("Error connecting to NATS server: %s", e)
        return

    # Create JetStream context.
    js = nc.jetstream()

    async def cb(msg):
        global up_to_date
        await msg.ack()

        data = json.loads(msg.data.decode())["data"]
        logging.debug("Received data: %s" % data)

        if not up_to_date and abs(data["timestamp_ms"] - int(time.time()*1000.0)) < 5000:
            up_to_date = True
            logging.info("Received all historic data. Proceed with live data.")

        # formtat timestamp into a human readable format
        dt_object = datetime.datetime.fromtimestamp(
            int(data["timestamp_ms"])/1000.0)
        date_string = dt_object.strftime("%Y-%m-%d")
        time_string = dt_object.strftime("%H:%M:%S.%f")

        # Get sensor data from message
        x1 = data["sensor1"]["x"]
        y1 = data["sensor1"]["y"]
        z1 = data["sensor1"]["z"]
        x2 = data["sensor2"]["x"]
        y2 = data["sensor2"]["y"]
        z2 = data["sensor2"]["z"]

        # Print data in the following format into csv file:
        # date,time,x1,y1,z1,x2,y2,z2
        # "2020-01-01","00:00:00",1.5235078460966271,2.1941572164732808,3.8712016695848748,1.5235078460966271,2.1941572164732808,3.8712016695848748

        csv_line = "%s,%s,%f,%f,%f,%f,%f,%f" % (
            date_string, time_string, x1, y1, z1, x2, y2, z2)

        logging.debug("Write to file: %s" % csv_line)
        csv_file.write(csv_line + "\n")

    # Create single push based subscriber that is durable across restarts.
    sub = await js.subscribe(EXPORT_SUBJECT, durable=CONSUMER, cb=cb, stream=STREAM_NAME)

    # The following shuts down gracefully when SIGINT or SIGTERM is received
    stop = {"stop": False}

    def signal_handler():
        stop["stop"] = True

    for sig in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(getattr(signal, sig), signal_handler)

    # Fetch and ack messagess from consumer.
    while not stop["stop"]:
        await asyncio.sleep(1)

    logging.info("Shutting down...")
    # Close nats connection
    await sub.unsubscribe(1)
    await asyncio.sleep(1)
    await nc.close()
    # Close file
    csv_file.flush()
    csv_file.close()

if __name__ == "__main__":
    logging.basicConfig(
        level=os.environ.get("LOGLEVEL", "INFO").upper(),
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    asyncio.run(main())
