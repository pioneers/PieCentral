Setup
=====

Getting Started
---------------

You can either run Runtime in the Docker_ container engine (recommended) or natively.
Using Docker, running Runtime really is as simple as installing Docker and running ``make run`` from ``PieCentral/runtime``.
Using a container also closely simulates a production environment.
``make run`` will always copy the ``runtime`` source on your host machine into the image, so the code will never be stale.

.. WARNING::
  Currently, Runtime is Linux-only because it uses the *udev* API for detecting hotplugged sensors.
  We do not anticipate migrating to a non-Linux single-board computer (SBC) in the near future.
  Non-Linux users may use virtual machines (like Anvil), containers, or physical hardware for development.
  Therefore, there is no compelling use case for supporting other operating systems.

To run Runtime natively, you should acquire Linux with at least Python 3.8, since Runtime uses the newly introduced ``multiprocessing.shared_memory`` API.

1. Install pipenv_, which combines the ``pip`` Python package manager with ``virtualenv``, a tool for creating isolated per-project Python environments.

  .. code-block::

    pip3 install --user pipenv

2. Create a new environment with almost all of Runtime's dependencies.
   Invoke ``pipenv`` from the ``runtime`` directory containing the project ``Pipfile``.

  .. code-block::

    pipenv install --dev

3. Install ZeroMQ_ (ZMQ), a messaging library, and its Python bindings.
   Currently, the `radio-dish pattern <http://api.zeromq.org/4-2:zmq-socket#toc6>`_ Runtime uses for UDP communication is still in *DRAFT* phase, so installing ZMQ is not as simple as invoking your distribution's package manager.
   Follow ``pyzmq``'s `instructions <https://pyzmq.readthedocs.io/en/latest/draft.html>`_ for building ZMQ from source with the latest version of ZMQ (currently ``4.3.2``).
4. Run ``make build`` to compile Cython extensions.
5. Run ``pipenv run dev`` to start Runtime in development mode.
   Runtime will start logging to your terminal.

For convenience, you can open shells attached to your virtual environment by running ``pipenv shell`` from the ``runtime`` project directory.
This will also put some scripts, including ``rtcli``, the Runtime command line interface (CLI), on your shell's ``PATH``.

In the future, we plan to support ``setup.py`` to handle ZMQ installation more cleanly.

Deploying to Production
-----------------------

Travis exports Runtime Docker images to PieCentral's releases_.

TODO

.. _Docker: https://docs.docker.com
.. _releases: https://github.com/pioneers/PieCentral/releases
.. _pipenv: https://github.com/pypa/pipenv
.. _ZeroMQ: https://zeromq.org
