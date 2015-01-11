function currentDatetimeRoundedUp() {
  var date = new Date();
  var hour = date.getHours();
  var minute = date.getMinutes();
  if (minute > 30) {
    hour = hour + 1;
    minute = 0;
  } else {
    minute = 30;
  }
  return new Date(date.getFullYear(), date.getMonth(), date.getDate(), hour, minute);
}

function endTimeFromStartTime(startTime, durationHours) {
    return new Date(startTime.getFullYear(), startTime.getMonth(),
      startTime.getDate(), startTime.getHours() + durationHours, startTime.getMinutes());
}

function gmapsLatLngFromJson(latlngJson) {
  return new google.maps.LatLng(latlngJson['lat'], latlngJson['lng']);
}

/*** Models ***/

function AppStateModel() {
  this.vehicleResults = null;
  this.selectedResult = null;
  this.scrollResult = null;
  this.searchLocation = null;
  this.collapseSearch = false;

  this.hasVehicleResults = function() {
    return this.vehicleResults && this.vehicleResults.length;
  };
}

/*** Controllers ***/

function RootCtrl($scope, $appState) {
  $scope.appState = $appState;
}

function SearchFormCtrl($scope, $appState, $http) {
  $scope.gettingCurrentPosition = false;
  $scope.searching = false;

  var startTime = currentDatetimeRoundedUp();
  var endTime = endTimeFromStartTime(startTime, 2);
  $scope.form = {
    rawLocation: null,
    lat: null,
    lng: null,
    startTime: startTime,
    endTime: endTime
  };

  $scope.locationInputFocused = function() {
    if ($scope.form.rawLocation == 'Current location') {
      $scope.form.rawLocation = null;
    }
  };

  $scope.placeChanged = function(place) {
    if (place['geometry'] && place['geometry']['location']) {
      var location = place['geometry']['location'];
      $scope.form.lat = location.lat();
      $scope.form.lng = location.lng();
    }
  };

  $scope.getCurrentLocation = function() {
    $scope.gettingCurrentLocation = true;

    navigator.geolocation.getCurrentPosition(function(position) {
      $scope.form.lat = position.coords.latitude;
      $scope.form.lng = position.coords.longitude;
      $scope.form.rawLocation = 'Current location';
      $scope.gettingCurrentLocation = false;
      $scope.$apply();
    }, function() {
      $scope.form.currentLocation = null;
      $scope.gettingCurrentLocation = false;
      $scope.$apply();
    });
  };

  $scope.canSubmit = function() {
    return !$scope.searching && $scope.form.lat;
  };

  $scope.submit = function() {
    $scope.searching = true;
    var params = {
      'lat': $scope.form.lat,
      'lng': $scope.form.lng,
      'start_time': $scope.form.startTime.toISOString(),
      'end_time': $scope.form.endTime.toISOString()
    };
    $http.get('/search?' + $.param(params))
      .success(function(response) {
        $scope.searching = false;
        $appState.collapseSearch = true;
        $appState.vehicleResults = response['vehicles'];
        $appState.searchLocation = new google.maps.LatLng(
          $scope.form.lat, $scope.form.lng);
      });
  };

  $scope.getCurrentLocation();
}

function VehicleResultsCtrl($scope, $appState) {
  $scope.mapState = {
    map: null,
    markers: [],
    currentLocationMarker: null
  };

  $scope.mapOptions = {
    center: new google.maps.LatLng(0, 0),
    draggable: true,
    zoom: 15,
    mapTypeControl: false,
    panControl: false,
    scaleControl: true,
    streetViewControl: false,
    zoomControlOptions: {
      style: google.maps.ZoomControlStyle.SMALL,
      position: google.maps.ControlPosition.TOP_LEFT
    }
  };

  $scope.mapCreated = function(map) {
    $scope.drawResults(map);
  };

  $scope.drawResults = function(map) {
    var bounds = new google.maps.LatLngBounds();
    $.each($appState.vehicleResults, function(i, result) {
      var location = gmapsLatLngFromJson(result['location']);
      bounds.extend(location);
      var marker = new google.maps.Marker({
        map: map,
        position: location,
        icon: '/static/img/' + result['map_icon_url']
      });
      google.maps.event.addListener(marker, 'click', function() {
        $appState.scrollResult = result;
        $scope.$apply();
      });
      $scope.mapState.markers.push(marker);
    });

    $scope.mapState.currentLocationMarker = new google.maps.Marker({
      map: map,
      position: $appState.searchLocation,
      icon: 'static/img/my-location-map-logo.png'
    });

    map && map.fitBounds(bounds);
  };

  $scope.clearMap = function() {
    if (!$scope.mapState.map) {
      return;
    }
    $.each($scope.mapState.markers, function(i, marker) {
      marker.setMap(null);
    });
    $scope.mapState.currentLocationMarker.setMap(null);
  };

  $scope.$watch('appState.vehicleResults', function(newResults, oldResults) {
    if (newResults) {
      $scope.clearMap();
      $scope.drawResults($scope.mapState.map);
    }
  });

  $scope.distanceMiles = function(result) {
    return result && result['distance_meters'] * 0.000621371;
  };
}

