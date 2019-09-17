# pyadept

AsyncIO-based library for communication with [Adept](https://www.adept.com/) robot controllers.

The library supports creation of high-level robot control nodes  and their integration into distributed publish-subscribe systems based on [ZeroMQ](http://zeromq.org/). The [AsyncIO](https://docs.python.org/3/library/asyncio.html) backend allows for flexible composition of multiple communication-heavy coroutines to form a single robot control node.

Robot applications written with `pyadept` interact with a robot based on the Adept V+ platform running the code from [AdeptServer](https://github.com/semeniuta/AdeptServer). 

## Workflow

The intended workflow is based on treating the robot controller as a service. The first stage is to enable high power for the robot and start the AdeptServer's `server` V+ program on the robot controller side.  After this, a Python program based on `pyadept` can be launched and used for high-level system coordination. 

## Abstractions

Robot commands are defined as classes in the `pyadept.rcommands` module. They construct immutable instances providing the functionality of correct generation of the corresponding messages via the the `get_messages` method. It returns a tuple of byte strings, each finalized with the delimiter sequence `"\r\n"`.

The `pyadept.rprotocol` module consists of classes, functions and coroutines realizing the communication logic of a `pyadept`-baseds program, as well as tools for data capture during system operation. 

`pyadept.rprotocol.RobotClient` provides coroutine methods `connect` (establishing the connection with the server), as well as `cmdexec` and `cmdexec_joined` (providing execution of commands). The two latter methods accept one on more instances of robot commands and initiate communication with the V+ server using AsyncIO's [`StreamWriter`](https://docs.python.org/3/library/asyncio-stream.html#streamwriter)/[`StreamReader`](https://docs.python.org/3/library/asyncio-stream.html#streamreader) pair. Several commands supplied to `cmdexec` are handled one-by-one: each command's messages are sent to the server, and the corresponding responses are awaited before proceeding to the next command. Conversely, `cmdexec_joined` combines messages from the supplied commands into a single sequence, and sends all of them in one run.

`pyadept.rprotocol.ProtobufCommunicator` uses AsyncIO-compatible ZeroMQ primitives to announce a Protobuf-based request event and wait for the corresponding Protobuf-based response in the context of a publish/subscribe system.

## References

Please refer to the following research [paper](https://peerj.com/articles/cs-207/) for more information about `pyadept` and AdeptServer:

 * Semeniuta, O. and Falkman, P. (2019) ‘Event-driven industrial robot control architecture for the Adept V+ platform’, PeerJ Computer Science, 5, e207. doi: 10.7717/peerj-cs.207.