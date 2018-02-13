# awsiotgg

Establishes AWS GreenGrass Connections

## Usage

```python
# Init AWSIoTMQTTShadowClient
self._shadow_client = AWSIoTMQTTShadowClient(self._config.THING_NAME)

# AWSIoTShadowClient configuration
...

# Init DiscoveryInfoProvider
discovery_info_provider = DiscoveryInfoProvider()

# DiscoveryInfoProvider configuration
...

discovery_info = discovery_info_provider.discover(
    self._config.THING_NAME)

# Connect to GGC
self._connection_manager = GGConnectionManager(
    self._shadow_client, discovery_info)
# Connect ShadowClient
logger.info('Connecting MQTT Shadow Client')
self._connection_manager.connect(
    self._config.PRIVATE_KEY_PATH, self._config.CERTIFICATE_PATH)

```

