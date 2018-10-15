'use strict';

var Map = (function() {

  function Map(config) {
    var defaults = {
      el: "#map-modal"
    };
    this.opt = _.extend({}, defaults, config);
    this.init();
  }

  Map.prototype.init = function(){
    this.scrollPercent = 0;
    this.data = _.map(this.opt.data, function(d, i){
      d.index = i;
      return d;
    });

    this.loadUI();
  };

  Map.prototype.loadData = function(results) {
    var _this = this;
    var data = this.data;

    _.each(results, function(result){
      var id = result.id;
      var d = data[id];
      if (!d.map) return;

      var rdata = result.data;
      d.meta = _.omit(rdata, 'data');
    });
  };

  Map.prototype.loadUI = function(){
    var el = this.opt.el;

    this.$map = $(el);
    this.$title = $(el + "-title");
    this.$description = $(el + "-description");
    this.$container = $(el + "-container");
    this.$labels = $(el + "-labels");
  };

  Map.prototype.onScroll = function(scrollPercent) {
    if (scrollPercent !== undefined) this.scrollPercent = scrollPercent;
    if (!this.currentData) return false;

    var d = this.currentData;
    var percent = this.scrollPercent;
  };

  Map.prototype.show = function(index){
    var d = this.data[index];
    this.currentData = d;
    this.onScroll();

    var meta = d.meta;
    var data = d.data;

    this.$title.text(meta.title + " by latitude (" + meta.year + ")");
    this.$description.html('Source: <a href="'+meta.sourceURL+'">'+meta.source+'</a>');

    this.$map.addClass("active");
  };

  return Map;

})();
