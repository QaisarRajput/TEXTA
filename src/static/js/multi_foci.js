var nodes=[];
var force,node,fill;

function Build_Foci(no_cluster,div){

var width = $(div).width(),
    height = $(div).height();

fill = d3.scale.category10();

//var nodes = [ {
//              "id":0,
//              "index":0,
//              "title":"Tweet"
//              },
//              {
//              "id":2,
//              "index":1,
//               "title":"Tweet"
//              },
//              {
//              "id":1,
//              "index":2,
//               "title":"Tweet"
//              },
//              {
//              "id":3,
//              "index":3,
//               "title":"Tweet"
//              },
//              
//            ];
//var foci = Get_Points(no_cluster);
    var foci=[{x: 350, y: 350}, {x: 650, y: 350}, {x: 900, y: 350}]; 
    console.log(foci);


var svg = d3.select(div).append("svg")
    .attr("width", width)
    .attr("height", height);
    
    force = d3.layout.force()
    .nodes(nodes)
    .links([])
    .gravity(0)
    .size([width, height])
    .on("tick", tick);

node = svg.selectAll("circle");

function tick(e) {
  var k = .1 * e.alpha;

  // Push nodes toward their designated focus.
  nodes.forEach(function(o, i) {
    o.y += (foci[o.id].y - o.y) * k;
    o.x += (foci[o.id].x - o.x) * k;
  });

  node.attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; });
  }

}


function Foci_Update(ndata){
  
  
 
  
  
  nodes = ndata;
 force.start();
    node = node.data(nodes);

  node.enter().append("circle")
      .attr("class", "node")
      .attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; })
      .attr("r", 8)
      .style("fill", function(d) { return fill(d.id); })
      .style("stroke", function(d) { return d3.rgb(fill(d.id)).darker(2); })
      .append("svg:title")
      .text(function(d) { return (d.title).toString(); })      
      .call(force.drag);
 
        
  
}


function Get_Points(no_cluster){

var foci = [];
var b = parseInt(no_cluster/2);
var a = no_cluster - b;
    
var p = parseInt(1300/no_cluster);
var q = parseInt(550/no_cluster);
var i,j;

    for(i=0;i<a;i++)
    {   
       
        for(j=0;j<b;j++)
        {
         foci.push({x:i*p+100,y:j*q+100});
         if(no_cluster==foci.length){break;};
        }
 
        if(no_cluster==foci.length){break;};

        if(no_cluster-1 == foci.length)
        {
          foci.push({x:(i+1)*p+100,y:100});
          break;
        }       
       
    }
//    console.log(foci);
    return foci;
    
}
