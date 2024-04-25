# Ops

`Op`s are objects representing tasks that can be arranged in `Computation`s to be run synchronously or asynchronously during the handling of a query in the server.

Ops can be run in the current process or in celery after the query has been handled. They can be pickled and unpickled.

Any safe operation that is to be used during request handling should be packaged as an op so it is more modulable / configurable and standard.

Operation handling critical aspects of request processing should not be packaged as ops as it might pose a security threat.