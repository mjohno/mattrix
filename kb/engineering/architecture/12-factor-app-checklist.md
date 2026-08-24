---
type: checklist
title: Twelve-Factor App checklist
description: Checks that an application follows the Twelve-Factor App methodology.
tags:
  - engineering
  - architecture
  - twelve-factor
  - cloud-native
---

# Twelve-Factor App checklist

Use this checklist when you design, build, or review a service application.

## I. Codebase

- [ ] Keep each application in one version-controlled codebase.
- [ ] Deploy the same codebase to multiple environments.
- [ ] Extract shared functionality into versioned dependencies.

## II. Dependencies

- [ ] Declare every application dependency explicitly.
- [ ] Isolate dependencies from system-wide packages and tools.
- [ ] Use the same dependency definition in development and production.

## III. Configuration

- [ ] Keep configuration separate from application code.
- [ ] Do not store credentials in the codebase.
- [ ] Provide deployment-specific configuration through environment variables.
- [ ] Manage each configuration value independently. Do not use grouped environment files as the configuration model.

## IV. Backing services

- [ ] Treat databases, queues, caches, email services, and APIs as attached resources.
- [ ] Store each backing-service connection detail in configuration.
- [ ] Replace a backing service through configuration without code changes.

## V. Build, release, and run

- [ ] Keep build, release, and run stages separate.
- [ ] Build one executable artifact from a specific code revision.
- [ ] Combine the build artifact and deployment configuration into a release.
- [ ] Give every release a unique identifier.
- [ ] Do not change a released artifact. Create a new release for every change.
- [ ] Keep runtime startup simple and reliable.

## VI. Processes

- [ ] Run the application as one or more stateless processes.
- [ ] Store persistent state in a backing service.
- [ ] Use process memory and local files only for temporary data.
- [ ] Do not depend on sticky sessions.

## VII. Port binding

- [ ] Make each network service self-contained.
- [ ] Export each service by binding to a configured port.
- [ ] Do not require a runtime-injected web server.

## VIII. Concurrency

- [ ] Define distinct process types for distinct workloads.
- [ ] Scale by running more processes, not by changing application design.
- [ ] Let the execution environment start, stop, and supervise processes.
- [ ] Do not daemonize processes or manage PID files.

## IX. Disposability

- [ ] Start processes quickly.
- [ ] Handle `SIGTERM` and stop gracefully.
- [ ] Finish, return, or safely retry in-progress work during shutdown.
- [ ] Design processes to recover from unexpected termination.

## X. Development and production parity

- [ ] Keep development, staging, and production environments similar.
- [ ] Minimize the time between code change and deployment.
- [ ] Involve application developers in deployment and production operation.
- [ ] Use the same type and version of backing services in all environments.

## XI. Logs

- [ ] Write logs as time-ordered event streams to standard error (`stderr`).
- [ ] Do not write, rotate, route, or store log files in the application.
- [ ] Let the execution environment collect and store logs.

## XII. Administrative processes

- [ ] Run migrations, repairs, and other one-off tasks as separate processes.
- [ ] Run administrative processes with the same code, dependencies, and configuration as the deployed application.
- [ ] Run administrative processes against the intended release.

## Modifications

This checklist intentionally sends logs to `stderr`, not `stdout`.

## Reference

- [The Twelve-Factor App](https://12factor.net/)
