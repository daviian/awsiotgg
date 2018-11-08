# -*- coding: utf-8 -*-

import logging
import os
import pickle
import socket
import errno

from AWSIoTGG.Exceptions import establishConnectionFailedException
from AWSIoTPythonSDK.exception import AWSIoTExceptions

logger = logging.getLogger(__name__)


class GGConnectionManager:
    """Connection Manager for Greengrass Devices"""

    def __init__(self, client, discovery_info):
        self._client = client

        if discovery_info is None:
            self._load_cached_discoveryinfo()
        else:
            self._core_connectivity_info = discovery_info.getAllCores()[0]
            self._root_certificate_map = discovery_info.getAllCas()

        # Certificate Storage path
        self._certificate_basepath = os.path.realpath(os.path.join(
            os.getcwd(), 'certs'))

        self._core_certificate_path = os.path.join(
            self._certificate_basepath, self._core_connectivity_info.groupId + '_root.ca.pem')

        # Cache path
        self._cache_basepath = os.path.realpath(os.path.join(
            os.getcwd(), 'discovery-cache'))

        self._prepare_certificates()

    def connect(self, private_key, certificate):
        """Attempts to connect to one of the discovered greengrass core devices"""

        connection_established = False

        # Configure Credentials
        self._client.configureCredentials(
            self._core_certificate_path, private_key, certificate)

        # Attempt connecting to any of the endpoint in the connectivity list
        for connectivity_info in self._core_connectivity_info.connectivityInfoList:
            logger.debug('Connecting to %s on Port %s with Certificate %s',
                         connectivity_info.host, connectivity_info.port, self._core_certificate_path)
            # Configure Endpoint
            self._client.configureEndpoint(
                connectivity_info.host, connectivity_info.port)

            try:
                # Connect to AWS IoT
                connection_established = self._client.connect()
                # If connection is successful break out of loop
                if connection_established:
                    break
            except OSError as err:
                logger.error(err)

            # If connection is not successul, attempt connecting with the next endpoint and port in the list
            logger.debug('Connection attempt failed for GCC %s in Group %s',
                         self._core_connectivity_info.coreThingArn, self._core_connectivity_info.groupId)

        # If unable to connect to any of the endpoints, then exit
        if not connection_established:
            logger.error(
                'Connection to any GGC could not be established!')
            self._delete_certificates()
            raise establishConnectionFailedException()

        # Connection attempt was succesful
        logger.info('Connected to GGC %s in Group %s!',
                    self._core_connectivity_info.coreThingArn, self._core_connectivity_info.groupId)

        self._cache_discoveryinfo()

    def _prepare_certificates(self):
        # Store all certificates using group names for the certificate names
        for group_id, certificate in self._root_certificate_map:
            with open(os.path.join(self._certificate_basepath, group_id + '_root.ca.pem'), 'w') as file:
                file.write(certificate)

    def _delete_certificates(self):
        logger.info('Cleanup core certificate files')
        for group_id, _ in self._root_certificate_map:
            os.remove(os.path.join(self._certificate_basepath,
                                   group_id + '_root.ca.pem'))

    def _cache_discoveryinfo(self):
        with open(os.path.join(self._cache_basepath, 'connectivityinfo.pickle'), 'wb') as f:
            pickle.dump(self._core_connectivity_info,
                        f, pickle.HIGHEST_PROTOCOL)

        with open(os.path.join(self._cache_basepath, 'certificate-map.pickle'), 'wb') as f:
            pickle.dump(self._root_certificate_map, f, pickle.HIGHEST_PROTOCOL)

    def _load_cached_discoveryinfo(self):
        with open(os.path.join(self._cache_basepath, 'connectivityinfo.pickle'), 'rb') as f:
            self._core_connectivity_info = pickle.load(f)

        with open(os.path.join(self._cache_basepath, 'certificate-map.pickle'), 'rb') as f:
            self._root_certificate_map = pickle.load(f)

    def disconnect(self):
        """Cleans up written core certificate files"""

        logger.info('Closing connection to GGC')
        try:
            self._client.disconnect()
        except AWSIoTExceptions.disconnectError as err:
            logger.warn(err.message)

        logger.info('Closed connection')

        self._delete_certificates()
