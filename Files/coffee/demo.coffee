# cd ~/BottleAngular/Files/coffee
# coffee -b -c -o ../js/ -w demo.coffee

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
  scope : { progress : '=' }
  link : (scope) ->
    scope.$watch 'progress', (v)->
      scope.curPrg = v
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

@CollectionCtrl = ($scope, $http, $q, $resource, AskInfo)->
  Collections = $resource('/collections/getlist')
  Images = $resource('/collections/getImages/:colId')
  Process = $resource('/collections/processImage',{},{do:{method:'POST'}})
  GetNames = $resource('/tags/getList')
  total = 0
  index = 0
  errors = []

  GetNames.get {}, (names)->
    $scope.names = null

  Collections.get {}, (colls)->
    $scope.collections = colls.colls

  $scope.Process = (id) ->
    images = Images.get {colId:id}, ->
      $scope.imgList = images.imgs
      index = 0
      total = $scope.imgList.length
      errors = []
      $scope.CropAgain()

  $scope.CropAgain = () ->
    vpict = $scope.imgList.shift()
    index += 1
    $scope.currentProgress = {'text':vpict.fullName, 'index': index, 'maxi': total, 'end':false, 'errors':errors}
    res = Process.do {'img':vpict}, ->
      if res.result == false
        errors.push(vpict.fullName)
        $scope.CropAgain()
      AskInfo.SendPicture(res) if res.result == true
      $scope.currentProgress = {'text':'Done', 'end':true, 'errors':errors} if $scope.imgList.length == 0

  $scope.$on 'Resume', () ->
       $scope.CropAgain() if $scope.imgList.length > 0

@NameCtrl = ($scope, $http, $q, $resource)->
  Train = $resource('/collections/train/:IdLocal/:name')
  Tag = $resource('/collections/tag/:IdLocal/:name')

  $scope.AddTrain = () ->
    Train.get {IdLocal: $scope.image.id_local, name : $scope.name}, ->
      $scope.MoveNext()

  $scope.AddTag = () ->
    Tag.get {IdLocal: $scope.image.id_local, name : $scope.name}, ->
      $scope.MoveNext()

  $scope.MoveNext = () ->
    $scope.name = ''
    $scope.$emit('Resume')

  $scope.Skip = () ->
    $scope.MoveNext()

  $scope.Label = () ->
    $scope.AddTrain() if $scope.name != $scope.image.recog
    $scope.AddTag() if $scope.name == $scope.image.recog

  $scope.$on 'askInfo', (sender, image) ->
    $scope.image = image
    $scope.imgSrc = image.imgSrc
    $scope.name = image.recog