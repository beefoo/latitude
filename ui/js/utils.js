function easeIn(t){
  return t*(2-t)
}

function formatLat(lat) {
  lat = round(lat, 1);
  if (lat < 0) lat = -lat + "°S";
  else if (lat > 0) lat += "°N";
  else lat += "°";
  return lat;
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

function getPieData(data, results) {
  var pies = _.filter(data, function(d){ return d.type==="pie" && !d.url; });
  pies = _.object(_.map(pies, function(p){ return [p.el, {results: [{id: p.index}]}]; }));

  _.each(results, function(result){
    var id = result.id;
    var d = data[id];
    if (d.type==="pie") {
      if (_.has(pies, d.el)) pies[d.el].results.push(result)
      else pies[d.el] = {results: [result]}
    }
  });

  _.each(pies, function(p, key){
    var results = _.sortBy(p.results, 'id');
    var dresults = _.filter(results, function(r){ return r.data; });
    var nresult = _.find(results, function(r){ return !r.data; });
    var count = dresults[0].data.data.length;

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

  return pies;
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
