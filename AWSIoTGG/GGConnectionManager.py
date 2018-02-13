# -*- coding: utf-8 -*-

import logging
import os
import socket
import sys
import errno

from AWSIoTPythonSDK.core.greengrass.discovery.models import DiscoveryInfo
from AWSIoTPythonSDK.exception import AWSIoTExceptions

logger = logging.getLogger(__name__)


class GGConnectionManager:
    """Connection Manager for Greengrass Devices"""

    def __init__(self, client, discovery_info: DiscoveryInfo):
        self._client = client
        self._core_connectivity_info = discovery_info.getAllCores()[0]
        self._root_certificate_map = discovery_info.getAllCas()

        # Certificate Storage path
        self._certificate_basepath = os.path.realpath(os.path.join(
            os.getcwd(), 'certs'))

        self._core_certificate_path = os.path.join(
            self._certificate_basepath, self._core_connectivity_info.groupId + '_root.ca.pem')

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
                if err.errno != errno.ECONNREFUSED:
                    logger.error(err.errno)
                    self._delete_certificates()
                    sys.exit(err)

            # If connection is not successul, attempt connecting with the next endpoint and port in the list
            logger.debug('Connection attempt failed for GCC %s in Group %s',
                         self._core_connectivity_info.coreThingArn, self._core_connectivity_info.groupId)

        if connection_established:
            # Connection attempt was succesful
            logger.info('Connected to GGC %s in Group %s!',
                        self._core_connectivity_info.coreThingArn, self._core_connectivity_info.groupId)

        # If unable to connect to any of the endpoints, then exit
        if not connection_established:
            logger.error(
                'Connection to any GGC could not be established!')
            self._delete_certificates()
            sys.exit()

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

    def disconnect(self):
        """Cleans up written core certificate files"""

        logger.info('Closing connection to GGC')
        try:
            self._client.disconnect()
        except AWSIoTExceptions.disconnectError as err:
            logger.warn(err.message)

        logger.info('Closed connection')

        self._delete_certificates()
