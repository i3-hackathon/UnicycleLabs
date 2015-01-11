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
  this.searchLocation = null;

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
        $appState.vehicleResults = response['vehicles'];
        $appState.searchLocation = new google.maps.LatLng(
          $scope.form.lat, $scope.form.lng);
      });
  };

  $scope.getCurrentLocation();
}

function VehicleResultsCtrl($scope, $appState) {
  $scope.mapState = {
    map: null
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
    var bounds = new google.maps.LatLngBounds();
    $.each($appState.vehicleResults, function(i, result) {
      var location = gmapsLatLngFromJson(result['location']);
      bounds.extend(location);
      var marker = new google.maps.Marker({
        map: map,
        position: location
      });
    });

    var currentLocationMarker = new google.maps.Marker({
      map: map,
      position: $appState.searchLocation,
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        scale: 10
      }
    })

    map.fitBounds(bounds);
  };

  $scope.distanceMiles = function(result) {
    return result['distance_meters'] * 0.000621371;
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
    .directive('htdGooglePlaceAutocomplete', htdGooglePlaceAutocomplete)
    .directive('htdGoogleMap', htdGoogleMap)
    .value('$appState', new AppStateModel());

  angular.element(document).ready(function() {
    angular.bootstrap(document, ['appModule']);
  });
};
