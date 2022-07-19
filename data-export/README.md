# data-export

This example shows the data transport via edgefarm.network and the transfer of this data to external systems.

For this purpose, an edgefarm.applications app will be rolled out in an edge node and continuously generates data. 
This data will be pushes into edgefarm.network and delivered to the external system.

The external system, in this example `receive-historic-data`, receives the puffered data and stores it into a local `csv` file.

The Jupyter Notebook `view-life-data`, can be used to receive and visualize live data from edgefarm.network.

## Usage

**Deploy example:**

First, create a kubernetes namespace in which to create the edge application and the network.  

```
kubectl create ns data-export

namespace/data-export created
```

Next, the application network will be created in which attributes are defined, such as valid subjects or buffer sizes within the network.

```
kubectl apply -f manifest/network.yaml -n data-export

application.core.oam.dev/data-export-network created
```

This creates a new application network within edgefarm.network. This network consists of a 10 MB intermediate buffer on the participating edge nodes and a 100 MB buffer in the main network (usually in the cloud), which collects and aggregates the edge buffers.
All buffers are managed in the respective file system. Alternatively, they can also be created in memory.

The application definition `manifest/application.yaml` contains a reference to the docker image of example application `publish-export-data`. If necessary, you can modify the docker image's tag for the correct version of the application image. 

You can either build your own docker image if you like to modify the demos. For this see the [building section](../README.md#building-yourself) of this Readme.
After any modifications, you need to redeploy the application.

Now, the actual edge application will be rolled out.

```
$ kubectl apply -f manifest/application.yaml -n data-export

application.core.oam.dev/data-export created
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

$ kubeclt label node axolotl publish-export-data=

node/axolotl labeled
```

These labels are used to select which edge node is to receive the application. In this case, the node 'axolotl' is selected.

After finishing deployment and modifications check if the application is running.

```bash
$ kubectl get pods -n data-export -o wide
NAME                        READY   STATUS    RESTARTS   AGE    IP           NODE        NOMINATED NODE   READINESS GATES
publish-export-data-bjsrk   3/3     Running   0          3m4s   172.17.0.2   rpi-snake   <none>           <none>
```

View the logs of the application. Viewing can be terminated with `Ctrl+C`.

```bash
$ kubectl logs publish-export-data-bjsrk -n data-export -c publish-export-data -f
2022-04-08 12:58:01 root         INFO     Connecting to NATS server: nats://leaf-nats.nats:4222
2022-04-08 12:58:16 root         INFO     Published 1000 messages in 15 seconds. Total size: 257750. Byte per Second:  17183.
2022-04-08 12:58:22 root         INFO     Published 1000 messages in 16 seconds. Total size: 257722. Byte per Second:  16107.
...
```

**Prepare config files for receiving the export data:**

It is required to prepare two files:
- `natsEndpoint.creds`: credentials file for a secure access to to your generated data
- `.env`: config file defining where to collect data from


Get `natsEndpoint.creds` from cluster:
```bash
kubectl get secret -n data-export -o yaml data-export.publish-export-data -o jsonpath='{.data.data-export-network\.creds}' | base64 --decode > data-export/natsEndpoint.creds
```

Prepare `.env` config file:
```bash
kubectl get secrets -o jsonpath='{.data.NATS_ADDRESS}' nats-server-info | base64 --decode | xargs printf 'NATS_SERVER="%s"\n' > data-export/.env
```


**Receive the historic data:**

Execute `receive-historic-data` application to collect histroic data from data endpoint and store data in local file `data.csv`.

```bash
$ cd data-export/receive-historic-data
$ pip3 install -r requirements.txt

# Run normally without verbose logs...
$ python3 main.py
2022-04-25 16:23:13 root         INFO     Connecting to NATS server: tls://connect.ngs.global:4222
2022-04-25 16:23:48 root         INFO     Received all historic data. Proceed with live data.

# ... or run it with verbose logs
$ LOGLEVEL=DEBUG python3 main.py
2022-05-16 21:33:20 asyncio      DEBUG    Using selector: EpollSelector
2022-05-16 21:33:20 root         INFO     Connecting to NATS server: nats://hb001.edgefarm.io:4222
2022-05-16 21:33:21 root         DEBUG    Received data: {'timestamp_ms': 1652729464720, 'msg_id': 16174, 'sensor1': {'x': 0.129648, 'y': 0.50633, 'z': 0.058441}, 'sensor2': {'x': 0.129648, 'y': 0.50633, 'z': 0.058441}}
2022-05-16 21:33:21 root         DEBUG    Write to file: 2022-05-16,21:31:04.720000,0.129648,0.506330,0.058441,0.129648,0.506330,0.058441
2022-05-16 21:33:21 root         DEBUG    Received data: {'timestamp_ms': 1652729464739, 'msg_id': 16175, 'sensor1': {'x': 0.157909, 'y': 0.423882, 'z': 0.034252}, 'sensor2': {'x': 0.157909, 'y': 0.423882, 'z': 0.034252}}

```

The output csv file can be configured by executing the following just before executing the application. The file does not have to exist, but the path does.
```bash
$ export CSV_FILE=/path/to/csv-file.csv
```

**View live data**

The view life data example is realized with a Jupyter Notebook. These files can be viewed and executed e.g. with VS Code by installing the extension  [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter).

To run Jupyter Notebook open the file `data-export/view-life-data/main.ipynb` e.g. in VS Code and click on `Run All`:

![Run Jupyter Notebook](../docs/run-jupyter-notebook.png)

Scroll down to the bottom of the file to view the graph.

![Jupyter Output Example](../docs/data-export-jupyter-output.png)

**⚠ NOTE:** If you experience issues with the notebook regarding missing packages please run `pip3 install -r requirements.txt` in the notebook directory.