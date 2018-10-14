'use strict';

var Sound = (function() {

  function Sound(config) {
    var defaults = {
      el: "#chart",
      chords: [
        ["Db", "D", "E", "Gb", "Ab", "A", "B"]
      ],
      octaveRange: [2, 4],
      filePath: "audio/xylophone/{note}{octave}.mp3"
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

  Sound.prototype.loadSounds = function(){
    var chords = this.opt.chords;
    var octaveRange = this.opt.octaveRange;
    var filePath = this.opt.filePath;
    var sounds = [];
    var notes = _.uniq(_.flatten(chords));

    _.each(notes, function(note){
      for (var octave = octaveRange[0]; octave <= octaveRange[1]; octave++) {
        var filename = filePath.replace("{note}", note).replace("{octave}", octave);
        // console.log(filename)
      }
    });
  };

  Sound.prototype.onFirstLoad = function(){
    Pizzicato.context.resume();
  };

  return Sound;

})();
