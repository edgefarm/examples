# examples

This repository contains minimal examples for edgefarm usage.

- [Export data from edgefarm.network](data-export/README.md) [![publish-export-data](https://github.com/edgefarm/examples/actions/workflows/release-export-data.yaml/badge.svg)](https://github.com/edgefarm/examples/actions/workflows/release-export-data.yaml)
- [Mount directory into an edgefarm application](mount/README.md) [![mount](https://github.com/edgefarm/examples/actions/workflows/release-mount.yaml/badge.svg)](https://github.com/edgefarm/examples/actions/workflows/release-mount.yaml)

## Building yourself

**Note: this is tested with linux kernel >= 5.0.0 and is not guaranteed to work with a lower kernel version!**

### Setup

In order to build the demo docker images, you need to have docker installed on your system.
You can modify the demos and build the docker image yourself using a tool called [dobi](https://github.com/dnephin/dobi).
There is no need to download `dobi` by manually. The wrapper script `dobi.sh` will handle everything for you.
To specify the location of the docker image, you can modify the variable `DOCKER_REGISTRY` in the file `default.env`.

Once you've changed you should run `docker login <your-registry>` to allow pushing to your registry.
If you are using docker hub, login with `docker login`.

### Building

To see a list of all build targets, run
```bash
./dobi.sh
```

To build the docker images run
```bash
./dobi.sh build-and-push-<application-name>
```

The build job registers `qemu-user-static` to run programs for foreign CPU architectures like `arm64` or `arm`.

Once the build has finished, your docker images are located at the speficied docker registry.

## Cleaning up

You can cleanup `qemu-user-static` using `./dobi.sh uninstall-qemu-user-static`.

To check if all qemu emulators have been removed successful, please run `./dobi.sh check-qemu-user-static`
