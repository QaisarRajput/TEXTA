

var container = "svg";

var w ;
var h ;



var wordSize;
var layout;
var div;

function generate(result,div_id) {
    div = div_id;
    w = $(div_id).width();
    h = $(div_id).height()-10;
    wordSize = 12;

    var frequency_list = [];
    var len = result.length;
    for (var i = 0; i < len; i++) {

        var obj = result[i];
        frequency_list.push({
            text : obj.text,
            freq : obj.freq,
            time : 0
        });

    }
    frequency_list.sort(function(a,b) { return parseFloat(b.freq) - parseFloat(a.freq) } );


    for(var t = 0 ; t < len ; t++)
    {
    var addTime = (10 * t) +500;
    frequency_list[t].time=addTime;
    }


        for(i in frequency_list){
            if(frequency_list[i].freq*wordSize > 160)
                wordSize = 3;
        }
     console.log(frequency_list);

var sizeScale = d3.scale.linear()
                       .domain([0, d3.max(frequency_list, function(d) { return d.freq} )])
                                        .range([10, 95]); // 95 because 100 was causing stuff to be missing


        layout = d3.layout.cloud().size([w, h])
        .words(frequency_list)
        .padding(5)
        .rotate(function() { return ~~(Math.random() * 2) * 90; })
        .font("Impact")
        .fontSize(function(d) { return sizeScale(d.freq); })
          .on("end",draw)
          .start();
    }
    function draw(words) {


var fill = d3.scale.category20();

        d3.select(container).remove();

        d3.select(div).append(container)
        .attr("width", w)
        .attr("height", h)
             .append("g")
        .attr("transform", "translate(" + [w/2, h/2] + ")")
          .selectAll("text")
        .data(words)
          .enter().append("text")

        .transition()
        .duration(function(d) { return d.time}  )
        .attr('opacity', 1)
        .style("font-size", function(d) { return d.size + "px"; })
        .style("font-family", "Impact")
          .style("fill", function(d, i) { return fill(i); })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "rotate(" + d.rotate + ")";
        })
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { return d.text; });

    }




