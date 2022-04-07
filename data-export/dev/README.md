# dev

This is the dev environment for local debugging.

**Prerequisites:**
- [docker](https://docs.ci4rail.com/edgefarm/reference-manual/prerequisites/docker/) and [docker-compose](https://docs.ci4rail.com/edgefarm/reference-manual/prerequisites/docker-compose/) installed
- [nats cli](https://github.com/nats-io/natscli#installation) installed
- [Visual Studio Code](https://code.visualstudio.com/download) installed

## Usage

**Startup dev environment:**

Startup dev environment locally using a docker container setup:

```bash
$ docker-compose up -d
```

It is required to create the stream manually:
```bash
$ nats -s nats://localhost:4222 stream add test --subjects "EXPORT.*" --ack --max-msgs=100000 --max-bytes=1073741824 --max-age=2d --storage file --retention limits --max-msg-size=-1 --discard old --dupe-window="0s" --replicas 1 --max-msgs-per-subject=-1
```

List all local streams:
```bash
$ nats -s nats://localhost:4222 stream ls
```

**Receive messages transmitted:**

Subscribe to stream subject to receive messages:
```bash
$ nats sub -s nats://localhost:4222 "EXPORT.>"
```

**Start debug sesstion:**

Open repository in Visual Studio Code, press `Ctrl+Shift+D` and select `data-export - publish-export-data` in drop down list. Press `F5` to start debug session.
