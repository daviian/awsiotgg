import logging
import os
import sys


class GGConnectionManager:
	def __init__(self, connectivity_info_list, root_ca_map, ca_location):
		self._logger = logging.getLogger(__name__)
		self.connectivity_info_list = connectivity_info_list
		self.root_ca_map = root_ca_map
		self.ca_location = ca_location


	def establish_connection(self, aws_iot_mqtt_shadow_client, certificate, private_key):
		self._store_certificates()
		connection_established = False

		# Attempt connecting to any of the endpoint in the connectivity list
		for connectivity_info_list_itr in self.connectivity_info_list:
			# Configure Endpoint
			aws_iot_mqtt_shadow_client.configureEndpoint(connectivity_info_list_itr.host_address, connectivity_info_list_itr.port)

			self._logger.info(
				'Connecting to {} on Port {}'.format(connectivity_info_list_itr.host_address, connectivity_info_list_itr.port))

			ca_list = self.root_ca_map[connectivity_info_list_itr.group_name]
			suffix_itr = 1
			for ca_list_itr in ca_list:
				core_ca_file_path = os.path.join(self.ca_location,
											connectivity_info_list_itr.group_name +'_root_ca'+ str(suffix_itr) +'.pem')
				aws_iot_mqtt_shadow_client.configureCredentials(core_ca_file_path, private_key, certificate)
				self._logger.info('Using CA at: {}'.format(core_ca_file_path))

				# Connect to AWS IoT
				connection_established = aws_iot_mqtt_shadow_client.connect()
				if connection_established:
					break

				# If connection is not successful, attempt connection with the next root CA in the list
				self._logger.info('Connect attempt failed with this CA!')
				suffix_itr += 1

			# If connection is successful, break and continue with the rest of the application
			if connection_established:
				self._logger.info('Connected to GGC {} in Group {}!!'.format(connectivity_info_list_itr.ggc_name,
																		connectivity_info_list_itr.group_name))
				break
			# If connection is not successul, attempt connecting with the next endpoint and port in the list
			self._logger.info('Connect attempt failed for GCC {} in Group {}'.format(connectivity_info_list_itr.ggc_name,
																				connectivity_info_list_itr.group_name))


		# If unable to connect to any of the endpoints, then exit
		if not connection_established:
			self._logger.error('Connection to any GGC could not be established!')
			sys.exit()


	def _store_certificates(self):
		# Store all certificates using group names for the certificate names
		for group_name, ca_list in self.root_ca_map.items():
			suffix_itr = 1
			for ca_list_itr in ca_list:
				with open(os.path.join(self.ca_location, group_name +'_root_ca'+ str(suffix_itr) +'.pem'), 'w') as file:
					file.write(ca_list_itr)
				suffix_itr += 1
