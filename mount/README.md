# mount

This example shows how to mount a directory into an application container on edge device.

The edgefarm.applications app will be rolled out in an edge node that reads a file mounted from the edge device. It reads the file line by line and writes the contents to another file along with a timestamp.

<!-- The file mount is defined in the deployment manifest `manifest.yaml`. The trait of type `volume` defines the volumes names, paths and permissions. -->

## Deploy example

First, create a Kubernetes namespace where you create the edge application.

```
$ kubectl create namespace mount
namespace/mount created
```

The application definition [manifest/application.yaml](manifest/application.yaml) ` contains a reference to the docker image of example application `rw-files`. If necessary, you can modify the docker image's tag for the correct version of the application image. 


You can either build your own docker image if you like to modify the demos. For this see the [building section](../README.md#building-yourself) of this Readme.
After any modifications, you need to redeploy the application.

Now, the actual edge application will be rolled out.

```bash
$ cd mount
$ kubectl apply -f mount/manifest/application.yaml -n mount
application.core.oam.dev/mount created
```

The corresponding label for the edge-node must be set.

```
$ kubectl get nodes
NAME           STATUS   ROLES                      AGE    VERSION
axolotl        Ready    agent,edge                 6d7h   v1.19.3-kubeedge-v1.9.1
test001-1      Ready    controlplane,etcd,worker   20d    v1.21.7
test001-2      Ready    controlplane,etcd,worker   20d    v1.21.7
test001-3      Ready    controlplane,etcd,worker   20d    v1.21.7
gecko-middle   Ready    agent,edge                 6d7h   v1.19.3-kubeedge-v1.9.1
gecko-right    Ready    agent,edge                 6d7h   v1.19.3-kubeedge-v1.9.1

$ kubeclt label node axolotl mount=
node/axolotl labeled
```

These labels are used to select which edge node is to receive the application. In this case, the node 'axolotl' is selected.

After finishing deployment and modifications check if the application is running.

```bash
$ kubectl get pods -n mount -o wide
NAME             READY   STATUS    RESTARTS   AGE   IP           NODE        NOMINATED NODE   READINESS GATES
rw-files-l9s6j   1/1     Running   0          44m   172.17.0.4   axolotl     <none>           <none>
```

## Check results

Log into your edge device and write something into the file to verify that the application can access the mounted directory.
```bash
$ ssh root@axolotl
root@axolotl:~ echo "hello" > /data/path-on-host/read-file
root@axolotl:~ echo "how are you" >> /data/path-on-host/read-file
```

Check the output from application:
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
