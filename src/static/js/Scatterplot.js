

    // register our custom symbols to nvd3
    // make sure your path is valid given any size because size scales if the chart scales.
    nv.utils.symbolMap.set('thin-x', function(size) {
        size = Math.sqrt(size);
        return 'M' + (-size/2) + ',' + (-size/2) +
                'l' + size + ',' + size +
                'm0,' + -(size) +
                'l' + (-size) + ',' + size;
    });

    // create the chart
    var chart;
    
    function ScatterPlot(tweets,sent_str){
    nv.addGraph(function() {
        chart = nv.models.scatterChart()
            .showDistX(true)
            .showDistY(true)
            .useVoronoi(true)
            .showVoronoi(false)
            .color(d3.scale.category10().range())
            .duration(300)
            .showLegend(false);
        
        chart.dispatch.on('renderEnd', function(){
            console.log('render complete');
        });
        
        
        chart.xAxis.tickFormat(d3.format('.02f'));
        chart.yAxis.tickFormat(d3.format('.02f'));
        
        chart.tooltip.enabled();
        chart.tooltip.contentGenerator(function (obj) 
              { 
              console.log(obj.series[0].key);
              return  '<h3>' + JSON.stringify(obj.series[0].key) + '</h3>';
              
              });

        d3.select('#scatter svg')
            .datum(randomData(tweets,sent_str))
            .call(chart);

        nv.utils.windowResize(chart.update);

        chart.dispatch.on('stateChange', function(e) { ('New State:', JSON.stringify(e)); });
        return chart;
    });

    }
    
    function randomData(tweets,sent_str) { 
        var data = [],
            shapes = ['circle'];
        if(sent_str=="frequency"){
        for (i = 0; i < tweets.length; i++) {
            if(tweets[i].frequency_sentiment.polarity_neg==0 && tweets[i].frequency_sentiment.polarity_pos ==0){
                
            
            }
            else{
            data.push({
                key: tweets[i].content_title,
                values: [{
                    x: tweets[i].frequency_sentiment.polarity_neg,
                    y: tweets[i].frequency_sentiment.polarity_pos,
                    size: Math.round(Math.random() * 100) / 100,
                    shape: shapes[i % shapes.length]
                    }]
            });
            }
        }
        }
        if(sent_str=="afinn"){
        for (i = 0; i < tweets.length; i++) {
            if(tweets[i].afinn_sentiment.polarity_neg==0 && tweets[i].afinn_sentiment.polarity_pos ==0){
                
            
            }
            else{
            data.push({
                key: tweets[i].content_title,
                values: [{
                    x: tweets[i].afinn_sentiment.polarity_neg,
                    y: tweets[i].afinn_sentiment.polarity_pos,
                    size: Math.round(Math.random() * 100) / 100,
                    shape: shapes[i % shapes.length]
                    }]
            });
            }
        }
        }
        
        if(sent_str=="nb_single"){
        for (i = 0; i < tweets.length; i++) {
            if(tweets[i].nb_single_sentiment.polarity_neg==0 && tweets[i].nb_single_sentiment.polarity_pos ==0){
                
            
            }
            else{
            data.push({
                key: tweets[i].content_title,
                values: [{
                    x: tweets[i].nb_single_sentiment.polarity_neg,
                    y: tweets[i].nb_single_sentiment.polarity_pos,
                    size: Math.round(Math.random() * 100) / 100,
                    shape: shapes[i % shapes.length]
                    }]
            });
            }
        }
        }
        
        if(sent_str=="nb_non_stop"){
        for (i = 0; i < tweets.length; i++) {
            if(tweets[i].nb_non_stop_sentiment.polarity_neg==0 && tweets[i].nb_non_stop_sentiment.polarity_pos ==0){
                
            
            }
            else{
            data.push({
                key: tweets[i].content_title,
                values: [{
                    x: tweets[i].nb_non_stop_sentiment.polarity_neg,
                    y: tweets[i].nb_non_stop_sentiment.polarity_pos,
                    size: Math.round(Math.random() * 100) / 100,
                    shape: shapes[i % shapes.length]
                    }]
            });
            }
        }
        }
        
        if(sent_str=="nb_best"){
        for (i = 0; i < tweets.length; i++) {
            if(tweets[i].nb_best_sentiment.polarity_neg==0 && tweets[i].nb_best_sentiment.polarity_pos ==0){
                
            
            }
            else{
            data.push({
                key: tweets[i].content_title,
                values: [{
                    x: tweets[i].nb_best_sentiment.polarity_neg,
                    y: tweets[i].nb_best_sentiment.polarity_pos,
                    size: Math.round(Math.random() * 100) / 100,
                    shape: shapes[i % shapes.length]
                    }]
            });
            }
        }
        }
        
        if(sent_str=="nb_bigram_best"){
        for (i = 0; i < tweets.length; i++) {
            if(tweets[i].nb_bigram_best_sentiment.polarity_neg==0 && tweets[i].nb_bigram_best_sentiment.polarity_pos ==0){
                
            
            }
            else{
            data.push({
                key: tweets[i].content_title,
                values: [{
                    x: tweets[i].nb_bigram_best_sentiment.polarity_neg,
                    y: tweets[i].nb_bigram_best_sentiment.polarity_pos,
                    size: Math.round(Math.random() * 100) / 100,
                    shape: shapes[i % shapes.length]
                    }]
            });
            }
        }
        }

        return data;
    }

