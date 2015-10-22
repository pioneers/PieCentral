#include "hibike_message.h"
#include "Arduino.h"

#define IN_PIN 1
#define CONTROLLER_ID 0 // arbitrarily chosen for now

uint32_t data;

uint32_t subscriptionDelay;

uint8_t sensor_ids[30];
SoftwareSerial *serial_connections[30];
size_t sensor_count;


HibikeMessage *cache[30] = {NULL};
HibikeMessagen *m;

// fills the three arrays with sensor info and returns the number of sensors found
// for now it just returns something hardcoded
// TODO: actually implement
size_t get_sensors(uint8_t *sensor_ids, uint8_t *sensor_rx_pins, uint8_t *sensor_tx_pins) {
  sensor_ids[0] = 1;
  sensor_rx_pins[0] = 5;
  sensor_tx_pins[0] = 7;
  return 1;
}

void setup() {
  Serial.begin(115200);
  //pinMode(IN_PIN, INPUT);
  



  uint8_t sensor_rx_pins[30];
  uint8_t sensor_tx_pins[30];
  sensor_count = get_sensors(sensor_ids, sensor_rx_pins, sensor_tx_pins);
  for (size_t i = 0; i < sensor_count; i++) {
    serial_connections[i] = new SoftwareSerial(sensor_rx_pins[i], sensor_tx_pins[i]);
  }
  /*find all the devices*/
  /*store a list of their controller ids*/




}

uint16_t wait_for_bytes(SoftwareSerial *serial_connection, size_t bytes, uint32_t timeout) {
  uint32_t start_time = millis();
  while(serial_connection->available() < bytes || millis() - start_time < timeout){}
  return serial_connection->available();
}
void read_bytes_software_serial(*SoftwareSerial serial_connection, size_t bytes, uint8_t *buff) {
  for (size_t i = 0; i < bytes; i++) {
    *buff = (uint8_t) serial_connection->read();
    buff++;
  }
}

HibikeMessage *poll_sensor(uint8_t sensor_id, *SoftwareSerial serial_connection) {
  // send a sensor update request
  // create a hibike message for the response
  // return a pointer to it
  uint32_t POLL_TIMEOUT = 10;
  serial_connection->listen();


  // TODO replace this with an abstraction for sensor update request
  serial_connection->write(0x03);
  serial_connection->write(sensor_id);
  serial_connection->write(0x03 ^ sensor_id);

  HibikeMessageType messageId;
  uint8_t controllerId, checksum;
  HibikeMessage *m;

  // get the message id
  wait_for_bytes(serial_connection, 2, POLL_TIMEOUT) || return NULL;
  read_bytes_software_serial(serial_connection, 1, (char *) &messageId);
  read_bytes_software_serial(serial_connection, 1, controllerId);
  // TODO, which byte of the reading length is MSB?
  switch (messageId) {
    case HibikeMessageType::SensorUpdate:
        SensorType sensorTypeId;
        uint16_t sensorReadingLength;
        uint8_t *dataPtr;

        wait_for_bytes(serial_connection, 3, POLL_TIMEOUT) || return NULL;
        read_bytes_software_serial(serial_connection, 1, (char *) &sensorTypeId);
        read_bytes_software_serial(serial_connection, 2, (char *) &sensorReadingLength);

        dataPtr = (uint8_t *) malloc((size_t) sensorReadingLength);
        if (!wait_for_bytes(serial_connection, (size_t) sensorReadingLength, POLL_TIMEOUT)) {
          free((void *) dataPtr);
          return NULL;
        }
        read_bytes_software_serial(serial_connection, (size_t) sensorReadingLength, dataPtr);

        *m = new SensorUpdate(controllerId, sensorTypeId, sensorReadingLength, dataPtr);
        if (!wait_for_bytes(serial_connection, 1, POLL_TIMEOUT)) {
          free((void *) dataPtr);
          delete m;
          return NULL;
        }
        read_bytes_software_serial(serial_connection, 1, &checksum);
        if (checksum ^ m->getChecksum()) {
          free((void *) dataPtr);
          delete m;
          return NULL;
        } else {
          return m;
        }
  }
  return NULL;
}

void loop() {
  /* MY CODE ************************************************/
  /*poll each sensor, store values in a cache*/
  for (size_t i = 0; i < sensor_count; i++) {
    HibikeMessage *curr_reading = poll_sensor(sensor_ids[i], serial_connections[i]);
    if (curr_reading) {
      if (cache[i]) {
        free((void *) cache[i]->getPtrToData());
        delete cache[i];
      }
      cache[i] = curr_reading;
    }
  }
  /* /MY CODE ************************************************/












  // data = digitalRead(IN_PIN);

  // // uncomment the line below for fun data spoofing

  // uint64_t currTime = millis();
  // data = (uint32_t) (currTime) & 0xFFFFFFFF;

  // if (subscriptionDelay) {
  //   SensorUpdate(CONTROLLER_ID, SensorType::LineFollower, sizeof(data), (uint8_t*) &data).send();
  //   delay(subscriptionDelay);
  // }
  // m = receiveHibikeMessage();
  // if (m) {
  //   switch (m->getMessageId()) {
  //     case HibikeMessageType::SubscriptionRequest:
  //       {
  //         subscriptionDelay = ((SubscriptionRequest*) m)->getSubscriptionDelay();
  //         SubscriptionResponse(CONTROLLER_ID).send();
  //         break;
  //       }
  //     case HibikeMessageType::SubscriptionResponse:
  //     case HibikeMessageType::SensorUpdate:
  //     case HibikeMessageType::Error:
  //     default:
  //       // TODO: implement error handling and retries
  //       // TODO: implement other message types
  //       break;
  //   }
  //   delete m;
  // }
}

/* MY CODE ************************************************/
void serialEvent() {
  m = receiveHibikeMessage();
  if (m) {
    switch (m->getMessageId()) {

      // if the bbb is asking for a sensor update
      // TODO: implement sensor update request
      case HibikeMessageType::SensorUpdate:
        {
          uint8_t update_sent = 0;
          // find the right sensor
          for (size_t i = 0; i < sensor_count; i++) {
            if (sensor_ids[i] == m->getControllerId()) {
              //send the packet stored at cache[i]
              cache[i]->send();
              update_sent = 1;
              break;
            }
          }
          if (!update_sent) {
            //send an error message if we didnt find the device
            Error(m->getControllerId, ErrorCode::InvalidArduinoId.send());
          }
        }
      case HibikeMessageType::Error:
      default:
        // TODO: implement error handling and retries
        // TODO: implement other message types
        break;
    }
    delete m;
  }
}
/* /MY CODE ************************************************/