function DetailViewCtrl($scope) {
  $scope.distanceMiles = function(result) {
    return result && result['distance_meters'] * 0.000621371;
  };  
}

/*** Directives ***/

function htdGooglePlaceAutocomplete($parse) {
  return {
    restrict: 'A',
    link: function(scope, element, attrs, model) {
      var placeChangeFn = $parse(attrs.onPlaceChange);
      var types = attrs.locationTypes ? attrs.locationTypes.split(',') : [];
      var options = {
        types: types,
        componentRestrictions: {}
      };
      var gPlace = new google.maps.places.Autocomplete(element[0], options);

      google.maps.event.addListener(gPlace, 'place_changed', function() {
        if (placeChangeFn) {
          scope.$apply(function() {
            placeChangeFn(scope, {$newPlace: gPlace.getPlace()});
          });
        };
      });
    }
  };
}

function htdGoogleMap($timeout) {
  return {
    restrict: 'AE',
    scope: {
      map: '=',
      mapOptions: '=',
      resizeWhen: '=',
      afterCreation: '&'
    },
    link: function(scope, element, attrs) {
      var mapOptions = scope.mapOptions || {};
      var map = scope.map = new google.maps.Map(element[0], mapOptions);
      scope.$watch('resizeWhen', function(newValue) {
        if (newValue) {
          var oldCenter = map.getCenter();
          google.maps.event.trigger(map, 'resize');
          map.setCenter(oldCenter);
        }
      });
      $timeout(function() {
        var oldCenter = map.getCenter();
        google.maps.event.trigger(map, 'resize');
        map.setCenter(oldCenter);
        scope.afterCreation({$map: map});
      });
    }
  };
}

function htdScrollToSelector($interpolate) {
  return {
    restrict: 'A',
    link: function(scope, element, attrs) {
      var elem = $(element);
      scope.$watch(attrs.scrollOnChangesTo, function(value) {
        if (value != undefined || value != null) {
          var selector = $interpolate(attrs.scrollDestSelector)(scope);
          var destOffset = $(selector).offset();
          if (!destOffset) {
            // The element could be hidden right now.
            return;
          }
          var oldScrollTop = elem.scrollTop();
          var newScrollTop = oldScrollTop + destOffset.top - elem.offset().top;
          if (attrs.skipScrollWhenInView && newScrollTop >= oldScrollTop && newScrollTop < (oldScrollTop + elem.height())) {
            return;
          }
          elem.animate({scrollTop: newScrollTop}, 500);
        }
      });
    }
  };
}

/*** Bootstrapping ***/

window['initApp'] = function() {
  function configuration($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
  }

  angular.module('appModule', ['ui.bootstrap'], configuration)
    .controller('RootCtrl', RootCtrl)
    .controller('SearchFormCtrl', SearchFormCtrl)
    .controller('VehicleResultsCtrl', VehicleResultsCtrl)
    .controller('DetailViewCtrl', DetailViewCtrl)
    .directive('htdGooglePlaceAutocomplete', htdGooglePlaceAutocomplete)
    .directive('htdGoogleMap', htdGoogleMap)
    .directive('htdScrollToSelector', htdScrollToSelector)
    .value('$appState', new AppStateModel());

  angular.element(document).ready(function() {
    angular.bootstrap(document, ['appModule']);
  });
};
