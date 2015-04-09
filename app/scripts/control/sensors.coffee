'use strict'

angular.module('daemon.sensors', [])

.controller('SensorCtrl', [
    '$scope'

    # possibly move all sensor related functions into factory and use controller for the dashboard
    ($scope) ->
        $scope.sensorList = []
        $scope.sensors = {}

        $scope.SensorClick = (sensor) ->
            console.log "Sensor was clicked"

        $scope.UpdateSensorData = (did) ->
            received = $scope.MockSensorData(did)
            $scope.sensors[did].data = received.data
            if $scope.sensors[did].properties.type == 'num'
                $scope.sensors[did].data_normalized = 100 * received.data / $scope.sensors[did].properties.max_value

        $scope.getSensorImage = (sensor) ->
            base_img = '<img class="sensor_img" src="image_loc"></img>'
            if sensor.properties.type == 'binary'
                if sensor.data == 1
                    return base_img.replace "image_loc", "images/on.png"
                else
                    return base_img.replace "image_loc", "images/off.png"
            return ''

        # methods since I don't have data yet
        $scope.HandleSensorEnumeration = (sensorList) ->
            sensorIds = Object.keys sensorList
            for i in sensorIds by 1
                int_did = parseInt sensorIds[i-1]
                $scope.sensorList.push parseInt int_did
                sensor = {did: int_did, description: sensorList[int_did], display: '', name: 'name' + int_did, properties: {}}
                $scope.sensors[int_did] = sensor

        $scope.RandomAllSensors = () ->
            for did in $scope.sensorList
                $scope.UpdateSensorData did

        $scope.MockSensorData = (did) ->
            if $scope.sensors[did].properties.type == 'binary'
                if Math.random() > 0.5
                    data = 1
                else
                    data = 0
                return {did: did, data: data}
            else
                return {did: did, data: (did * Math.random()).toFixed(3)}

        $scope.HandleSensorEnumeration {1: "On and off", 2: "On and off 2", 3: "sensor 3", 4:"sensor 4"}
        $scope.sensors[1].properties = {type: 'binary'}
        $scope.sensors[2].properties = {type: 'binary'}
        $scope.sensors[3].properties = {type: 'num', max_value: 5}
        $scope.sensors[4].properties = {type: 'num', max_value: 8}

        setInterval $scope.RandomAllSensors, 500

])
