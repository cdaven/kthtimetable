# -*- coding: iso-8859-1 -*-

# Skapat av Christian Davén 2004

class ReadError(IOError): pass
class WriteError(IOError): pass
class DataError(ReadError): pass
class NullError(DataError): pass
class LoginError(RuntimeError): pass
class InterruptedError(RuntimeError): pass
