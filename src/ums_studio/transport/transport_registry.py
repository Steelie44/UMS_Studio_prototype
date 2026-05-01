class TransportRegistry:
    def list_transports(self):
        return ["mock", "serial", "tcp"]

    def create(self, name: str, **kwargs):
        if name == "serial":
            from .serial_transport import SerialTransport

            return SerialTransport(kwargs.get("port", "COM1"), kwargs.get("baud", 115200))
        if name == "tcp":
            from .tcp_transport import TCPTransport

            return TCPTransport(kwargs.get("host", "127.0.0.1"), kwargs.get("port", 9000))
        from .transport_mock import MockTransport

        return MockTransport()
