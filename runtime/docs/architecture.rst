Architecture
============

These high-level principles guide Runtime's design:

#. Reliability: Working with hardware is inherently unreliable, so we should attempt to recover from transient failures.
   Each component should have a small "blast radius" to prevent failures from cascading.
#. Performance: Control loops should run at a high frequency, with minimal latency from gamepad input to device actuation.
#. Easy-of-use: APIs should hide complexity by default, even at the cost of flexibility.
#. Transparency: Any component of the control stack should be easily auditable to facilitate debugging.
#. Backwards compatibility: Interfaces (especially those consumed by students) should only change with good reason.

Keep in mind that the kit's purpose is educational.
The intended users are high school students with minimal to no programming or debugging experience.
Lag, hard-to-distinguish bugs, and unnecessarily high coding expectations can all ruin the student experience.

Services
--------

Runtime is essentially a distributed application.
Functionality is partitioned into multiple *services*, each of which runs one or more processes and threads.
Services communicate with one another and external clients either through ZeroMQ_ sockets or through `shared memory <https://docs.python.org/3/library/multiprocessing.shared_memory.html>`_ for fast buffered interprocess communication (IPC).

.. Important::
   A multiprocess architecture complicates state sharing, since each process has its own isolated memory space.
   However, multiprocessing allows Runtime to take full advantage of hardware parallelism.
   Most Python implementations (including CPython, the implementation used by PiE) use a Global Interpreter Lock (GIL) to manage memory and references, so the operating system cannot actually schedule Python threads to run concurrently on multiple physical cores (except for some C or Cython extensions).
   By contrast, each process runs its own Python interpreter with its own GIL, so there's no any contention.

Because of the I/O bound nature of Runtime, no services so far spin up more than one process.

+--------------+-----------------------------------------------------+
| Service      | Description                                         |
+==============+=====================================================+
| ``device``   | - Detects sensor hotplug events                     |
|              | - Encodes and decodes sensor packets                |
|              | - Reads and writes to sensors                       |
+--------------+-----------------------------------------------------+
| ``executor`` | - Executes student code                             |
|              | - Manages student-visible state, such as match data |
+--------------+-----------------------------------------------------+
| ``broker``   | - Receives and decodes gamepad data                 |
|              | - Broadcasts sensor data to clients                 |
+--------------+-----------------------------------------------------+

Supervisor
``````````

The service lifecycle is managed by a *supervisor*, which:

- Spawns all services as subprocesses
- Restarts all the services if any of them fail
- Signals subprocesses to terminate gracefully
- Start a thread to forward logs to external clients

The supervisor should be the smallest and most reliable component of Runtime.

Clients
-------

Runtime has several intended clients:

- Dawn: The student-facing UI
- Shepherd: Field control
- Command-line tools: Allow for control over robots over the command line.
  Useful for developers and debug station.

To hide messaging implementation details, Runtime offers plug-and-play client libraries in Python and NodeJS.
For further information, see the specification.

Communication
-------------

Communication of state in distributed systems is inherently tricky.

Shared Memory
`````````````

Runtime communicates gamepad and sensor parameters through shared memory buffers.
These buffers are attached to ``ctypes`` structs to provide convenient field access.
Every parameter has a name, type, and readable/writeable flags.
Readable parameters have a ``current_<name>`` field in the struct representing the current parameter value.
Writeable parameters have a ``desired_<name>`` field in the struct representing the desired parameter value.

- Since these devices should be controlled at a very high frequency, it is important for reads and writes to be highly optimized.
  Shared memory buffers outperform pipes and queues attached to a centralized memory store.
- There is no need for synchronization because, typically, only one thread will write to a particular field in the buffer.
  Atomic reads and writes to the entire buffer are not necessary.

Sockets
```````

All other communication is handled through ZeroMQ_ sockets.

.. _ZeroMQ: https://zeromq.org/
