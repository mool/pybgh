# pybgh

A BGH Smart devices API client written in python.

## Install

```
pip install pybgh
```

## Example

```
import pybgh

client = pybgh.BghClient('email@xxx.com', 'password')
home_id = client.get_homes()[0]['HomeID']
device_id = next(iter(client.get_devices(home_id)))

print(client.get_status(home_id, device_id)['data'])
client.set_mode(device_id, 'cool', 24, 'auto')
```
