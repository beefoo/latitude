'use strict';

var Sound = (function() {

  function Sound(config) {
    var defaults = {
      el: "#chart",
      audioSrc: "ui/audio/orchestra.mp3",
      sprites: "ui/audio/orchestra.json"
    };
    this.opt = _.extend({}, defaults, config);
    this.init();
  }

  Sound.prototype.init = function(){
    var _this = this;
    this.data = _.map(this.opt.data, function(d, i){
      d.index = i;
      return d;
    });

    this.dataPromise = $.Deferred();
    this.soundPromise = this.loadSounds();
    this.interactionPromise = $.Deferred();
    this.scrollPercent = 0;

    $.when.apply($, [this.dataPromise, this.soundPromise, this.interactionPromise]).then(function(){
      _this.onReady();
    });
  };

  Sound.prototype.loadData = function(results) {

    var _this = this;
    var data = this.data;

    _.each(results, function(result){
      var id = result.id;
      var d = data[id];
      var rdata = result.data;
      d.meta = _.omit(rdata, 'data');

      if (d.sound) {
        var rddata = result.data.data;
        var values = _.filter(rddata, function(v){ return v!=="-"; })
        var vmin = _.min(values);
        var vmax = _.max(values);
        var newData = _.map(rddata, function(value){
          var normValue = 0;
          if (value !== "-") normValue = norm(value, vmin, vmax);
          return normValue;
        });
        d.data = newData;
      }
    });

    this.dataPromise.resolve();
  };

  Sound.prototype.onScroll = function(scrollPercent) {
    if (scrollPercent !== undefined) this.scrollPercent = scrollPercent;
    if (!this.ready) return false;

    var _this = this;
    var percent = this.scrollPercent;

    _.each(this.data, function(d, i){
      if (d.sound1 && d.sound2) {
        var len = d.data.length;
        var index = Math.round((len-1) * percent);
        var volume = d.data[index];
        _this.sound1.volume(volume, d.sound1);
        _this.sound2.volume(volume, d.sound2);
      }
    });
  };

  Sound.prototype.loadSounds = function(){
    var _this = this;
    var audioSrc = this.opt.audioSrc;
    var deferred = $.Deferred();

    $.getJSON(this.opt.sprites, function(sprites) {
      sprites = _.mapObject(sprites, function(sprite){
        sprite.push(true);
        return sprite;
      })
      console.log("Loaded sprites: ", sprites);
      var first = _.first(_.values(sprites));
      _this.clipDuration = first[1];
      _this.sound1 = new Howl({ src: audioSrc, sprite: sprites });
      _this.sound2 = new Howl({ src: audioSrc, sprite: sprites });
      console.log("Sound loaded.");
      deferred.resolve();
    });

    return deferred;
  };

  Sound.prototype.onFirstLoad = function(){
    Howler.ctx.resume();
    this.interactionPromise.resolve();
  };

  Sound.prototype.onReady = function(){
    var _this = this;
    var data = this.data;
    var half = this.clipDuration / 1000.0 * 0.5;
    this.ready = true;

    _.each(data, function(d, i){
      if (d.sound) {
        var s1 = _this.sound1.play(d.sound);
        var s2 = _this.sound2.play(d.sound);
        _this.sound1.volume(0, s1);
        _this.sound2.volume(0, s2);
        _this.sound2.seek(half, s2);
        data[i].sound1 = s1;
        data[i].sound2 = s2;
      }
    });

    this.onScroll();
  };

  return Sound;

})();
