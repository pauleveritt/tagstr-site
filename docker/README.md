# tagstr-docker

This directory contains Dockerfiles for CPython of lysnikolaou's [tstrings](https://github.com/lysnikolaou/cpython/tree/tstrings) branch.

The dockerfile were generated with [a patched version of the official dockerfile code generator](https://github.com/koxudaxi/docker-python/blob/support_tag_strings_rebased/apply-templates.sh).
The patched code generator and Dockerfiles exist in [Koudai's(@koxudaxi) repository](https://github.com/koxudaxi/docker-python/tree/support_tag_strings_rebased) is fork on the official Python Dockerfile repository.

All images are available on [Docker Hub](https://hub.docker.com/r/koxudaxi/python).
These images are built and published on [GitHub Actions](https://github.com/pauleveritt/tagstr-site/actions) (and [Old GitHub Actions](https://github.com/koxudaxi/tagstr-docker/actions))

## How to pull from Docker Hub
```shell
$ docker pull koxudaxi/python:3.14-rc-alpine3.20
```

## How to run
```shell
$ docker run -it --rm koxudaxi/python:3.14-rc-alpine3.20
Python 3.14.0a1+ (heads/tstrings:499d70c, Oct 21 2024, 19:13:41) [GCC 13.2.1 20240309] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from templatelib import Template, Interpolation
>>> name = "World"
>>> template = t"Hello {name}"
>>> assert isinstance(template.args[0], str)
>>> assert isinstance(template.args[1], Interpolation)
>>> assert template.args[0] == "Hello "
>>> assert template.args[1].value == "World"
```

## How to build from Dockerfile
```shell
$ make build # default base image is alpine3.20
$ make build BASE_IMAGE=slim-bookworm # base image is debian:bookworm-slim
$ make build-all # build all base images
```

## Base images
- alpine3.20
- alpine3.19
- bookworm
- bullseye
- slim-bookworm
- slim-bullseye
## All tags for each base image
- alpine3.20
  - 3.14-rc-alpine3.20
  - 3.14-rc-tstrings-alpine3.20
  - 3.14-rc-tstrings-7573346-alpine3.20
  - 3.14-rc-tstrings-7573346958b09d2053e4dfb26672c5856c20986d-alpine3.20
- alpine3.19
  - 3.14-rc-alpine3.19
  - 3.14-rc-tstrings-alpine3.19
  - 3.14-rc-tstrings-7573346-alpine3.19
  - 3.14-rc-tstrings-7573346958b09d2053e4dfb26672c5856c20986d-alpine3.19
- bookworm 
  - 3.14-rc-bookworm
  - 3.14-rc-tstrings-bookworm
  - 3.14-rc-tstrings-7573346-bookworm
  - 3.14-rc-tstrings-7573346958b09d2053e4dfb26672c5856c20986d-bookworm
- bullseye
  - 3.14-rc-bullseye
  - 3.14-rc-tstrings-bullseye
  - 3.14-rc-tstrings-7573346-bullseye
  - 3.14-rc-tstrings-7573346958b09d2053e4dfb26672c5856c20986d-bullseye
- slim-bookworm
  - 3.14-rc-slim-bookworm
  - 3.14-rc-tstrings-slim-bookworm
  - 3.14-rc-tstrings-7573346-slim-bookworm
  - 3.14-rc-tstrings-7573346958b09d2053e4dfb26672c5856c20986d-slim-bookworm
- slim-bullseye
  - 3.14-rc-slim-bullseye
  - 3.14-rc-tstrings-slim-bullseye
  - 3.14-rc-tstrings-7573346-slim-bullseye
  - 3.14-rc-tstrings-7573346958b09d2053e4dfb26672c5856c20986d-slim-bullseye
