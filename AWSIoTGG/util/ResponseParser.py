from AWSIoTGG.util import ConnectivityInfo
from AWSIoTGG.util.Exceptions import UnexpectedJsonStructureError


class ResponseParser:
	_GROUP_ARRAY_KEY = 'GGGroups'
	_GROUP_ID_KEY = 'GGGroupId'
	_GGC_ARRAY_KEY = 'Cores'
	_GGC_THING_ARN_KEY = 'thingArn'
	_ROOT_CA_KEY = 'CAs'
	_CONNECTIVITY_INFO_ARRAY_KEY = 'Connectivity'
	_ID_KEY = 'Id'
	_HOST_ADDRESS_KEY = 'HostAddress'
	_PORT_KEY = 'PortNumber'
	_METADATA_KEY = 'Metadata'

	def __init__(self, response_document):
		self.response_document = response_document

	def get_parsed_response(self):
		connectivity_info_list = list()
		root_ca_map = dict()

		for group_itr in self.response_document[self._GROUP_ARRAY_KEY]:
			if self._GROUP_ID_KEY not in group_itr or self._GGC_ARRAY_KEY not in group_itr or self._ROOT_CA_KEY not in group_itr:
				raise UnexpectedJsonStructureError()

			group_name = group_itr[self._GROUP_ID_KEY]

			for core_itr in group_itr[self._GGC_ARRAY_KEY]:
				if self._GGC_THING_ARN_KEY not in core_itr or self._CONNECTIVITY_INFO_ARRAY_KEY not in core_itr:
					raise UnexpectedJsonStructureError()

				core_name = core_itr[self._GGC_THING_ARN_KEY]

				for connectivity_info_itr in core_itr[self._CONNECTIVITY_INFO_ARRAY_KEY]:
					if self._ID_KEY not in connectivity_info_itr or self._HOST_ADDRESS_KEY not in connectivity_info_itr or self._PORT_KEY not in connectivity_info_itr:
						raise UnexpectedJsonStructureError()

					cid = connectivity_info_itr[self._ID_KEY]
					host_address = connectivity_info_itr[self._HOST_ADDRESS_KEY]
					metadata = connectivity_info_itr[self._METADATA_KEY] if self._METADATA_KEY in connectivity_info_itr else ''
					port = int(connectivity_info_itr[self._PORT_KEY])

					connectivity_info = ConnectivityInfo(group_name, core_name, cid, host_address, metadata, port)
					connectivity_info_list.append(connectivity_info)

					ca_list = group_itr[self._ROOT_CA_KEY]
					root_ca_map[group_name] = ca_list

		return connectivity_info_list, root_ca_map
