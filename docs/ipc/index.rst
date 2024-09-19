.. currentmodule:: discord_tools.ipc

IPC Server Tools
================

``discord_tools`` provides a simple IPC handler. This section outlines
everything about it.



Models
------

ClientSession
~~~~~~~~~~~~~

.. attributetable:: ClientSession

.. autoclass:: ClientSession()
    :members:

Server
~~~~~~

.. attributetable:: Server

.. autoclass:: Server()
    :members:

Request
~~~~~~~

.. attributetable:: Request

.. autoclass:: Request()
    :members:

Route
~~~~~

.. attributetable:: Route

.. autoclass:: Route()
    :members:


Functions
---------

.. autofunction:: route


Event Reference
---------------

.. function:: on_raw_ipc_request(request)

    Called when the IPC receives a request. This is called before
    the actual route callback, so it is recommended to not respond to the request
    in this event nor depend on it.

    .. note::

        This event is dispatched always, even if the endpoint is
        not a valid one.

    :param request: The raw request
    :type request: Request


.. function:: on_ipc_request_completion(request)

    Called when the IPC completes a request. This is called after
    the route callback.

    .. note::

        Unlike :func:`on_raw_ipc_request`, this event is not dispatched if the route is not valid.

    :param request: The request that was completed
    :type request: Request
