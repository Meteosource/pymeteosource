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


class InvalidAlertIndexTypeError(ValueError):
    """
    Exception that is raised when illegal index type is used
    for indexing MultipleTimesData.

    Attributes
    ----------
    MSG : string
        The exceptions message to print
    """
    MSG = 'Invalid index data type "%s" to AlertsData!'

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


class InvalidDateFormat(ValueError):
    """
    Exception that is raised when wrong date format is passed

    Attributes
    ----------
    MSG : string
        The exceptions message to print
    """
    MSG = 'Invalid date "%s", should be "%s"'

    def __init__(self, passed_date, correct_format):
        """
        :param str: The value that was passed as date
        :param str: Correct date format
        """
        self.message = self.MSG % (passed_date, correct_format)
        super().__init__(self.message)


class InvalidClassType(ValueError):
    """
    Exception that is raised when wrong class type is passed

    Attributes
    ----------
    MSG : string
        The exceptions message to print
    """
    MSG = 'Invalid class type "%s"'

    def __init__(self, class_type):
        """
        :param str: The data type that was passed
        """
        self.message = self.MSG % class_type
        super().__init__(self.message)


class InvalidDateSpecification(ValueError):
    """
    Exception that is raised date(s) for time_machien not specified correctly

    Attributes
    ----------
    MSG : string
        The exceptions message to print
    """
    MSG = 'Specify either "date" or "date_from" and "date_to"'

    def __init__(self):
        """
        :param str: The value that was passed as date
        :param str: Correct date format
        """
        self.message = self.MSG
        super().__init__(self.message)


class InvalidDateRange(ValueError):
    """
    Exception that is raised date(s) for time_machien not specified correctly

    Attributes
    ----------
    MSG : string
        The exceptions message to print
    """
    MSG = 'Specified "date_from" %s is not smaller than "date_to" %s'

    def __init__(self, date_from, date_to):
        """
        :param str: The value that was passed as date
        :param str: Correct date format
        """
        self.message = self.MSG % (date_from, date_to)
        super().__init__(self.message)
