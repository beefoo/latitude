'use strict';

var App = (function() {

  function App(config) {
    var defaults = {
      "data": [
        {"el": "#anomaly", "url": "data/anomaly.json", "type": "bar", "append": "°C", "chart": true},
        {"el": "#emissions", "url": "data/emissions.json", "type": "bar", "append": "M", "chart": true},
        {"el": "#gdp", "url": "data/gdp.json", "type": "bar", "prepend": "$", "chart": true},
        {"el": "#population", "url": "data/pop_count.json", "type": "bar", "chart": true},
        {"el": "#temperature", "url": "data/temperature.json", "type": "bar", "append": "°C", "chart": true},
        {"el": "#vegetation", "url": "data/vegetation.json", "type": "bar", "chart": true},
        {"el": "#cities", "url": "data/cities.json", "type": "list"},
        {"el": "#surface", "url": "data/land.json", "label": "Land", "type": "pie", "chart": true},
        {"el": "#surface", "label": "Ocean", "type": "pie", "title": "Ocean area", "year": 2010, "source": "NASA SEDAC", "sourceURL": "http://sedac.ciesin.columbia.edu/data/set/gpw-v4-land-water-area-rev10", "chart": true},
        {"el": "#surface", "url": "data/ice.json", "label": "Ice sheet", "type": "pie", "chart": true}
      ]
    };

    this.opt = _.extend({}, defaults, config);
    this.init();
  }

  App.prototype.init = function(){
    var _this = this;

    var data = this.opt.data;
    this.dashboard = new Dashboard({data: _.map(data, _.clone) });
    this.chart = new Chart({data: _.map(data, _.clone)});
    this.sound = new Sound({data: _.map(data, _.clone)});
    this.data = data;

    var dataPromise = this.loadData();
    $.when.apply($, [dataPromise]).then(function(results){
      _this.onDataLoaded(results);
      _this.onReady();
    });
  };

  App.prototype.closeModals = function(){
    $('.modal').removeClass('active');
  };

  App.prototype.loadData = function(){
    var _this = this;
    var deferreds = [];
    var deferred = $.Deferred();
    _.each(this.data, function(d, i){
      var entry = _this.data[i];
      entry.index = i;
      var url = d.url;
      if (url && url.endsWith(".csv")) deferreds.push(loadCSV(url, i));
      else if (url && url.endsWith(".json")) deferreds.push(loadJSON(url, i));
    })
    $.when.apply(null, deferreds).done(function() {
      var args = Array.prototype.slice.call(arguments);
      deferred.resolve(args);
    });
    return deferred;
  };

  App.prototype.loadListeners = function(){
    var _this = this;

    $(window).on("resize", function(e){
      _this.onResize();
    })

    $(window).on("scroll", function(e) {
      _this.onScroll();
    });

    var firstLoad = true;
    $('.modal-close').on("click", function(e){
      if (firstLoad) _this.onFirstLoad();
      _this.closeModals();
      firstLoad = false;
    });

    $('.modal-open').on("click", function(e){
      e.preventDefault();
      _this.closeModals();
      _this.openModal($(this));
    });

    $('.modal').on("click", function(e){
      e.preventDefault();
      var $target = $(e.target);
      if ($target.hasClass("chart")) _this.closeModals();
    });
  };

  App.prototype.onDataLoaded = function(results){
    this.dashboard.loadData(results);
    this.chart.loadData(results);
  };

  App.prototype.onFirstLoad = function(){
    $('.start-button').text("Continue");
    this.sound.onFirstLoad();
  };

  App.prototype.onReady = function(){
    this.onResize();
    this.loadListeners();
  };

  App.prototype.onResize = function(){
    this.windowDelta = $(document).height() - $(window).height();
    this.chart.onResize();
    this.onScroll();
  };

  App.prototype.onScroll = function(){
    var _this = this;
    var scrollPercent = $(window).scrollTop() / this.windowDelta;

    this.dashboard.onScroll(scrollPercent);
    this.chart.onScroll(scrollPercent);
  };

  App.prototype.openModal = function($el){
    var el = $el.attr("href");

    if ($el.hasClass("value")) {
      this.chart.show(parseInt($el.attr("data-index")));
    } else {
      $(el).addClass("active");
    }

  };

  return App;

})();

$(function() {
  var app = new App({});
});
