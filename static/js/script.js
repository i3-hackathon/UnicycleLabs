function AppStateModel() {
  this.vehicleResults = null;

  this.hasVehicleResults = function() {
    return this.vehicleResults && this.vehicleResults.length;
  };
}

function RootCtrl($scope, $appState, $http) {
  $scope.appState = $appState;

  $scope.dummySearch = function() {
    $http.get('/search')
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
