# awsiotgg

Wrapper for AWS Greengrass to perform Core Discovery and Connection Establishment

## Features

* Core Discovery
* Core Connection Establishment
* Discovery Information Cache (enables connecting to Core even connection to Discovery Endpoint is lost)
* Automatic Retry during Discovery and Connection Establishment

## Usage

```python

from AWSIoTGG import GGConnector

# Init AWSIoTMQTTShadowClient
self._shadow_client = AWSIoTPyMQTT.AWSIoTMQTTShadowClient(<THING_NAME>)

# Init DiscoveryInfoProvider
self._discovery_info_provider = DiscoveryInfoProvider()
self._discovery_info_provider.configureEndpoint(<HOST>)
self._discovery_info_provider.configureCredentials(<ROOT_CA_PATH>, <CERTIFICATE_PATH>, <PRIVATE_KEY_PATH>)

gg_connector = GGConnector(
    self._shadow_client, self._discovery_info_provider)

try:
    core_info, group_ca_path = gg_connector.discover(<THING_NAME>)

    gg_connector.connect(
        core_info, group_ca_path, <CERTIFICATE_PATH>, <PRIVATE_KEY_PATH>)
except BaseException as err:
    logger.error(err)
    sys.exit(1)

# Here comes the actual device implementation

```
