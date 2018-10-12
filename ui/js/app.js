'use strict';

var App = (function() {

  function App(config) {
    var defaults = {
      "data": [
        {"el": "#anomaly", "url": "data/anomaly.json", "type": "bar", "append": "°C", "chart": "ui/img/plot/plot_anomaly.png"},
        {"el": "#emissions", "url": "data/emissions.json", "type": "bar", "append": "M", "chart": "ui/img/plot/plot_emissions.png"},
        {"el": "#gdp", "url": "data/gdp.json", "type": "bar", "prepend": "$", "chart": "ui/img/plot/plot_gdp.png"},
        {"el": "#population", "url": "data/pop_count.json", "type": "bar", "chart": "ui/img/plot/plot_pop_count.png"},
        {"el": "#temperature", "url": "data/temperature.json", "type": "bar", "append": "°C", "chart": "ui/img/plot/plot_temperature.png"},
        {"el": "#vegetation", "url": "data/vegetation.json", "type": "bar", "chart": "ui/img/plot/plot_vegetation.png"},
        {"el": "#cities", "url": "data/cities.json", "type": "list"},
        {"el": "#surface", "url": "data/land.json", "label": "Land", "type": "pie", "chart": "ui/img/plot/plot_land.png"},
        {"el": "#surface", "label": "Water", "type": "pie"},
        {"el": "#surface", "url": "data/ice.json", "label": "Ice sheet", "type": "pie", "chart": "ui/img/plot/plot_ice.png"}
      ]
    };
    this.opt = _.extend({}, defaults, config);
    this.init();
  }

  App.prototype.init = function(){
    var _this = this;

    this.data = this.opt.data;
    var dataPromise = this.loadData();

    this.dashboard = new Dashboard({data: this.data});

    $.when.apply($, [dataPromise]).then(function(data){
      _this.onDataLoaded(data);
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
      deferred.resolve(arguments);
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
      _this.openModal($(this).attr("href"));
    });

    $('.modal').on("click", function(e){
      e.preventDefault();
      var $target = $(e.target);
      if ($target.hasClass("chart")) _this.closeModals();
    });
  };

  App.prototype.onDataLoaded = function(results){
    this.dashboard.loadData(results);
  };

  App.prototype.onFirstLoad = function(){
    $('.start-button').text("Continue");
  };

  App.prototype.onReady = function(){
    this.onResize();
    this.loadListeners();
  };

  App.prototype.onResize = function(){
    this.windowDelta = $(document).height() - $(window).height();
    this.onScroll();
  };

  App.prototype.onScroll = function(){
    var _this = this;
    var scrollPercent = $(window).scrollTop() / this.windowDelta;

    this.dashboard.onScroll(scrollPercent);
  };

  App.prototype.openModal = function(el){
    $(el).addClass("active");
  };

  return App;

})();

$(function() {
  var app = new App({});
});
