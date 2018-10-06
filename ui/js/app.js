'use strict';

var App = (function() {

  function App(config) {
    var defaults = {
      "data": [
        {"el": "#anomaly", "url": "data/anomaly.json", "type": "bar"},
        {"el": "#emissions", "url": "data/emissions.json", "type": "bar"},
        {"el": "#gdp", "url": "data/gdp.json", "type": "bar"},
        {"el": "#population", "url": "data/pop_count.json", "type": "bar"},
        {"el": "#temperature", "url": "data/temperature.json", "type": "bar"},
        {"el": "#vegetation", "url": "data/vegetation.json", "type": "bar"},
        {"el": "#cities", "url": "data/countries.csv", "type": "list"},
        {
          "el": "#surface-type",
          "urls": ["data/land.json", "data/ice.json"],
          "type": "pie",
          "default": {}
        }
      ]
    };
    this.opt = _.extend({}, defaults, config);
    this.init();
  }

  function lerp(a, b, percent) {
    return (1.0*b - a) * percent + a;
  }

  function loadCSV(csvFilename, id){
    var deferred = $.Deferred();
    Papa.parse(csvFilename, {
      download: true,
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: function(results) {
        if (results.errors.length) console.log(results.errors[0].message);
        console.log("Found "+results.data.length+" rows in "+csvFilename);
        deferred.resolve({ "id": id, "data": results.data });
      }
    });
    return deferred.promise();
  }

  function loadJSON(jsonFilename, id){
    var _this = this;
    var deferred = $.Deferred();
    $.getJSON(jsonFilename, function(data) {
      console.log("Found "+data.data.length+" entries in "+jsonFilename);
      deferred.resolve({ "id": id, "data": data });
    }).fail(function() {
      console.log("No data found in "+jsonFilename);
      deferred.resolve({ "id": id, "data": [] });
    });
    return deferred.promise();
  }

  function norm(value, a, b){
    var denom = (b - a);
    if (denom > 0 || denom < 0) return (1.0 * value - a) / denom;
    else return 0;
  }

  function round(value, precision) {
    return +value.toFixed(precision);
  }

  App.prototype.init = function(){
    var _this = this;
    this.$highlight = $("#map-highlight");
    this.$label = $("#map-label");

    this.data = this.opt.data;
    var dataPromise = this.loadData();

    $.when.apply($, [dataPromise]).then(function(data){
      _this.onDataLoaded(data);
      _this.onReady();
    });
  };

  App.prototype.loadData = function(){
    var _this = this;
    var deferreds = [];
    var deferred = $.Deferred();
    _.each(this.data, function(d, i){
      _this.data[i].index = i;
      var $el = $(d.el);
      _this.data[i].$value = $el.find('.value');
      _this.data[i].$label = $el.find('.label');
      var urls = [];
      if (d.urls) urls = d.urls;
      if (d.url) urls.push(d.url);
      _.each(urls, function(url){
        if (url.endsWith(".csv")) deferreds.push(loadCSV(url, i));
        else deferreds.push(loadJSON(url, i));
      });
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
  };

  App.prototype.onDataLoaded = function(results){
    var _this = this;
    var data = _this.data;
    _.each(results, function(result){
      var id = result.id;
      var d = data[id];

      if (d.type==="bar") {
        var rdata = result.data.data;
        var values = _.filter(rdata, function(v){ return v!=="-"; })
        var vmin = _.min(values);
        var vmax = _.max(values);
        var newData = _.map(rdata, function(value){
          var normValue = 0;
          if (value !== "-") normValue = norm(value, vmin, vmax);
          return {
            "value": value,
            "norm": normValue
          }
        });
        d.data = newData;
      }

    });
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

    var lat = lerp(90, -90, scrollPercent);
    lat = round(lat, 1);

    // update label
    if (lat < 0) this.$label.addClass("below");
    else this.$label.removeClass("below");
    if (lat < 0) lat = -lat + "°S";
    else if (lat > 0) lat += "°N";
    else lat += "°";
    this.$label.text(lat);

    // update map highlight
    var top = lerp(0, 100-(100/180), scrollPercent);
    this.$highlight.css("top", top+"%");

    // update data dashboard
    _.each(this.data, function(d){
      if (d.type==="list") _this.updateList(d, scrollPercent);
      else if (d.type==="pie") _this.updatePie(d, scrollPercent);
      else _this.updateBar(d, scrollPercent);
    });
  };

  App.prototype.updateBar = function(d, percent){
    var len = d.data.length;
    var index = Math.round((len-1) * percent);
    var v = d.data[index];
    d.$label.text(v.value.toLocaleString());
  };

  App.prototype.updateList = function(d, percent){

  };

  App.prototype.updatePie = function(d, percent){

  };

  return App;

})();

$(function() {
  var app = new App({});
});
