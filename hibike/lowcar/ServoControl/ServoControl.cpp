#include "../ServoControl.h"

Servo servo0;
Servo servo1;
Servo servos[NUM_PINS] = {servo0, servo1};

//runs default Device constructor and then disables all servos at start
ServoControl::ServoControl() : Device(DeviceID::SERVO_CONTROL, 1)
{
    disableAll();
}

// Device functions

// device_read is called when the device receives a Device Data Update packet.
// Modifies data to contain the parameter value.
//    param - Parameter index
//    data - buffer to return data in
//    len - Maximum length of the buffer? TODO: Clarify
//
//    return - sizeof(param) on success; 0 otherwise
// Additional notes:
// - reads value in positions associated with servo at param to buffer
// - returns size of float if successful and 0 otherwise
uint8_t ServoControl::device_read(uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
    if(data_buf_len < sizeof(float))
    {
        return 0;
    }
    float* float_buf = (float *) data_buf;
    float_buf[0] = positions[param];
    return sizeof(float);
}

// device_write is called when the device receives a Device Write packet.
// Updates param to new value passed in data.
//    param   -   Parameter index
//    data    -   value to write, in bytes TODO: What endian?
//    (DEPRECATED) len     -   number of bytes in data
//
//   return  -   size of bytes written on success; otherwise return 0
// Additional notes:
// - attaches servo at param to corresponding pin
// - updates value in positions array to value
// - updates pulse width associated with specified servo
// - returns size of bytes written if successful and 0 otherwise
uint32_t ServoControl::device_write(uint8_t param, uint8_t *data_buf)
{
    float value = ((float *)data_buf)[0];
    if (value < -1 || value > 1)
    {
        return sizeof(float);
    }
    enable(param);
    positions[param] = value;
    servos[param].writeMicroseconds(SERVO_CENTER + (positions[param] * SERVO_RANGE/2));
    return sizeof(float);
}

// device_disable is called when the BBB sends a message to the Smart Device
// tellinng the Smart Device to disable itself.
// Consult README.md, section 6, to see what exact functionality is expected
// out of disable.
void ServoControl::device_disable()
{
    disableAll();
}

// Helper Functions
void ServoControl::disableAll() {
    for (int i = 0; i < NUM_PINS; i++) {
        servos[i].detach();
    }
}

void ServoControl::enable(int num)
{
    servos[num].attach(pins[num]);
}
