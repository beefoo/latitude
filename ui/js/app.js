'use strict';

var App = (function() {

  function App(config) {
    var defaults = {
      "data": [
        {"el": "#anomaly", "url": "data/anomaly.json", "type": "bar", "append": "°C", "chart": true, "sound": "flute_Cs6_1_mezzo-forte_normal"},
        {"el": "#emissions", "url": "data/emissions.json", "type": "bar", "append": "M", "chart": true, "sound": "trumpet_Fs4_long_piano_normal"},
        {"el": "#gdp", "url": "data/gdp.json", "type": "bar", "prepend": "$", "chart": true, "sound": "saxophone_Gs4_1_forte_normal"},
        {"el": "#population", "url": "data/pop_count.json", "type": "bar", "chart": true, "sound": "long-synth-choir_C_major"},
        {"el": "#temperature", "url": "data/temperature.json", "type": "bar", "append": "°C", "chart": true, "sound": "cello_G2_1_forte_arco-normal"},
        {"el": "#vegetation", "url": "data/vegetation.json", "type": "bar", "chart": true, "sound": "viola_D3_1_forte_arco-normal"},
        {"el": "#cities", "url": "data/cities.json", "type": "list", "map": true},
        {"el": "#surface", "url": "data/land.json", "label": "Land", "type": "pie", "chart": true},
        {"el": "#surface", "label": "Ocean", "type": "pie", "title": "Ocean area", "year": 2010, "source": "NASA SEDAC", "sourceURL": "http://sedac.ciesin.columbia.edu/data/set/gpw-v4-land-water-area-rev10", "chart": true, "sound": "double-bass_A1_1_mezzo-forte_arco-normal"},
        {"el": "#surface", "url": "data/ice.json", "label": "Ice sheet", "type": "pie", "chart": true, "sound": "double-bass_A3_1_mezzo-forte_arco-normal"}
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
    this.map = new Map({data: _.map(data, _.clone)});
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
      if (firstLoad) {
        _this.onFirstLoad();
        firstLoad = false;
      }
      _this.closeModals();

    });

    $('.modal-open').on("click", function(e){
      e.preventDefault();
      _this.closeModals();
      _this.openModal($(this));
    });

    $('.modal').on("click", function(e){
      var $target = $(e.target);
      if ($target.hasClass("modal")) {
        if (firstLoad) {
          _this.onFirstLoad();
          firstLoad = false;
        }
        _this.closeModals();
      }
    });

    $('.toggle-sound').on("click", function(e){
      e.preventDefault();
      _this.sound.toggleSound($(this));
    });
  };

  App.prototype.onDataLoaded = function(results){
    this.dashboard.loadData(results);
    this.chart.loadData(results);
    this.map.loadData(results);
    this.sound.loadData(results);
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
    this.map.onScroll(scrollPercent);
    this.sound.onScroll(scrollPercent);
  };

  App.prototype.openModal = function($el){
    var el = $el.attr("href");

    if ($el.hasClass("modal-open-chart")) {
      this.chart.show(parseInt($el.attr("data-index")));

    } else if ($el.hasClass("modal-open-map")) {
      this.map.show(parseInt($el.attr("data-index")));

    } else {
      $(el).addClass("active");
    }

  };

  return App;

})();

$(function() {
  var app = new App({});
});
