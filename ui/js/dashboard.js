'use strict';

var Dashboard = (function() {

  function Dashboard(config) {
    var defaults = {
    };
    this.opt = _.extend({}, defaults, config);
    this.init();
  }

  Dashboard.prototype.init = function(){
    this.$mapHighlight = $("#map-highlight");
    this.$mapLabel = $("#map-label");

    this.data = this.opt.data;
    this.loadUI();
  };

  Dashboard.prototype.loadData = function(results) {
    var _this = this;
    var data = this.data;
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

  Dashboard.prototype.loadUI = function(data) {
    var _this = this;
    _.each(this.data, function(d, i){
      var entry = _this.data[i];
      entry.index = i;
      var $el = $(d.el);

      if (d.type==="pie") {
        var $pieSlice = $('<div><div class="label">'+d.label+'</div><a class="value"></a></div>');
        var $value = $pieSlice.find('.value');
        entry.$el = $pieSlice;
        $el.find(".pie").append($pieSlice);
      } else {
        entry.$el = $el;
      }

      entry.$bar = entry.$el.find('.bar');
      entry.$list = entry.$el.find('.list');
      entry.$pie = entry.$el.find('.pie');
      entry.$value = entry.$el.find('.value');

      // init chart
      if (d.chart && entry.$value.length) {
        entry.chart = new Chart({
          image: d.chart
        });
        entry.$value.addClass("modal-open");
        entry.$value.attr("href", "#" + entry.chart.getId());
      }
    });
  };

  Dashboard.prototype.onScroll = function(scrollPercent) {
    var _this = this;
    
    this.updateMap(scrollPercent);

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

  Dashboard.prototype.updateMap = function(scrollPercent) {
    var lat0 = lerp(90, -89, scrollPercent);
    var lat1 = lat0 - 1;

    // update label
    if (lat0 < 0) this.$mapLabel.addClass("below");
    else this.$mapLabel.removeClass("below");

    function formatLat(lat) {
      lat = round(lat, 1);
      if (lat < 0) lat = -lat + "°S";
      else if (lat > 0) lat += "°N";
      else lat += "°";
      return lat;
    }
    lat0 = formatLat(lat0);
    lat1 = formatLat(lat1);

    this.$mapLabel.html(lat0 + " <small>to</small> " + lat1);

    // update map highlight
    var top = lerp(0, 100-(100/90), scrollPercent);
    this.$mapHighlight.css("top", top+"%");
  };

  Dashboard.prototype.updateBar = function(d, percent){
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

  Dashboard.prototype.updateList = function(d, percent){
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

  Dashboard.prototype.updatePie = function(d, percent){
    var data = this.data;
    var len = d.data.length;
    var index = Math.round((len-1) * percent);
    var v = d.data[index];
    var html = "";
    var count = d.results.length;

    _.each(d.results, function(r, i){
      var dd = data[r.id];
      var value = v[i].value;
      var text = Math.round(value*100) + "%"
      dd.$value.text(text);
      dd.$el.css('height', (value*100) + "%");
      if (value <= 0) dd.$el.css('display', 'none');
      else dd.$el.css('display', '');
      if (dd.chart) dd.chart.onScroll(percent, text);
    })

  };

  return Dashboard;

})();
