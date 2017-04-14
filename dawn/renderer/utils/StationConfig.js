import fs from 'fs';
export const stationNumber = parseInt(fs.readFileSync('/opt/driver_station/station_number.txt'))
export const bridgeAddress = fs.readFileSync('/opt/driver_station/lcm_bridge_addr.txt')
console.log("station: " + stationNumber)
console.log("bridge: " + bridgeAddress)