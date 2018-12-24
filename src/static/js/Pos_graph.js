
var g = {
    data: null,
    force:null,

};
var div ;
var scale;
function Build_Pos_Graph(div_id){

   div = div_id;
   g.data = [];
   var width = 1300;
   var height = 550;

    //Create a sized SVG surface within viz:
    var svg = d3.select(div)
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    scale = d3.scale.linear()
                    .domain([0,1000])
                    .range([10, 50]);

    g.link = svg.selectAll(".link"),
    g.node = svg.selectAll(".node");

    //Create a graph layout engine:
    g.force = d3.layout.force()
        .linkDistance(10)
        .charge(-500)
        .gravity(0.07)
        .size([width, height])
    //that invokes the tick method to draw the elements in their new location:
    .on("tick", tick);

    //Draw the graph:
    //Note that this method is invoked again
    //when clicking nodes:
    //update();
    console.log("graph initialized");


   update();

}

function Graph_update(Json){

g.data = null;
g.data = Json;
update();

}


function Graph_Minimize(){
var allnode =  flatten(g.data);
    for (var i=0;i<allnode.length;i++){
        if(allnode[i].children!=null)
        {
        click(allnode[i]);
        }
    }

update();

}




function update() {

    //iterate through original nested data, and get one dimension array of nodes.
    var nodes = flatten(g.data);

    //Each node extracted above has a children attribute.
    //from them, we can use a tree() layout function in order
    //to build a links selection.
    var links = d3.layout.tree().links(nodes);

    // pass both of those sets to the graph layout engine, and restart it
    g.force.nodes(nodes)
        .links(links)
        .start();

    //-------------------
    // create a subselection, wiring up data, using a function to define
    //how it's suppossed to know what is appended/updated/exited
    g.link = g.link.data(links, function (d) {return d.target.id;});

    //Get rid of old links:
    g.link.exit().remove();

    //Build new links by adding new svg lines:
    g.link
        .enter()
        .insert("line", ".node")
        .attr("class", "link");

    // create a subselection, wiring up data, using a function to define
    //how it's suppossed to know what is appended/updated/exited
    g.node = g.node.data(nodes, function (d) {return d.id;});
    //Get rid of old nodes:
    g.node.exit().remove();
    //-------------------
    //create new nodes by making groupd elements, that contain circls and text:
    var nodeEnter = g.node.enter()
        .append("g")
        .attr("class", "node")
        .on("click", click)
        .call(g.force.drag);
//        .on("mouseover", mouseover)
//        .on("mouseout", mouseout);
//    //circle within the single node group:
    nodeEnter.append("title")
        .text(function (d) {
        return "count: "+d.size;
    });
    nodeEnter.append("circle")
        .attr("r", function (d) {return scale(d.size);});
    //text within the single node group:
    nodeEnter.append("text")
        .attr("dy", ".35em")
        .text(function (d) {
        return d.name;
    });

    //All nodes, do the following:
    g.node.select("circle")
        .style("fill", color); //calls delegate
    //-------------------
}


// Invoked from 'update'.
// The original source data is not the usual nodes + edge list,
// but that's what's needed for the force layout engine.
// So returns a list of all nodes under the root.
function flatten(data) {
    var nodes = [],
        i = 0;
    //count only children (not _children)
    //note that it doesn't count any descendents of collapsed _children
    //rather elegant?
    function recurse(node) {
        if (node.children) node.children.forEach(recurse);
        if (!node.id) node.id = ++i;
        nodes.push(node);
    }
    recurse(data);

    //Done:
    return nodes;
}




//Invoked from 'update'
//Return the color of the node
//based on the children value of the
//source data item: {name=..., children: {...}}
function color(d) {
    return d._children ? "#3182bd" // collapsed package
    :
    d.children ? "#c6dbef" // expanded package
    :
        "#fd8d3c"; // leaf node
}






// Toggle children on click by switching around values on _children and children.
function click(d) {
    //if (d3.event.defaultPrevented) return; // ignore drag
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else {
        d.children = d._children;
        d._children = null;
    }
    //
    update();
}





//event handler for every time the force layout engine
//says to redraw everthing:
function tick() {
    width = $(div).width();
    height = $(div).height();
//    console.log("tick width"+width);
//    console.log("tick height"+height);
    r=6;
     g.node.attr("cx", function(d) { return d.x = Math.max(r, Math.min(width - r, d.x)); })
      .attr("cy", function(d) { return d.y = Math.max(r, Math.min(height - r, d.y)); });

    //redraw position of every link within the link set:
    g.link.attr("x1", function (d) {
        return d.source.x;
    })
        .attr("y1", function (d) {
        return d.source.y;
    })
        .attr("x2", function (d) {
        return d.target.x;
    })
        .attr("y2", function (d) {
        return d.target.y;
    });
    //same for the nodes, using a functor:
    g.node.attr("transform", function (d) {
        return "translate(" + d.x + "," + d.y + ")";
    });
//    g.node.each(collide(0.5)); //Added
}





//{
//    name: "flare",
//    children: [{
//        name: "analytics",
//        children: [{
//            name: "cluster",
//            children: [{
//                name: "AgglomerativeCluster",
//                size: 3949
//            }, {
//                name: "CommunityStructure",
//                size: 3812
//            }, {
//                name: "HierarchicalCluster",
//                size: 6714
//            }, {
//                name: "MergeEdge",
//                size: 743
//            }],
//            size: 3000
//        }, {
//            name: "graph",
//            children: [{
//                name: "BetweennessCentrality",
//                size: 3534
//            }, {
//                name: "LinkDistance",
//                size: 5731
//            }, {
//                name: "MaxFlowMinCut",
//                size: 7840
//            }, {
//                name: "ShortestPaths",
//                size: 5914
//            }, {
//                name: "SpanningTree",
//                size: 3416
//            }],
//            size: 1000
//        }, {
//            name: "optimization",
//            children: [{
//                name: "AspectRatioBanker",
//                size: 7074
//            }],
//            size: 500
//        }]
//    }]
//};
