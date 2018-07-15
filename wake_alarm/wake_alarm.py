"""
Copyright (C) 2018 Ben Lewis.
Licensed under the MIT License; see the included LICENSE file.
Component to manage a visual wake up alarm.
"""

from homeassistant.const import CONF_WEEKDAY, STATE_OFF, STATE_ON
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event_decorators import track_time_change
from homeassistant.components import light
import time
import logging
import voluptuous as vol

# Helpers for schema validation
def Time(format='%H:%m'):
  return lambda v: time.strptime(v, format)

# Component domain; this is how configurations will refer to it.
DOMAIN = "wake_alarm"

# Components this component depends on.
DEPENDENCIES = ["group", "light"]

#  Configuration keys
"""Target device getting a time set."""
CONF_TARGET = "target"

"""Starting time to begin wake cycle. Must be presented in HH:MM format. Defaults to 07:00."""
CONF_START_TIME = "start_time"

"""Stopping time for wake cycle. Must be presented in HH:MM format. Defaults to 08:00."""
CONF_END_TIME = "end_time"

COMPONENT_SCHEMA = vol.Schema({
  vol.Required(CONF_PLATFORM): 'wake_alarm',
  vol.Required(CONF_LIGHTS): cv.entity_ids,
  vol.Optional(CONF_START_TIME, default="07:00"): vol.All(Time())
})

# Variable for storing configuration parameters.
TARGET_ID = None

# Variables to store start and stop times for alarm sequence.
START_TIME_VALUE = time.strptime("07:00", "%H:%M")
END_TIME_VALUE = time.strptime("08:00", "%H:%M")

# Name of the service we expose
SERVICE_WAKE_ALARM = "Wake Alarm"

# Shortcut to the logger
_LOGGER = logging.getLogger(__name__);

def setup(hass, config):
  """Setup Wake Alarm component."""
  global TARGET_ID
  global START_TIME_VALUE
  global END_TIME_VALUE

  config_schema = vol.Schema({
    vol.Required(CONF_LIGHTS): 
  })

  # Validate that all required config options are given
  if not validate_config(config, {DOMAIN: [CONF_TARGET, CONF_START_TIME, CONF_END_TIME]}, _LOGGER):
    return False

  TARGET_ID = config[DOMAIN][CONF_TARGET]
  if CONF_START_TIME in config[DOMAIN]:
    try:
      START_TIME_VALUE = time.strptime(config[DOMAIN][CONF_START_TIME], "%H:%M")
    except ValueError e:
      _LOGGER.error("Start time was in an invalid format; expected a value in the format HH:MM, like '07:00'. Provided value was %s.", config[DOMAiN][CONF_START_TIME])
      return False
  
  if CONF_END_TIME in config[DOMAIN]:
    try:
      END_TIME_VALUE = time.strptime(config[DOMAIN][CONF_END_TIME], "%H:%M")
    except ValueError e:
      _LOGGER.error("End time was in an invalid format; expected a time in the format HH:MM, like '08:00'. Supplied value was %s.", config[DOMAIN][CONF_END_TIME])
      return False

  if START_TIME_VALUE > END_TIME_VALUE:
    _LOGGER.error("Can't start an alarm after ending it; supplied times are __ and __.")

  if hass.states.get(TARGET_ID) is None:
    _LOGGER.error("Target entity id %s does not exist.", TARGET_ID)

    TARGET_ID = None
    return False
  
  # We've initialized successfully.
  return True