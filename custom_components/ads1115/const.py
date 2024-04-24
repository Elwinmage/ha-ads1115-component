from homeassistant.const import Platform

DOMAIN = "ads1115"

CONF_FLOW_PLATFORM = "platform"

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_I2C_BUS="i2c_bus"
CONF_DEFAULT_I2C_BUS=1

CONF_I2C_ADDRESS="i2c_address"
CONF_DEFAULT_ADDRESS=72

CONF_PINS = "pins"
CONF_FLOW_PIN_NUMBER = "pin_number"
CONF_FLOW_PIN_NAME = "pin_name"

CONF_GAIN="gain"
CONF_GAIN_DEFAULT=6.144
CONF_GAINS=[6.144,4.096,2.048,1.024,0.512,0.256]

DEFAULT_SCAN_RATE = 5#.1 #seconds
