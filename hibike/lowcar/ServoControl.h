#ifndef SERVO_CONTROL_H
#define SERVO_CONTROL_H

#include "Device.h"
#include "defs.h"
#include <Servo.h>

#define NUM_PINS 2

#define SERVO_0 5
#define SERVO_1 6

#define SERVO_RANGE 1000
#define SERVO_CENTER 1500

class ServoControl : public Device
{
public:
    ServoControl();
    // Overridden functions
    // Comments/descriptions can be found in source file
    virtual uint8_t device_read(uint8_t param, uint8_t *data_buf, size_t data_buf_len);
    virtual uint32_t device_write(uint8_t param, uint8_t *data_buf);
    virtual void device_disable(); //calls helper disableAll() to detach all servos

private:
    //detaches all servos
    void disableAll();
    //attaches the index 'num' to its corresponding pin
    void enable(int num);

    uint8_t pins[NUM_PINS] = {SERVO_0, SERVO_1};
    float positions[NUM_PINS] = {0,0};
};

#endif
