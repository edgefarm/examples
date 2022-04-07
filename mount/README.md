# mount

This example shows how to mount a directory into an application container on edge device.

The edge application reads a file mounted from the edge device line by line and writes the content together with a time stamp into another file.

## Usage

**Deploy example application:**

`manifest.yaml` is the deployment manifest of this example. This contains a reference to the docker image of example application `rw-files` and describes which directory to mount into this image. Modify the docker image's tag for the correct version of the application image.

You can either build your own docker image if you like to modify the demos. For this see the [building section](../README.md#building-yourself) of this Readme.

Apply the application using kubectl.

```bash
$ kubectl apply -f mount/manifest.yaml
namespace/mount created
application.core.oam.dev/mount created
```

**Check the status of your application:**

Check if the application is running.

```bash
$ kubectl get pods -n mount -o wide
NAME             READY   STATUS    RESTARTS   AGE   IP           NODE        NOMINATED NODE   READINESS GATES
rw-files-l9s6j   1/1     Running   0          44m   172.17.0.4   rpi-snake   <none>           <none>
```

View the logs of the application. Viewing can be terminated with `Ctrl+C`.

```bash
$ kubectl logs rw-files-l9s6j -n mount -f
2022-04-07 12:20:21 root         INFO     Read data from file: No data in file
2022-04-07 12:20:21 root         INFO     Wrtie data to file: 2022-04-07 12:20:21.263937: No data in file
2022-04-07 12:20:26 root         INFO     Read data from file: No data in file
2022-04-07 12:20:26 root         INFO     Wrtie data to file: 2022-04-07 12:20:26.270444: No data in file
...
```

Log into your edge device and write something into the file to see directories are connected.
```bash
$ ssh root@<ip address of your device>
root@raspberrypi4-64:~# echo "hello" > /data/path-on-host/read-file
root@raspberrypi4-64:~# echo "how are you" >> /data/path-on-host/read-file
```

Check the new output from application:
```bash
$ kubectl logs rw-files-l9s6j -n mount -f
2022-04-07 12:25:21 root         INFO     Read data from file: hello
2022-04-07 12:25:21 root         INFO     Wrtie data to file: 2022-04-07 12:25:21.619019: hello
2022-04-07 12:25:26 root         INFO     Read data from file: how are you
2022-04-07 12:25:26 root         INFO     Wrtie data to file: 2022-04-07 12:25:26.623087: how are you
2022-04-07 12:25:31 root         INFO     Read data from file: End of file reached
2022-04-07 12:25:31 root         INFO     Wrtie data to file: 2022-04-07 12:25:31.628804: End of file reached
...
```
