#ifndef DEVICES_H
#define DEVICES_H

typedef enum {
  LIMIT_SWITCH = 0x00,
  POTENTIOMETER = 0x02,
  SERVO_CONTROL = 0x07,
  EXAMPLE_DEVICE = 0xFFFF
} deviceID;


#endif /* DEVICES_H */