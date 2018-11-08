# -*- coding: utf-8 -*-

import logging
import os
import pickle
import shutil
import uuid

from AWSIoTGG.Exceptions import DiscoverCoreFailedException, EstablishConnectionFailedException
from AWSIoTPythonSDK.core.protocol.connection.cores import ProgressiveBackOffCore
from AWSIoTPythonSDK.exception.AWSIoTExceptions import DiscoveryInvalidRequestException

logger = logging.getLogger(__name__)

GROUP_CA_PATH = './groupCA/'
CACHE_PATH = './groupCache/'

COREINFO_KEY = 'core_info'
GROUP_CA_KEY = 'group_ca'


class GGConnector:
    """Connection Manager for Greengrass Devices"""

    def __init__(self, client, discovery_info_provider):
        self._client = client
        self._discovery_info_provider = discovery_info_provider

    def discover(self, thing, retry_count=5):
        """Performs GG Core discovery"""

        # Progressive back off core
        backOffCore = ProgressiveBackOffCore()
        MAX_RETRY_COUNT = retry_count

        discovered = False
        core_info = None
        group_ca_path = None
        while retry_count != 0:
            try:
                discovery_info = self._discovery_info_provider.discover(thing)
                ca_list = discovery_info.getAllCas()
                core_list = discovery_info.getAllCores()

                # only pick the first ca and core info
                group_id, ca = ca_list[0]
                core_info = core_list[0]
                logger.info('Discovered GGC: {} from Group: {}'.format(
                    core_info.coreThingArn, group_id))

                logger.debug('Persist connectivity/identity information...')
                # cleanup old certificates
                shutil.rmtree(GROUP_CA_PATH)

                # persist new certificate
                group_ca_path = GROUP_CA_PATH + group_id + \
                    "_CA_" + str(uuid.uuid4()) + ".crt"
                if not os.path.exists(GROUP_CA_PATH):
                    os.makedirs(GROUP_CA_PATH)
                with open(group_ca_path, "w") as group_ca_file:
                    group_ca_file.write(ca)

                self._store_connectivityinfo(core_info, group_ca_path)

                discovered = True
                break
            except BaseException as e:
                retry_count -= 1
                logger.debug('Discovery Error: %s\n%d/%d retries left',
                             e, retry_count, MAX_RETRY_COUNT)
                backOffCore.backOff()

        if not discovered and self._cache_empty():
            raise DiscoverCoreFailedException()
        elif not discovered:
            core_info, group_ca_path = self._get_connectivityinfo()

        return core_info, group_ca_path

    def connect(self, core_info, group_ca, certificate_path, private_key_path, retry_count=5):
        """Attempts to connect to one of the discovered greengrass core devices"""

        self._client.configureCredentials(
            group_ca, private_key_path, certificate_path)

        # Progressive back off core
        backOffCore = ProgressiveBackOffCore()
        MAX_RETRY_COUNT = retry_count

        connected = False
        while retry_count != 0:
            # Attempt connecting to any of the endpoint in the connectivity list
            for connectivity_info in core_info.connectivityInfoList:
                current_host = connectivity_info.host
                current_port = connectivity_info.port

                logger.debug('Trying to connect to core at %s:%s',
                             current_host, current_port)

                # Configure Endpoint
                self._client.configureEndpoint(current_host, current_port)

                try:
                    # Connect client to Core
                    self._client.connect()
                    connected = True
                    break
                except BaseException as e:
                    logger.debug(e)

            if not connected:
                retry_count -= 1
                logger.debug('Connection Error\n%d/%d retries left',
                             retry_count, MAX_RETRY_COUNT)
                backOffCore.backOff()
            else:
                break

        if not connected:
            raise EstablishConnectionFailedException()

    def _cache_empty(self):
        """Returns if discovery info has been cached earlier"""

        core_info, group_ca_path = self._get_connectivityinfo()

        return core_info is not None and group_ca_path is not None

    def _store_connectivityinfo(self, core_info, group_ca_path):
        """Cache connectivity info"""

        if not os.path.exists(CACHE_PATH):
            os.makedirs(CACHE_PATH)

        discovery_info = {
            COREINFO_KEY: core_info,
            GROUP_CA_KEY: group_ca_path
        }

        with open(os.path.join(CACHE_PATH, 'connectivityinfo.pickle'), 'wb+') as connectivity_info_file:
            pickle.dump(discovery_info, connectivity_info_file,
                        pickle.HIGHEST_PROTOCOL)

    def _get_connectivityinfo(self):
        """Get previously cached connectivity info"""

        with open(os.path.join(CACHE_PATH, 'connectivityinfo.pickle'), 'rb') as connectivity_info_file:
            discovery_info = pickle.load(connectivity_info_file)

        return discovery_info[COREINFO_KEY], discovery_info[GROUP_CA_KEY]
