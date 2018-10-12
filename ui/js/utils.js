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
