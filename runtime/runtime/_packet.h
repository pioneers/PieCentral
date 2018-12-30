#ifndef PACKET_H
#define PACKET_H

namespace packet {
    std::string cobs_encode(std::string data);
    std::string cobs_decode(std::string data);
}

#endif
