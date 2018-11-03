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
    this.data = _.map(this.opt.data, function(d, i){
      d.index = i;
      return d;
    });

    this.loadSounds();
  };

  Sound.prototype.loadData = function(results) {

  };

  Sound.prototype.onScroll = function(scrollPercent) {

  };

  Sound.prototype.loadSounds = function(){
    var _this = this;
    var audioSrc = this.opt.audioSrc;

    $.getJSON(this.opt.sprites, function(sprites) {
      console.log("Loaded sprites: ", sprites)
      _this.sound1 = new Howl({ src: audioSrc, sprite: sprites });
      _this.sound2 = new Howl({ src: audioSrc, sprite: sprites });
      console.log("Sound loaded.");
    });
  };

  Sound.prototype.onFirstLoad = function(){
    Howler.ctx.resume();
  };

  return Sound;

})();
