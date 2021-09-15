"""Various custom exceptions"""


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


class InvalidIndexType(ValueError):
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


class InvalidDatetimeIndex(ValueError):
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


class InvalidStrIndex(ValueError):
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
