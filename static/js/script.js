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

function AppStateModel() {
  this.vehicleResults = null;

  this.hasVehicleResults = function() {
    return this.vehicleResults && this.vehicleResults.length;
  };
}

function RootCtrl($scope, $appState, $http) {
  $scope.appState = $appState;

  $scope.dummySearch = function() {
    var startTime = currentDatetimeRoundedUp();
    var endTime = new Date(startTime.getFullYear(), startTime.getMonth(),
      startTime.getDate(), startTime.getHours() + 2, startTime.getMinutes());
    var params = {
      'lat': 37.7735937,
      'lng': -122.4036157,
      'start_time': startTime.toISOString(),
      'end_time': endTime.toISOString()
    };
    $http.get('/search?' + $.param(params))
      .success(function(response) {
        $appState.vehicleResults = response['vehicles'];
      });
  };
}

function VehicleResultsCtrl($scope) {

}

window['initApp'] = function() {
  function configuration($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
  }

  angular.module('appModule', ['ui.bootstrap'], configuration)
    .controller('RootCtrl', RootCtrl)
    .controller('VehicleResultsCtrl', VehicleResultsCtrl)
    .value('$appState', new AppStateModel());

  angular.element(document).ready(function() {
    angular.bootstrap(document, ['appModule']);
  });
};
