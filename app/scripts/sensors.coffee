'use strict'

angular.module('daemon.sensors', ['daemon.widget'])

.controller('SensorCtrl', [
    '$scope'
    'SensorGraphData'

    # possibly move all sensor related functions into factory and use controller for the dashboard
    ($scope, SensorGraphData) ->
        $scope.sensorList = []
        $scope.sensors = {}

        $scope.SensorClick = (sensor) ->
            $scope.addWidget 'linechart', { did: sensor.did, name: sensor.description }

        $scope.UpdateSensorData = (did) ->
            received = $scope.MockSensorData(did)
            $scope.sensors[did].data = received.data
            if $scope.sensors[did].properties.type == 'num'
                $scope.sensors[did].data_normalized = 100 * received.data / $scope.sensors[did].properties.max_value
            SensorGraphData.UpdateGraphData did, received.data

        $scope.GetLastValuesArray = (did) ->
            return $scope.sensors[did].last_values

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
                $scope.UpdateSensorData sensor.did
            
        $scope.GetSensorData = (did) ->
            received = $scope.MockSensorData did
            received['last_values'] = []
            return received

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

        $scope.test = () ->
            DataStore.create('simple').clear()
            console.log "clearing datastore " + DataStore.create('simple').count()

        $scope.HandleSensorEnumeration {1: "This is the description of some random binary sensor that only produces on and off values.", 2: "This is another description from some different arbritrary sensor that only has two values.", 3: "This has any random values.", 4:"This is sensor 4."}
        $scope.sensors[1].properties = {type: 'binary'}
        $scope.sensors[2].properties = {type: 'binary'}
        $scope.sensors[3].properties = {type: 'num', max_value: 5}
        $scope.sensors[4].properties = {type: 'num', max_value: 8}

        setInterval $scope.RandomAllSensors, 500

])
.factory('SensorGraphData', [
    () ->
        {
        graph_data: {}
        UpdateGraphData: (did, val) ->
            if !this.graph_data[did]?
                this.graph_data[did] = []
            now = Date.now()
            this.graph_data[did].push {x: now, y: val}
            while this.graph_data[did][0].x < (now-10000)
                this.graph_data[did].shift()
        GetGraphData: (did) ->
            if !this.graph_data[did]?
                this.graph_data[did] = []
            return this.graph_data[did]
        }
    ]
)
