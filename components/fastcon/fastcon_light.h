#pragma once

#include <array>
#include <vector>
#include "esphome/core/component.h"
#include "esphome/components/light/light_output.h"
#include "fastcon_controller.h"

namespace esphome
{
    namespace fastcon
    {
        enum class LightState
        {
            OFF,
            WARM_WHITE,
            RGB
        };

        class FastconLight : public Component, public light::LightOutput
        {
        public:
            FastconLight(uint8_t light_id) : light_id_(light_id) {}

            void setup() override;
            light::LightTraits get_traits() override;
            void write_state(light::LightState *state) override;
            void set_controller(FastconController *controller);

            void set_supports_rgb(bool supports_rgb) { this->supports_rgb_ = supports_rgb; }
            void set_supports_color_temperature(bool supports_color_temperature) { this->supports_color_temperature_ = supports_color_temperature; }
            void set_supports_white(bool supports_white) { this->supports_white_ = supports_white; }
            void set_supports_brightness(bool supports_brightness) { this->supports_brightness_ = supports_brightness; }
            void set_min_mireds(float min_mireds) { this->min_mireds_ = min_mireds; }
            void set_max_mireds(float max_mireds) { this->max_mireds_ = max_mireds; }

        protected:
            FastconController *controller_{nullptr};
            uint8_t light_id_;
            bool supports_rgb_{true};
            bool supports_color_temperature_{true};
            bool supports_white_{true};
            bool supports_brightness_{true};
            float min_mireds_{153.0f};
            float max_mireds_{500.0f};
        };
    } // namespace fastcon
} // namespace esphome
