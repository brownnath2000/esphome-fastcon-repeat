"""Light platform for Fastcon BLE lights."""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import light
from esphome.const import (
    CONF_LIGHT_ID,
    CONF_OUTPUT_ID,
    CONF_COLD_WHITE_COLOR_TEMPERATURE,
    CONF_WARM_WHITE_COLOR_TEMPERATURE,
)

from .fastcon_controller import FastconController

DEPENDENCIES = ["esp32_ble"]
AUTO_LOAD = ["light"]

CONF_CONTROLLER_ID = "controller_id"
CONF_SUPPORTS_RGB = "supports_rgb"
CONF_SUPPORTS_COLOR_TEMPERATURE = "supports_color_temperature"
CONF_SUPPORTS_WHITE = "supports_white"
CONF_SUPPORTS_BRIGHTNESS = "supports_brightness"

fastcon_ns = cg.esphome_ns.namespace("fastcon")
FastconLight = fastcon_ns.class_("FastconLight", light.LightOutput, cg.Component)


def validate_fastcon_light(config):
    # Handle aliases for supports_rgb
    for key in ("supports_colour", "supports_color", "rgb", "colour", "color"):
        if key in config and CONF_SUPPORTS_RGB not in config:
            config[CONF_SUPPORTS_RGB] = config[key]
    if config.get("no_colour") or config.get("no_color"):
        config[CONF_SUPPORTS_RGB] = False
    if CONF_SUPPORTS_RGB not in config:
        config[CONF_SUPPORTS_RGB] = True

    # Handle aliases for supports_color_temperature
    for key in (
        "supports_colour_temperature",
        "supports_cwww",
        "color_temperature",
        "colour_temperature",
        "cwww",
    ):
        if key in config and CONF_SUPPORTS_COLOR_TEMPERATURE not in config:
            config[CONF_SUPPORTS_COLOR_TEMPERATURE] = config[key]
    if CONF_SUPPORTS_COLOR_TEMPERATURE not in config:
        config[CONF_SUPPORTS_COLOR_TEMPERATURE] = True

    # Handle aliases for supports_white
    if "white" in config and CONF_SUPPORTS_WHITE not in config:
        config[CONF_SUPPORTS_WHITE] = config["white"]
    if CONF_SUPPORTS_WHITE not in config:
        config[CONF_SUPPORTS_WHITE] = True

    # Handle aliases for supports_brightness
    if "brightness" in config and CONF_SUPPORTS_BRIGHTNESS not in config:
        config[CONF_SUPPORTS_BRIGHTNESS] = config["brightness"]
    if CONF_SUPPORTS_BRIGHTNESS not in config:
        config[CONF_SUPPORTS_BRIGHTNESS] = True

    return config


CONFIG_SCHEMA = cv.All(
    light.BRIGHTNESS_ONLY_LIGHT_SCHEMA.extend(
        {
            cv.GenerateID(CONF_OUTPUT_ID): cv.declare_id(FastconLight),
            cv.Required(CONF_LIGHT_ID): cv.int_range(min=1, max=255),
            cv.Optional(CONF_CONTROLLER_ID, default="fastcon_controller"): cv.use_id(
                FastconController
            ),
            cv.Optional(CONF_SUPPORTS_RGB): cv.boolean,
            cv.Optional("supports_colour"): cv.boolean,
            cv.Optional("supports_color"): cv.boolean,
            cv.Optional("rgb"): cv.boolean,
            cv.Optional("colour"): cv.boolean,
            cv.Optional("color"): cv.boolean,
            cv.Optional("no_colour"): cv.boolean,
            cv.Optional("no_color"): cv.boolean,
            cv.Optional(CONF_SUPPORTS_COLOR_TEMPERATURE): cv.boolean,
            cv.Optional("supports_colour_temperature"): cv.boolean,
            cv.Optional("supports_cwww"): cv.boolean,
            cv.Optional("color_temperature"): cv.boolean,
            cv.Optional("colour_temperature"): cv.boolean,
            cv.Optional("cwww"): cv.boolean,
            cv.Optional(CONF_SUPPORTS_WHITE): cv.boolean,
            cv.Optional("white"): cv.boolean,
            cv.Optional(CONF_SUPPORTS_BRIGHTNESS): cv.boolean,
            cv.Optional("brightness"): cv.boolean,
            cv.Optional(
                CONF_COLD_WHITE_COLOR_TEMPERATURE, default="153 mireds"
            ): cv.color_temperature,
            cv.Optional(
                CONF_WARM_WHITE_COLOR_TEMPERATURE, default="500 mireds"
            ): cv.color_temperature,
        }
    ).extend(cv.COMPONENT_SCHEMA),
    validate_fastcon_light,
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_OUTPUT_ID], config[CONF_LIGHT_ID])
    await cg.register_component(var, config)
    await light.register_light(var, config)

    controller = await cg.get_variable(config[CONF_CONTROLLER_ID])
    cg.add(var.set_controller(controller))

    cg.add(var.set_supports_rgb(config[CONF_SUPPORTS_RGB]))
    cg.add(var.set_supports_color_temperature(config[CONF_SUPPORTS_COLOR_TEMPERATURE]))
    cg.add(var.set_supports_white(config[CONF_SUPPORTS_WHITE]))
    cg.add(var.set_supports_brightness(config[CONF_SUPPORTS_BRIGHTNESS]))
    cg.add(var.set_min_mireds(config[CONF_COLD_WHITE_COLOR_TEMPERATURE]))
    cg.add(var.set_max_mireds(config[CONF_WARM_WHITE_COLOR_TEMPERATURE]))
