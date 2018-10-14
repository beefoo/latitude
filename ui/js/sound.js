'use strict';

var Sound = (function() {

  function Sound(config) {
    var defaults = {
      el: "#chart",
      chords: [
        ["D","E","Gb","A","B"],
        ["D","E","Gb","A","B"],
        ["Db","E","Gb","A"],
        ["Db","E","Gb","A","B"],
        ["D","E","Gb","Ab","A","B"],
        ["Db","E","Gb","Ab","A","B"],
        ["Db","Gb","Ab","A"],
        ["Db","Gb","Ab","A","B"],
        ["Db","E","Gb","Ab","A","B"],
        ["D","E","Gb","Ab","A"],
        ["D","E","Gb","A"]
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
    console.log("Loading "+notes.length*(octaveRange[1]-octaveRange[0]+1)+ " notes...");

    _.each(notes, function(note){
      for (var octave = octaveRange[0]; octave <= octaveRange[1]; octave++) {
        var filename = filePath.replace("{note}", note).replace("{octave}", octave);
      }
    });
  };

  Sound.prototype.onFirstLoad = function(){
    Pizzicato.context.resume();
  };

  return Sound;

})();
