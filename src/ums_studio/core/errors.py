class UMSException(Exception):
    pass


class ParserError(UMSException):
    pass


class ValidatorError(UMSException):
    pass


class TransportError(UMSException):
    pass
