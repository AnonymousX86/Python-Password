# -*- coding: utf-8 -*-
class ValidateError(BaseException):
    pass


class ValueTooShort(ValidateError):
    pass


class PatternError(ValidateError):
    pass
