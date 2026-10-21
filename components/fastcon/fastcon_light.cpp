#include <algorithm>
#include <set>
#include "esphome/core/log.h"
#include "fastcon_light.h"
#include "fastcon_controller.h"
#include "utils.h"

namespace esphome
{
    namespace fastcon
    {
        static const char *const TAG = "fastcon.light";

        void FastconLight::setup()
        {
            if (this->controller_ == nullptr)
            {
                ESP_LOGE(TAG, "Controller not set for light %d!", this->light_id_);
                this->mark_failed();
                return;
            }
            ESP_LOGCONFIG(TAG, "Setting up Fastcon BLE light (ID: %d)...", this->light_id_);
            ESP_LOGCONFIG(TAG, "  Supports RGB: %s", YESNO(this->supports_rgb_));
            ESP_LOGCONFIG(TAG, "  Supports Color Temperature: %s", YESNO(this->supports_color_temperature_));
            ESP_LOGCONFIG(TAG, "  Supports White: %s", YESNO(this->supports_white_));
            ESP_LOGCONFIG(TAG, "  Supports Brightness: %s", YESNO(this->supports_brightness_));
        }

        void FastconLight::set_controller(FastconController *controller)
        {
            this->controller_ = controller;
        }

        light::LightTraits FastconLight::get_traits()
        {
            auto traits = light::LightTraits();
            std::set<light::ColorMode> modes;

            if (this->supports_rgb_)
            {
                modes.insert(light::ColorMode::RGB);
            }

            if (this->supports_color_temperature_)
            {
                modes.insert(light::ColorMode::COLD_WARM_WHITE);
                traits.set_min_mireds(this->min_mireds_);
                traits.set_max_mireds(this->max_mireds_);
            }

            // In Home Assistant, ColorMode.WHITE is for lights with RGB and an auxiliary white channel (RGBW).
            // It cannot be combined with ColorMode.COLOR_TEMP.
            if (this->supports_white_ && this->supports_rgb_ && !this->supports_color_temperature_)
            {
                modes.insert(light::ColorMode::WHITE);
            }

            // Fallback: If no color or temperature modes are enabled
            if (modes.empty())
            {
                if (this->supports_brightness_)
                {
                    modes.insert(light::ColorMode::BRIGHTNESS);
                }
                else
                {
                    modes.insert(light::ColorMode::ON_OFF);
                }
            }

            traits.set_supported_color_modes(modes);
            return traits;
        }

        void FastconLight::write_state(light::LightState *state)
        {
            // Get the light data bits from the state
            auto light_data = this->controller_->get_light_data(state);

            // Debug output - print the light state values
            bool is_on = (light_data[0] & 0x80) != 0;
            float brightness = ((light_data[0] & 0x7F) / 127.0f) * 100.0f;
            if (light_data.size() == 1)
            {
                ESP_LOGD(TAG, "Writing state: light_id=%d, on=%d, brightness=%.1f%%", light_id_, is_on, brightness);
            }
            else
            {
                auto r = light_data[2];
                auto g = light_data[3];
                auto b = light_data[1];
                auto warm = light_data[4];
                auto cold = light_data[5];
                ESP_LOGD(TAG, "Writing state: light_id=%d, on=%d, brightness=%.1f%%, rgb=(%d,%d,%d), warm=%d, cold=%d", light_id_, is_on, brightness, r, g, b, warm, cold);
            }

            // Generate the advertisement payload
            auto adv_data = this->controller_->single_control(this->light_id_, light_data);

            // Debug output - print payload as hex
            std::string hex_str = vector_to_hex_string(adv_data);
            ESP_LOGD(TAG, "Advertisement Payload (%zu bytes): %s", adv_data.size(), hex_str.c_str());

            // Send the advertisement repeat_count times
            for (uint8_t i = 0; i < this->controller_->get_repeat_count(); i++)
            {
                this->controller_->queueCommand(this->light_id_, adv_data);
            }
        }
    } // namespace fastcon
} // namespace esphome
