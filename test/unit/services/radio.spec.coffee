'use strict'

describe "daemon.radio", ->
  radio = undefined
  $interval = undefined
  callbackfn = undefined
  beforeEach -> 
    module "daemon.radio"
    inject (_radio_) -> radio = _radio_
    inject (_$interval_) -> $interval = _$interval_
    radio.enableMock()
    callbackfn = jasmine.createSpy('callbackfn')

  describe "when initialized", -> 

    beforeEach -> radio.init()
    it "should report an initialized radio", ->
      expect(radio.initialized()).toBe(true)
    it "should create mock events", ->
      radio.onReceive('mock', callbackfn)
      $interval.flush(101)
      expect(callbackfn).toHaveBeenCalled()
    describe "and then closed", ->
      beforeEach -> radio.close()
      it "should not report an initialized radio", ->
        expect(radio.initialized()).toBe(false)
      it "should not accept callbacks", ->
        return_value = radio.onReceive('mock', callbackfn)
        expect(return_value).toBe(false)
        $interval.flush(101)
        expect(callbackfn).not.toHaveBeenCalled()
        
  describe "when not initialized", ->
    it "should not report an initialized radio", ->
      expect(radio.initialized()).toBe(false)
    it "should not accept callbacks", ->
      return_value = radio.onReceive('mock', callbackfn)
      expect(return_value).toBe(false)
      $interval.flush(101)
      expect(callbackfn).not.toHaveBeenCalled()
