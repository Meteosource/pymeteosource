"""Various custom exceptions"""

class InvalidRequestError(ValueError):
    """
    Exception that is raised when API does not return 200 to a request
    """
    def __init__(self, response):
        code, msg = response.status_code, response.text
        self.message = 'API returned code %s with error: \n  %s' % (code, msg)
        super().__init__(self.message)


class InvalidArgumentError(ValueError):
    """
    Exception that is raised when illegal combination
    of place_id and lat+lon is requested.

    Attributes
    ----------
    MSG : string
        The exceptions message to print
    """
    MSG = 'Only place_id or lat+lon can be specified!'

    def __init__(self):
        self.message = self.MSG
        super().__init__(self.message)


class EmptyInstanceError(ValueError):
    """
    Exception that is raised when access using [] attempted to empty instance

    Attributes
    ----------
    MSG : string
        The exceptions message to print
    """
    MSG = 'The instance does not contain any data!'

    def __init__(self):
        self.message = self.MSG
        super().__init__(self.message)


class InvalidIndexTypeError(ValueError):
    """
    Exception that is raised when illegal index type is used
    for indexing MultipleTimesData.

    Attributes
    ----------
    MSG : string
        The exceptions message to print
    """
    MSG = 'Invalid index data type "%s" to MultipleTimesData!'

    def __init__(self, parameter):
        """
        :param str: The value that was incorrectly used
        """
        self.message = self.MSG % parameter
        super().__init__(self.message)


class InvalidDatetimeIndexError(ValueError):
    """
    Exception that is raised when datetime used to index MultipleTimesData
    is not present in the data.

    Attributes
    ----------
    MSG : string
        The exceptions message to print
    """
    MSG = 'Invalid datetime index "%s" to MultipleTimesData!'

    def __init__(self, parameter):
        """
        :param datetime: The value that was incorrectly used
        """
        self.message = self.MSG % parameter
        super().__init__(self.message)


class InvalidStrIndexError(ValueError):
    """
    Exception that is raised when string used to index MultipleTimesData
    is not present in the data.

    Attributes
    ----------
    MSG : string
        The exceptions message to print
    """
    MSG = 'Invalid string index "%s" to MultipleTimesData!'

    def __init__(self, parameter):
        """
        :param datetime: The value that was incorrectly used
        """
        self.message = self.MSG % parameter
        super().__init__(self.message)
