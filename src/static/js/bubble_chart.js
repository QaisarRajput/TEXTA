function load_histograms(word_count,div_id,b_count){
	
		// return a list whick works with this bubble chart
		function histograms_list(word_count_list){
				var hist_list = []
				console.log(word_count_list);
                if(word_count_list.length<25)
                {
                 b_count=word_count_list.length;
                }
				for(var i=0; i < b_count; i++){
				  hist_list.push({packageName: word_count_list[i][0], className: word_count_list[i][0].toString(), value: Math.round(word_count_list[i][1])});
				  }
				  console.log('hist: '+hist_list[0].className);
				 return {children: hist_list};
		}
		//give a different random color
		function getRandomColor() {
		    var letters = '0123456789ABCDEF'.split('');
		    var color = '#';
		    for (var i = 0; i < 6; i++ ) {
		        color += letters[Math.floor(Math.random() * 16)];
		    }
		    return color;
		}
		
		var width_d = $(div_id).width();
        var height_d = $(div_id).height();
        var format = d3.format(",d"),
		    color = d3.scale.category20c();
		
		var bubble = d3.layout.pack()
		    .sort(null)
		    .size([width_d, height_d])
		    .padding(1.5);
		
		var svg = d3.select(div_id.toString()).append("svg")
		    .attr("width", width_d)
		    .attr("height", height_d)
		    .attr("class", "bubble");
		
		var node = svg.selectAll(".node")
		      .data(bubble.nodes(histograms_list(word_count))
		      .filter(function(d) { return !d.children; }))
		    .enter().append("g")
		      .attr("class", "node")
		      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
		
		  node.append("title")
		      .text(function(d) { return d.className + ": " + format(d.value); });
		      
		
		  node.append("circle")
		      .attr("r", function(d) { return d.r; })
		      .style("fill", function(d) { return color(getRandomColor()); })
		      .on("click", function(d) {
		        Add_Btext_Search(d.className);
		        });
              
          
		  node.append("text")
		      .attr("dy", ".3em")
		      .style("text-anchor", "middle")
		      .text(function(d) { return d.className.substring(0, d.r / 3); });
		
		d3.select(self.frameElement).style("height", height_d + "px");
	}


//
//function load_buckets(bucket_count,div_id){
//	console.log('i am in bucket load');
//		// return a list whick works with this bubble chart
//		function buckets_list(bucket_count_list){
//				var bucket_list = []
//				console.log(bucket_count_list);
//				for(var i=0; i < bucket_count_list.length; i++){
//				  bucket_list.push({packageName: bucket_count_list[i][0].toString(), className: bucket_count_list[i][0].toString(), value: Math.round(bucket_count_list[i][1])});
//				  }
//				  console.log('bucket: '+bucket_list[0].className);
//				 return {children: bucket_list};
//		}
//		//give a different random color
//		function getRandomColor() {
//		    var letters = '0123456789ABCDEF'.split('');
//		    var color = '#';
//		    for (var i = 0; i < 6; i++ ) {
//		        color += letters[Math.floor(Math.random() * 16)];
//		    }
//		    return color;
//		}
//		
//		var diameter = 960,
//		    format = d3.format(",d"),
//		    color = d3.scale.category20c();
//		
//		var bubble = d3.layout.pack()
//		    .sort(null)
//		    .size([diameter, diameter])
//		    .padding(1.5);
//		
//		var svg = d3.select(div_id.toString()).append("svg")
//		    .attr("width", diameter)
//		    .attr("height", diameter)
//		    .attr("class", "bubble");
//		
//		var node = svg.selectAll(".node")
//		      .data(bubble.nodes(buckets_list(bucket_count))
//		      .filter(function(d) { return !d.children; }))
//		    .enter().append("g")
//		      .attr("class", "node")
//		      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
//		
//		  node.append("title")
//		      .text(function(d) { return d.className + ": " + format(d.value); });
//		      
//		  
//    
//		  node.append("circle")
//		      .attr("r", function(d) { return d.r; })
//		      .style("fill", function(d) { return color(getRandomColor()); })
//		      .on("click", function(d) {
//		        console.log('i am in show cluster function');
//		    	document.getElementById(d.className).style.display = "block";
//		    	console.log('bucket clicked: '+d.className);
//                
//		        });
//          
//          node.on("contextmenu", function(d) {
//                console.log(d.className);  
//                d3.event.preventDefault();
//                Dialouge_start("Loading..!");
//                Load_DataTable(d.className);
//                });
//		  node.append("text")
//		      .attr("dy", ".3em")
//		      .style("text-anchor", "middle")
//		      .text(function(d) { return d.className.substring(0, d.r / 3); });
//		
//		d3.select(self.frameElement).style("height", diameter + "px");
//	}
//
//function Add_Btext_Search(text){
//    
//    AddtoSearch(null,null,text);
//    
//    
//}
//
