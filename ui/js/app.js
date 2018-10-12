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
        {"el": "#surface", "url": "data/land.json", "label": "Land", "type": "pie"},
        {"el": "#surface", "label": "Water", "type": "pie"},
        {"el": "#surface", "url": "data/ice.json", "label": "Ice sheet", "type": "pie"}
      ]
    };
    this.opt = _.extend({}, defaults, config);
    this.init();
  }

  function formatNumber(value) {
    var append = "";

    if (value >= 1000000) {
      append = "M";
      value = Math.round(value / 1000000);
    } else if (value >= 1000) {
      append = "K";
      value = Math.round(value / 1000);
    }

    return value.toLocaleString() + append;
  }

  function lerp(a, b, percent) {
    return (1.0*b - a) * percent + a;
  }

  function lim(v, min, max) {
    return (Math.min(max, Math.max(min, v)));
  }

  function roundToNearest(value, nearest) {
    return Math.round(value / nearest) * nearest;
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
      var $el = $(d.el);

      entry.$el = $el;
      entry.$bar = $el.find('.bar');
      entry.$list = $el.find('.list');
      entry.$pie = $el.find('.pie');
      entry.$value = $el.find('.value');

      // init chart
      if (d.chart) {
        entry.chart = new Chart({
          image: d.chart
        });
        entry.$value.addClass("modal-open");
        entry.$value.attr("href", "#" + entry.chart.getId());
      }

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
    var _this = this;
    var data = _this.data;
    var pies = _.filter(data, function(d){ return d.type==="pie" && !d.url; });
    pies = _.object(_.map(pies, function(p){ return [p.el, {results: [{id: p.index}]}]; }));

    _.each(results, function(result){
      var id = result.id;
      var d = data[id];
      var rdata = result.data;
      d.meta = _.omit(rdata, 'data');

      if (d.type==="bar") {
        var bdata = result.data.data;
        var values = _.filter(bdata, function(v){ return v!=="-"; })
        var vmin = _.min(values);
        var vmax = _.max(values);
        var newData = _.map(bdata, function(value){
          var normValue = 0;
          if (value !== "-") normValue = norm(value, vmin, vmax);
          return {
            "value": value,
            "norm": normValue
          }
        });
        d.data = newData;
      }

      if (d.type==="pie") {
        if (_.has(pies, d.el)) pies[d.el].results.push(result)
        else pies[d.el] = {results: [result]}
      }

      if (d.type==="list") {
        var cdata = result.data.data;
        var ref = result.data.ref;
        cdata = _.map(cdata, function(dlist){
          return _.map(dlist, function(i){
            return ref[i];
          })
        });
        d.data = cdata;
      }
    });
    var bars = _.filter(data, function(d){ return d.type==="bar"; });
    var lists = _.filter(data, function(d){ return d.type==="list"; });

    _.each(bars, function(p, i){
      var meta = p.meta;
      var $source = $('<div class="source"><a href="'+meta.sourceURL+'">'+meta.source+'</a>, '+meta.year+'</div>');
      p.$el.append($source);
    });

    _.each(lists, function(p, i){
      var meta = p.meta;
      var $source = $('<div class="source"><a href="'+meta.sourceURL+'">'+meta.source+'</a>, '+meta.year+'</div>');
      p.$el.append($source);
    });

    _.each(pies, function(p, key){
      var results = _.sortBy(p.results, 'id');
      var dresults = _.filter(results, function(r){ return r.data; });
      var nresult = _.find(results, function(r){ return !r.data; });
      var count = dresults[0].data.data.length;

      // create html
      var $el = $(key);
      var $pie = $el.find(".pie");
      _.each(results, function(r){
        var d = data[r.id];
        var $del = $('<div><div class="label">'+d.label+'</div><div class="value"></div></div>');
        d.$value = $del.find('.value');
        d.$el = $del;
        $pie.append(d.$el);
      });

      // add source
      var sourcesHTML = _.map(dresults, function(r){
        var source = r.data.source;
        var url = r.data.sourceURL;
        var year = r.data.year;
        return '<a href="'+url+'">'+source+'</a>, '+year;
      });
      sourcesHTML = '<div class="source">'+sourcesHTML.join(". ")+"</div>";
      $el.append($(sourcesHTML));

      var pieData = [];
      _.times(count, function(i){
        var pd = [];
        var total = 0
        _.each(dresults, function(r){
          var d = data[r.id];
          var value = r.data.data[i];
          if (value==="-") value = 0;
          pd.push({id: r.id, label: d.label, value: value});
          total += value;
        });
        var difference = 1.0 - total;
        difference = lim(difference, 0, 1);
        pd.push({id: nresult.id, label: data[nresult.id].label, value: difference});
        pd = _.sortBy(pd, 'id');
        pieData.push(pd);
      });

      pies[key].data = pieData;
      pies[key].results = results;
    });

    this.bars = bars;
    this.lists = lists;
    this.pies = pies;
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

    var lat0 = lerp(90, -89, scrollPercent);
    var lat1 = lat0 - 1;

    // update label
    if (lat0 < 0) this.$label.addClass("below");
    else this.$label.removeClass("below");

    function formatLat(lat) {
      lat = round(lat, 1);
      if (lat < 0) lat = -lat + "°S";
      else if (lat > 0) lat += "°N";
      else lat += "°";
      return lat;
    }
    lat0 = formatLat(lat0);
    lat1 = formatLat(lat1);

    this.$label.html(lat0 + " <small>to</small> " + lat1);

    // update map highlight
    var top = lerp(0, 100-(100/90), scrollPercent);
    this.$highlight.css("top", top+"%");

    // update bars
    _.each(this.bars, function(b){
      _this.updateBar(b, scrollPercent);
    });

    // update pies
    _.each(this.pies, function(p, el){
      _this.updatePie(p, scrollPercent);
    });

    // update lists
    _.each(this.lists, function(p){
      _this.updateList(p, scrollPercent);
    });
  };

  App.prototype.openModal = function(el){
    $(el).addClass("active");
  };

  App.prototype.updateBar = function(d, percent){
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
      d.$el.removeClass('noData');
    } else {
      d.$el.addClass('noData');
    }
    d.$value.text(text);
    d.$bar.css("transform", "scale3d(1,"+nvalue+",1)");
    if (d.chart) d.chart.onScroll(percent, text);
  };

  App.prototype.updateList = function(d, percent){
    var html = "";
    var len = d.data.length;
    var index = Math.round((len-1) * percent);
    var data = d.data[index];

    _.each(data, function(item){
      html += '<div>' + item + '</div>';
    });

    if (html.length <= 0) {
      html = "<div>No data</div>";
      d.$el.addClass('noData');
    } else {
      d.$el.removeClass('noData');
    }
    d.$list.html(html);
  };

  App.prototype.updatePie = function(d, percent){
    var data = this.data;
    var len = d.data.length;
    var index = Math.round((len-1) * percent);
    var v = d.data[index];
    var html = "";
    var count = d.results.length;

    _.each(d.results, function(r, i){
      var dd = data[r.id];
      var value = v[i].value;
      dd.$value.text(Math.round(value*100) + "%");
      dd.$el.css('height', (value*100) + "%");
      if (value <= 0) dd.$el.css('display', 'none');
      else dd.$el.css('display', '');
    })

  };

  return App;

})();

$(function() {
  var app = new App({});
});
