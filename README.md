# Python Concurrency

A hands-on project for understanding Python concurrency by implementing the same HTTP workload using multiple concurrency models.

The aim is to build an intuition for **when** each approach should be used, rather than simply learning the syntax.

## Objectives


- Learn when to use sequential execution, threads and coroutines.
- Compare execution models using the same workload.
- Understand the abstractions used by Python's concurrency libraries:
  - Thread pools
  - Futures
  - Coroutines
  - Tasks
  - Event loops
- Build a mental model of how concurrency relates to operating systems and networking.

## HTTP API

The examples use a locally hosted instance of **httpbin** running in Docker.

The `/delay/<seconds>` endpoint simulates slow network responses, allowing the effects of different concurrency models to be observed.

Example:

```
GET http://localhost:8080/delay/3
```