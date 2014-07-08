"use strict"

# http://docs.angularjs.org/guide/dev_guide.e2e-testing 
describe "the app as a whole", ->
  beforeEach ->
    browser().navigateTo "/"

  it "should automatically redirect to /control when location hash/fragment is empty", ->
    expect(browser().location().url()).toBe "/control"

  it "should navigate to /edit when the View 1 link in nav is clicked", ->
    element(".nav a[href=\"#/edit\"]").click()
    expect(browser().location().url()).toBe "/edit"

  describe "control module", ->

    it "should list 2 items", ->
      expect(repeater("[ng-view] ul li").count()).toEqual 2

    it "should display checked items with a line-through", ->
      expect(element("[ng-view] ul li input:checked + span").css("text-decoration")).toEqual "line-through"

    it "should sync done status with checkbox state", ->
      element("[ng-view] ul li input:not(:checked)").click()
      expect(element("[ng-view] ul li span").attr("class")).toEqual "donetrue"
      element("[ng-view] ul li input:checked").click()
      expect(element("[ng-view] ul li span").attr("class")).toEqual "donefalse"

    it "should remove checked items when the archive link is clicked", ->
      element("[ng-view] a[ng-click=\"archive()\"]").click()
      expect(repeater("[ng-view] ul li").count()).toEqual 1

    it "should add a newly submitted item to the end of the list and empty the text input", ->
      newItemLabel = "test newly added item"
      input("todoText").enter newItemLabel
      element("[ng-view] input[type=\"submit\"]").click()
      expect(repeater("[ng-view] ul li").count()).toEqual 3
      expect(element("[ng-view] ul li:last span").text()).toEqual newItemLabel
      expect(input("todoText").val()).toEqual ""


  describe "edit", ->
    beforeEach ->
      browser().navigateTo "#/edit"

    it "should render edit when user navigates to /edit", ->
      expect(element("[ng-view] p:first").text()).toMatch /partial for view 1/


  describe "simulate", ->
    beforeEach ->
      browser().navigateTo "#/simulate"

    it "should render simulate when user navigates to /simulate", ->
      expect(element("[ng-view] p:first").text()).toMatch /partial for view 2/
