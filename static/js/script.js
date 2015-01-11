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

function AppStateModel() {
  this.vehicleResults = null;

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
      });
  };

  $scope.getCurrentLocation();
}

function VehicleResultsCtrl($scope) {

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
    .value('$appState', new AppStateModel());

  angular.element(document).ready(function() {
    angular.bootstrap(document, ['appModule']);
  });
};
