# pyadept

AsyncIO-based library for communication with Adept robot controllers.

The library supports creation of high-level robot control nodes 
and their integration into distributed publish-subscribe 
systems based on ZeroMQ. The AsyncIO backend allows for 
flexible composition of multiple communication-heavy coroutines to
form a single robot control node.
