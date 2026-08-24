---
type: checklist
title: Dockerfile quality checklist
description: Checks for secure, small, reproducible, and maintainable Dockerfiles.
tags:
  - devops
  - docker
  - dockerfile
  - containers
---

# Dockerfile quality checklist

Use this checklist when you create or review a Dockerfile.

## Base image

- [ ] Prefer Alpine Linux; otherwise use a Debian slim image; use another OS only when requirements need it.
- [ ] Use a specific image version or digest.
- [ ] Use an official or trusted base image.
- [ ] Use the smallest suitable base image.
- [ ] Remove build-only tools from the final image.

## Build

- [ ] Use a multi-stage build when the build produces artifacts.
- [ ] Put stable dependency files before frequently changed source files.
- [ ] Combine related package-install steps.
- [ ] Remove package-manager caches in the same layer.
- [ ] Do not copy files that the build does not need.
- [ ] Add a `.dockerignore` file.

## Security

- [ ] Do not put secrets in the Dockerfile, image, or build arguments.
- [ ] Run the service as a non-root user.
- [ ] Set file ownership only where it is necessary.
- [ ] Install only required packages.
- [ ] Do not use `latest` for production images.

## Runtime

- [ ] Set `WORKDIR`.
- [ ] Externalise configuration and build one immutable image.
- [ ] Inject configuration at runtime through a loaded configuration file, command-line parameters, or environment variables.
- [ ] Keep state outside the image and container, for example in a database, object store, cache, or the host filesystem.
- [ ] Use `CMD` for the default process.
- [ ] Use exec-form `CMD` or `ENTRYPOINT`.
- [ ] Make the container run one main service.
- [ ] Expose only required ports.
- [ ] Define a health check when the service supports one.

## Verification

- [ ] Build the image without errors.
- [ ] Run the image as its configured user.
- [ ] Confirm that the application starts.
- [ ] Scan the image for known vulnerabilities.
- [ ] Check the final image size.
- [ ] Confirm that no secret or unnecessary file is in the image.
