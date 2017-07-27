import logging

import requests

from AWSIoTGG.util import ResponseParser
from AWSIoTGG.util.Exceptions import CoreNotFoundError


class GGCoreDiscoveryService:
	def __init__(self, host, thing_name, certificate, private_key, root_ca):
		self._logger = logging.getLogger(__name__)
		self.host = host
		self.thing_name = thing_name
		self.certificate = certificate
		self.private_key = private_key
		self.root_ca = root_ca


	def discover(self):
		# Discover Greengrass Core
		discovery_response = requests.get('https://'+ self.host +':8443/greengrass/discover/thing/'+ self.thing_name,
										cert=(self.certificate, self.private_key), verify=self.root_ca)

		if discovery_response.status_code != 200:
			raise CoreNotFoundError()


		# Parse response to get connectivity info and certificates
		response_parser = ResponseParser(discovery_response.json())
		connectivity_info_list, root_ca_map = response_parser.get_parsed_response()

		# Sort by connection info id
		connectivity_info_list.sort(key=lambda x: x.id)

		return connectivity_info_list, root_ca_map
