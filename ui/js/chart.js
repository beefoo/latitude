'use strict';

var Chart = (function() {

  function Chart(config) {
    var defaults = {
      el: "#chart"
    };
    this.opt = _.extend({}, defaults, config);
    this.init();
  }

  Chart.prototype.init = function(){
    this.scrollPercent = 0;
    this.data = _.map(this.opt.data, function(d, i){
      d.index = i;
      return d;
    });

    this.loadUI();
  };

  Chart.prototype.loadData = function(results) {
    var _this = this;
    var data = this.data;

    _.each(results, function(result){
      var id = result.id;
      var d = data[id];
      if (!d.chart) return;

      var rdata = result.data;
      d.meta = _.omit(rdata, 'data');

      var lineData = rdata.data;
      var count = lineData.length;
      var cleanedData = _.filter(lineData, function(ld) { return ld !== "-"; });
      d.minValue = _.min(cleanedData);
      d.maxValue = _.max(cleanedData);

      lineData = _.map(lineData, function(value, i){
        var lat = lerp(90, -90, i/(count-1));
        var normValue = 0;
        if (value !== "-") normValue = norm(value, d.minValue, d.maxValue);
        return { x: value, y: lat, value: value, norm: normValue };
      });
      d.data = lineData;
      d.cleanData = _.filter(lineData, function(ld) { return ld.x !== "-"; });
    });
  };

  Chart.prototype.loadUI = function(){
    var el = this.opt.el;

    this.$chart = $(el);
    this.$title = $(el + "-title");
    this.$description = $(el + "-description");
    this.$container = $(el + "-container");
    this.$line = $(el + "-line");
    this.$lat = $(el + "-lat");
    this.$value = $(el + "-value");
    this.$circle = $(el + "-circle");

    var svg = d3.select(el + "-content");
    var container = svg.append("g");
    var path = container.append("path")
      .attr("class", "dataLine");

    this.svg = svg;
    this.path = path;

    this.onResize();
  };

  Chart.prototype.onResize = function(){
    var width = this.$container.width();
    var height = this.$container.height();
    this.width = width;
    this.height = height;

    this.svg.attr("width", width)
      .attr("height", height);

    var x = d3.scaleLinear().range([0, width]);
    var y = d3.scaleLinear().range([height, 0]);
    this.xRange = x;
    this.yRange = y;
  };

  Chart.prototype.onScroll = function(scrollPercent) {
    if (scrollPercent !== undefined) this.scrollPercent = scrollPercent;
    if (!this.currentData) return false;

    var d = this.currentData;
    var percent = this.scrollPercent;
    this.$line.css("top", (percent*100) + "%");

    var len = d.data.length;
    var index = Math.round((len-1) * percent);
    var v = d.data[index];
    var value = v.value;
    var nvalue = v.norm;
    var text = "No data";
    if (!isNaN(value)) {
      text = formatNumber(value);
      if (d.prepend) text = d.prepend + text;
      if (d.append) text += d.append;
      this.$circle.css({"left": (nvalue*100) + "%", "display": "block"});
    } else {
      this.$circle.css("display", "none");
    }
    this.$value.text(text);
    this.$lat.text(formatLat(lerp(-90, 90, percent)));

  };

  Chart.prototype.show = function(index){
    var d = this.data[index];
    this.currentData = d;
    this.onScroll();

    var meta = d.meta;
    var data = d.data;
    var cleanData = d.cleanData;

    this.$title.text(meta.title + " by latitude (" + meta.year + ")");
    this.$description.html('Source: <a href="'+meta.sourceURL+'">'+meta.source+'</a>');

    var x = this.xRange;
    var y = this.yRange;
    var minValue = d.minValue;
    var maxValue = d.maxValue;

    // Scale the range of the data
    var line = d3.line()
      .x(function(d) { return x(d.x)})
      .y(function(d) { return y(d.y)});
    x.domain([minValue, maxValue]);
    y.domain([-90, 90]);

    // Set the data
    this.path
      .datum(cleanData)
      .attr("d", line);
    this.$chart.addClass("active");
  };

  return Chart;

})();
