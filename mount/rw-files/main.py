import os
import datetime
import logging
import time

defaultReadFile = "/path-in-container/read-file"
defaultWriteFile = "/path-in-container/write-file"


def main():

    # Read read file names if provided
    readFile = defaultReadFile
    writeFile = defaultWriteFile
    if os.getenv("READ_FILE") is not None:
        readFile = os.getenv("READ_FILE")
    if os.getenv("WRITE_FILE") is not None:
        writeFile = os.getenv("WRITE_FILE")

    # If read file does not exist, create it
    if not os.path.isfile(readFile):
        f = open(readFile, "x")
        f.close()

    # Open files
    rf = open(readFile, 'r')
    wf = open(writeFile, "a+")

    # Endless loop
    while True:
        # Read data from file
        data = rf.readline()

        # If no data, check if file is empty
        if data == "":
            # if file is empty, just update data
            if os.stat(readFile).st_size == 0:
                data = "No data in file\n"
            else:
                # start from the beginning
                rf.seek(0)
                data = "End of file reached\n"

        logging.info('Read data from file: ' + str(data).removesuffix('\n'))

        # Write data to file
        writeString = str(datetime.datetime.now()) + ": " + str(data)
        wf.write(writeString)
        wf.flush()
        logging.info('Wrtie data to file: ' +
                     str(writeString).removesuffix('\n'))
        time.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(
        level=os.environ.get("LOGLEVEL", "INFO").upper(),
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
