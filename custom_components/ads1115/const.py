from homeassistant.const import Platform

DOMAIN = "ads1115"

CONF_FLOW_PLATFORM = "platform"

CONF_DEVICE_ID = "device_id"
DEVICE_MANUFACTURER = "Texas Instruments"

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_I2C_BUS="i2c_bus"
CONF_DEFAULT_I2C_BUS='/dev/i2c-1'
SKIP_I2C_BUSES=['/dev/i2c-0','/dev/i2c-2']

CONF_I2C_ADDRESS="i2c_address"
CONF_DEFAULT_ADDRESS=0x48

CONF_PINS = "pins"
CONF_FLOW_PIN_NUMBER = "pin_number"
CONF_FLOW_PIN_NAME = "pin_name"
CONF_PIN_MULT=['0@A0-A1','1@A0-A3','2@A1-A3','3@A2-A3','4@A0-GND','5@A1-GND','6@A2-GND','7@A3-GND']
CONF_DEFAULT_PIN='0@A0-A1'


CONF_GAIN="gain"
CONF_GAIN_DEFAULT="0@6.144"
CONF_GAINS=["0@6.144","1@4.096","2@2.048","3@1.024","4@0.512","5@0.256"]

DEFAULT_SCAN_RATE = 5#seconds
MAX_RETRY = 3

CONF_CONVERT="convert"
