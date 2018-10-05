'use strict';

var App = (function() {

  function App(config) {
    var defaults = {};
    this.opt = _.extend({}, defaults, config);
    this.init();
  }

  function lerp(a, b, percent) {
    return (1.0*b - a) * percent + a;
  }

  function round(value, precision) {
    return +value.toFixed(precision);
  }

  App.prototype.init = function(){
    this.$highlight = $("#map-highlight");
    this.$label = $("#map-label");

    this.onResize();
    this.loadListeners();
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

  App.prototype.onResize = function(){
    this.windowDelta = $(document).height() - $(window).height();
    this.onScroll();
  };

  App.prototype.onScroll = function(){
    var scrollPercent = $(window).scrollTop() / this.windowDelta;

    var lat = lerp(90, -90, scrollPercent);
    lat = round(lat, 1);

    // update label
    if (lat < 0) lat = -lat + "°S";
    else if (lat > 0) lat += "°N";
    else lat += "°";

    this.$label.text(lat);
  };

  return App;

})();

$(function() {
  var app = new App({});
});
