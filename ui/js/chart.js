'use strict';

var Chart = (function() {

  function Chart(config) {
    var defaults = {
      "parent": "#charts",
      "bounds": [12.1, 12.4, 82.8, 80.4],
      "image": ""
    };
    this.opt = _.extend({}, defaults, config);
    this.init();
  }

  Chart.prototype.init = function(){
    this.$parent = $(this.opt.parent);
    this.id = "chart-" + Math.random().toString(36).substring(8);
    this.loadChart();
  };

  Chart.prototype.getId = function(){
    return this.id;
  };

  Chart.prototype.loadChart = function(){
    var _this = this;

    var html = '';
    html += '<div id="'+this.id+'" class="chart modal">';
      html += '<div class="chart-content">';
        html += '<img src="' + this.opt.image + '" />';
        html += '<div class="chart-bounds"><div class="chart-line"><div class="chart-label"></div></div></div>';
      html += '</div>';
    html += '</div>';

    var $chart = $(html);

    var b = this.opt.bounds;
    var $bounds = $chart.find(".chart-bounds");
    $bounds.css({
      left: b[0] + "%",
      top: b[1] + "%",
      width: b[2] + "%",
      height: b[3] + "%"
    })

    this.$parent.append($chart);
    this.$el = $chart;
    this.$line = $chart.find(".chart-line");
    this.$label = $chart.find(".chart-label");
  };

  Chart.prototype.onScroll = function(scrollPercent, labelText){
    this.$line.css("top", (scrollPercent*100) + "%");
    this.$label.text(labelText);
  };

  Chart.prototype.show = function(){
    this.$chart.addClass("active");
  };

  return Chart;

})();
