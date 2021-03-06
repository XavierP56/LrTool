// Generated by CoffeeScript 1.6.3
(function() {
  var app;

  app = angular.module('myApp', ['ngResource', 'googlechart', 'ui.router']);

  app.config(function($stateProvider) {
    var col, home, list;
    home = {
      url: "/Intro",
      templateUrl: "/demo/intro.html"
    };
    list = {
      url: "/Focales",
      templateUrl: "/demo/focals.html",
      controller: FocalCtrl
    };
    col = {
      url: "/Collections",
      templateUrl: "/demo/collections.html",
      controller: CollectionCtrl
    };
    $stateProvider.state('intro', home);
    $stateProvider.state('focales', list);
    return $stateProvider.state('collections', col);
  });

  app.directive('progressIndicator', function() {
    return {
      restrict: 'E',
      scope: {
        progress: '=',
        collection: '='
      },
      controller: function($scope, $resource) {
        var Undetected;
        Undetected = $resource('/collections/undetected', {}, {
          "do": {
            method: 'POST'
          }
        });
        $scope.toggleList = function() {
          return $scope.showList = !$scope.showList;
        };
        return $scope.generate = function(collection) {
          return Undetected["do"]({
            'errors': $scope.progress.errors,
            'col': collection
          }, function() {
            return alert("Added into collection !");
          });
        };
      },
      templateUrl: '/demo/progress.html'
    };
  });

  app.factory('AskInfo', function($rootScope) {
    var r;
    r = {};
    r.SendPicture = function(pict) {
      return $rootScope.$broadcast('askInfo', pict);
    };
    return r;
  });

  this.FocalCtrl = function($scope, $http, $q, $resource) {
    var Cameras, Graph;
    Graph = $resource('/graphs/:type/:camid/:minFoc/:maxFoc/:pas');
    Cameras = $resource('/cameras/models');
    $scope.lastentries = [];
    Cameras.get({}, function(cameras) {
      $scope.cameras = cameras.cams;
      return $scope.mycam = cameras.cams[0];
    });
    $scope.get_pub = function() {
      var e, mongraph, v;
      e = {
        'min': $scope.minFoc,
        'max': $scope.maxFoc,
        'pas': $scope.pas
      };
      v = $scope.lastentries.filter(function(x) {
        return x.min === e.min && x.max === e.max && x.pas === e.pas;
      });
      if (v.length === 0) {
        $scope.lastentries.push(e);
      }
      if ($scope.lastentries.length > 4) {
        $scope.lastentries = $scope.lastentries.slice(1);
      }
      return mongraph = Graph.get({
        type: $scope.graphStyle,
        camid: $scope.mycam.id,
        minFoc: $scope.minFoc,
        maxFoc: $scope.maxFoc,
        pas: $scope.pas
      }, function() {
        return $scope.chart = mongraph;
      });
    };
    $scope.zoom = function(row) {
      var key;
      key = $scope.chart.data.rows[row]['c'][0];
      $scope.minFoc = key.low;
      $scope.maxFoc = key.high;
      $scope.pas = Math.floor(((key.high - key.low) / 10) + 1);
      return $scope.get_pub();
    };
    $scope.back = function(e) {
      $scope.minFoc = e.min;
      $scope.maxFoc = e.max;
      $scope.pas = e.pas;
      return $scope.get_pub();
    };
    $scope.minFoc = 0;
    $scope.maxFoc = 800;
    $scope.pas = 30;
    return $scope.graphStyle = "PieChart";
  };

  this.CollectionCtrl = function($scope, $http, $q, $resource, AskInfo) {
    var Collections, Finish, GetNames, Images, Process, errors, index, total;
    Collections = $resource('/collections/getlist');
    Images = $resource('/collections/getImages/:colId');
    Process = $resource('/collections/processImage', {}, {
      "do": {
        method: 'POST'
      }
    });
    GetNames = $resource('/tags/getList');
    Finish = $resource('/collections/finish');
    total = 0;
    index = 0;
    errors = [];
    GetNames.get({}, function(names) {
      return $scope.names = names.res;
    });
    Collections.get({}, function(colls) {
      return $scope.collections = colls.colls;
    });
    $scope.Process = function(id) {
      var images;
      $scope.$broadcast('hideMe');
      return images = Images.get({
        colId: id
      }, function() {
        $scope.imgList = images.imgs;
        index = 0;
        total = $scope.imgList.length;
        errors = [];
        return $scope.ProcessAgain();
      });
    };
    $scope.ProcessAgain = function() {
      var res, vpict;
      vpict = $scope.imgList.shift();
      index += 1;
      $scope.currentProgress = {
        'text': vpict.fullName,
        'index': index,
        'maxi': total,
        'end': false,
        'errors': errors
      };
      return res = Process["do"]({
        'img': vpict
      }, function() {
        $scope.colors = res.colorpath;
        if (res.detect.length === 0) {
          errors.push({
            'path': vpict.fullName,
            'id': vpict.id_local
          });
          if ($scope.imgList.length > 0) {
            $scope.ProcessAgain();
          }
        }
        if (res.detect.length > 0) {
          AskInfo.SendPicture(res);
        }
        if ($scope.imgList.length === 0) {
          return $scope.currentProgress = {
            'text': 'Done',
            'end': true,
            'errors': errors
          };
        }
      });
    };
    $scope.RemoveTempFiles = function() {
      return Finish.get({}, function() {});
    };
    return $scope.$on('Resume', function() {
      if ($scope.imgList.length === 0) {
        $scope.RemoveTempFiles();
      }
      if ($scope.imgList.length > 0) {
        return $scope.ProcessAgain();
      }
    });
  };

  this.NameCtrl = function($scope, $http, $q, $resource) {
    var Tag, Train;
    Train = $resource('/collections/train', {}, {
      "do": {
        method: 'POST'
      }
    });
    Tag = $resource('/collections/tag', {}, {
      "do": {
        method: 'POST'
      }
    });
    $scope.showMe = false;
    $scope.AddTrain = function() {
      return Train["do"]({
        'face': $scope.curHead
      }, function() {
        return $scope.MoveNext();
      });
    };
    $scope.AddTag = function() {
      return Tag["do"]({
        'face': $scope.curHead
      }, function() {
        return $scope.MoveNext();
      });
    };
    $scope.MoveNext = function() {
      $scope.showMe = false;
      $scope.name = '';
      if ($scope.FaceList.length === 0) {
        $scope.$emit('Resume');
      }
      if ($scope.FaceList.length > 0) {
        return $scope.ProcessAgain();
      }
    };
    $scope.Skip = function() {
      return $scope.MoveNext();
    };
    $scope.Label = function() {
      if (($scope.name.name !== $scope.guess) || ($scope.curHead.confid < 50)) {
        $scope.AddTrain();
      }
      if (($scope.name.name === $scope.guess) && ($scope.curHead.confid >= 50)) {
        return $scope.AddTag();
      }
    };
    $scope.SetName = function(name) {
      return $scope.curHead.name = name;
    };
    $scope.ProcessAgain = function() {
      var cface, headname, headpict, imgSrc, obj;
      $scope.showMe = true;
      cface = $scope.FaceList.shift();
      headpict = cface.headPict;
      headname = cface.name;
      imgSrc = cface.headPath;
      $scope.guess = headname;
      $scope.curHead = {
        'id_img': $scope.id_img,
        'name': headname,
        'cropHead': headpict,
        'confid': cface.confid
      };
      $scope.imgSrc = imgSrc;
      obj = $scope.names.filter(function(x) {
        return x.name === headname;
      });
      $scope.name = obj[0];
      if (($scope.autoNext === true) && (cface.confid > 80)) {
        return $scope.Label();
      }
    };
    $scope.$on('askInfo', function(sender, faces) {
      $scope.id_img = faces.id_img;
      $scope.FaceList = faces.detect;
      return $scope.ProcessAgain();
    });
    return $scope.$on('hideMe', function() {
      return $scope.showMe = false;
    });
  };

}).call(this);

/*
//@ sourceMappingURL=demo.map
*/
