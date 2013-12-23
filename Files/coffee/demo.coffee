# Copyright Xavier Pouyollon 2013
# GPL v3 License

app = angular.module 'myApp', ['ngResource','googlechart','ui.router']

app.config ($stateProvider) ->
  home = {name:"home", url: "/Intro", templateUrl: "/demo/intro.html"}
  list = {name:"list", url: "/Focales", templateUrl: "/demo/focals.html", controller: FocalCtrl}
  col = {name:"collection",url: "/Collections",templateUrl: "/demo/collections.html",controller: CollectionCtrl}
  $stateProvider.state home
  $stateProvider.state list
  $stateProvider.state col

# Directive
app.directive 'progressIndicator', ->
  restrict : 'E'
  scope : { progress : '=', collection:'=' }
  link : (scope) ->
    scope.$watch 'progress', (v)->
      scope.curPrg = v
  controller: ($scope, $resource) ->
    Undetected = $resource('/collections/undetected',{},{do:{method:'POST'}})

    $scope.toggleList = () ->
      $scope.showList = !$scope.showList
    $scope.generate = (collection) ->
      Undetected.do  {'errors':$scope.curPrg.errors, 'col':collection}, ->
        alert ("Added into collection !")
  templateUrl : '/demo/progress.html'

# Progress service.
app.factory 'AskInfo', ($rootScope) ->
  r = {}
  r.SendPicture = (pict) ->
    $rootScope.$broadcast('askInfo', pict)
  # And return r
  r

@FocalCtrl = ($scope, $http, $q, $resource)->
  Graph =  $resource('/graphs/:type/:camid/:minFoc/:maxFoc/:pas')
  Cameras = $resource('/cameras/models')
  $scope.lastentries = []

  Cameras.get {}, (cameras) ->
    $scope.cameras = cameras.cams
    $scope.mycam = cameras.cams[0]

  $scope.get_pub = ->
    e = {'min': $scope.minFoc, 'max': $scope.maxFoc, 'pas': $scope.pas}
    v = $scope.lastentries.filter (x) -> x.min == e.min and x.max == e.max and x.pas == e.pas
    $scope.lastentries.push(e) if v.length == 0
    $scope.lastentries = $scope.lastentries[1..] if $scope.lastentries.length > 4
    mongraph = Graph.get {type:$scope.graphStyle,
    camid:$scope.mycam.id,
    minFoc:$scope.minFoc, maxFoc:$scope.maxFoc,
    pas:$scope.pas}, ->
      $scope.chart = mongraph

  $scope.zoom = (row) ->
      key = $scope.chart.data.rows[row]['c'][0]
      $scope.minFoc = key.low
      $scope.maxFoc = key.high
      $scope.pas = Math.floor ((key.high - key.low) / 10) + 1
      $scope.get_pub()

  $scope.back = (e) ->
    $scope.minFoc = e.min
    $scope.maxFoc = e.max
    $scope.pas = e.pas
    $scope.get_pub()

  $scope.minFoc = 0
  $scope.maxFoc = 800
  $scope.pas = 30
  $scope.graphStyle = "PieChart"

# This controller moves into the list of pictures to tag

@CollectionCtrl = ($scope, $http, $q, $resource, AskInfo)->
  Collections = $resource('/collections/getlist')
  Images = $resource('/collections/getImages/:colId')
  Process = $resource('/collections/processImage',{},{do:{method:'POST'}})
  GetNames = $resource('/tags/getList')
  Finish = $resource('/collections/finish')

  total = 0
  index = 0
  errors = []

  GetNames.get {}, (names)->
    $scope.names = names.res

  Collections.get {}, (colls)->
    $scope.collections = colls.colls

  $scope.Process = (id) ->
    $scope.$broadcast('hideMe')
    images = Images.get {colId:id}, ->
      $scope.imgList = images.imgs
      index = 0
      total = $scope.imgList.length
      errors = []
      $scope.ProcessAgain()

  $scope.ProcessAgain = () ->
    vpict = $scope.imgList.shift()
    index += 1
    $scope.currentProgress = {'text':vpict.fullName, 'index': index, 'maxi': total, 'end':false, 'errors':errors}
    res = Process.do {'img':vpict}, ->
      $scope.colors = res.colorpath
      if res.detect.length == 0
        errors.push({'path':vpict.fullName, 'id': vpict.id_local})
        $scope.ProcessAgain() if $scope.imgList.length > 0
      AskInfo.SendPicture(res) if res.detect.length > 0
      $scope.currentProgress = {'text':'Done', 'end':true, 'errors':errors} if $scope.imgList.length == 0

  $scope.RemoveTempFiles = () ->
    Finish.get {}, () ->

  $scope.$on 'Resume', () ->
    $scope.RemoveTempFiles()if $scope.imgList.length == 0
    $scope.ProcessAgain() if $scope.imgList.length > 0

# This controller displays the various faces found in a picture

@NameCtrl = ($scope, $http, $q, $resource)->
  Train = $resource('/collections/train',{},{do:{method:'POST'}})
  Tag = $resource('/collections/tag',{},{do:{method:'POST'}})
  $scope.showMe = false

  $scope.AddTrain = () ->
    Train.do {'face':$scope.curHead}, ->
      $scope.MoveNext()

  $scope.AddTag = () ->
    Tag.do {'face':$scope.curHead}, ->
      $scope.MoveNext()

  $scope.MoveNext = () ->
    $scope.showMe = false
    $scope.name = ''
    $scope.$emit('Resume') if $scope.FaceList.length == 0
    $scope.ProcessAgain() if $scope.FaceList.length > 0

  $scope.Skip = () ->
    $scope.MoveNext()

  $scope.Label = () ->
    $scope.AddTrain() if $scope.name.name != $scope.guess
    $scope.AddTag() if $scope.name.name == $scope.guess

  $scope.SetName = (name) ->
    $scope.curHead.name = name

  $scope.ProcessAgain = () ->
    $scope.showMe = true
    cface = $scope.FaceList.shift()
    # Process the current face.
    headpict = cface.headPict
    headname = cface.name
    $scope.guess = headname
    imgSrc = cface.headPath
    $scope.curHead = { 'id_img' : $scope.id_img, 'name' : headname, 'cropHead' : headpict}
    $scope.imgSrc = imgSrc
    obj = $scope.names.filter (x) -> x.name == headname
    $scope.name = obj[0]

  $scope.$on 'askInfo', (sender, faces) ->
    $scope.id_img = faces.id_img
    $scope.FaceList = faces.detect
    $scope.ProcessAgain()

  $scope.$on 'hideMe', ->
    $scope.showMe = false
