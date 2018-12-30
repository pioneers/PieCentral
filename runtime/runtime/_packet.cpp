#include "_packet.h"

namespace packet {
    std::string cobs_encode(std::string decoded) {
        std::string encoded;
        uint8_t byte;
        bool final_zero = true;
        size_t index = 0, search_start_index = 0, offset;

        for (offset = 0; offset < decoded.size(); offset++) {
            byte = decoded[offset];
            if (!byte) {
                final_zero = true;
                encoded += (uint8_t)(index - search_start_index + 1);
                encoded += decoded.substr(search_start_index, index - search_start_index);
                search_start_index = index + 1;
            } else if (index - search_start_index == 0xFD) {
                final_zero = false;
                encoded += '\xff';
                encoded += decoded.substr(search_start_index, index + 1 - search_start_index);
                search_start_index = index + 1;
            }
            index++;
        }

        if (index != search_start_index || final_zero) {
            encoded += (uint8_t)(index - search_start_index + 1);
            encoded += decoded.substr(search_start_index, index - search_start_index);
        }
        return encoded;
    }

    std::string cobs_decode(std::string encoded) {
        std::string decoded;
        uint8_t byte;
        size_t len, encoded_base = 0, decoded_base, offset;

        while (encoded_base < encoded.size()) {
            len = (size_t) encoded[encoded_base];
            if (len == 0 || encoded_base + len > encoded.size()) {
                return "";
            }
            encoded_base++;
            len--;

            decoded_base = decoded.size();
            decoded.resize(decoded_base + len);
            for (offset = 0; offset < len; offset++) {
                byte = encoded[encoded_base + offset];
                if (!byte) {
                    return "";
                }
                decoded.at(decoded_base + offset) = byte;
            }
            encoded_base += len;

            if (encoded_base < encoded.size()) {
                if (len + 1 < 0xFF) {
                    decoded += '\x00';
                }
            } else {
                break;
            }
        }

        return decoded;
    }
}
