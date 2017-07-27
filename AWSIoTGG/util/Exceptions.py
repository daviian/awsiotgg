class Error(Exception):
	"""Base class for exceptions in this module"""
	pass


class UnexpectedJsonStructureError(Error):
	"""Exception raised for errors on unexpected JSON structure"""
	pass


class CoreNotFoundError(Error):
	"""Exception raised for not found greengrass cores"""
	pass
