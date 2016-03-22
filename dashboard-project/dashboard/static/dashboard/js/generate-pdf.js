/*jshint*/
/*global console, GLOBAL, jsPDF */

function dashboardToPDF() {
    var rowSizes = [], colSizes = [];

    for (var i=0; i<GLOBAL.widgets.length; i++) {
        var widget = GLOBAL.widgets[i],
            $vis = $("#" + widget.id),
            width = $vis.parent().width(),
            height = $vis.parent().height();
        console.log(widget);
        
        if (rowSizes[widget.row] === undefined) {
            rowSizes[widget.row] = 0;
        }
        rowSizes[widget.row] += width + 20;
        
        if (colSizes[widget.col] === undefined) {
            colSizes[widget.col] = 0;
        }
        colSizes[widget.col] += height + 20;
    }
    
    console.log(rowSizes);
    console.log(colSizes);
    
    var maxXSize = -1, maxYSize = -1;
    
    for (i=0; i<rowSizes.length; i++) {
        if (rowSizes[i] > maxXSize) {
            maxXSize = rowSizes[i];
        }
    }
    
    for (i=0; i<colSizes.length; i++) {
        if (colSizes[i] > maxYSize) {
            maxYSize = colSizes[i];
        }
    }
    
    console.log("MaxXSize = " + maxXSize);
    console.log("MaxYSize = " + maxYSize);
    
    var doc = new jsPDF("portrait", "pt", "a4");
    var image = new Image();

    // create an empty canvas element
    var canvas = document.createElement("canvas"),
        canvasContext = canvas.getContext("2d");

    // Called when image has finished loading.
    image.onload = function () {
        //Set canvas size is same as the picture
        canvas.width = image.width;
        canvas.height = image.height;
 
        // draw image into canvas element
        canvasContext.drawImage(image, 0, 0, image.naturalWidth, image.naturalHeight);
 
        // get canvas contents as a data URL (returns png format by default)
        var dataURL = canvas.toDataURL();
        
        // currHeight records how far down we are through this page.
        var currHeight = 0;
        
        // How wide the image will be in the PDF
        var newWidth = 500;
        doc.addImage(dataURL, 'PNG', 40, 20, newWidth, newWidth * (image.naturalHeight / image.naturalWidth));
        currHeight += 20 + newWidth * (image.naturalHeight / image.naturalWidth);
        
        currHeight += 50;
        doc.setFontSize(22);
        doc.text(150, currHeight, "Generated by Crichton Institute's");
        currHeight += 25;
        
        doc.text(140, currHeight, "Dumfries and Galloway Dashboard");
        currHeight += 30;
        
        doc.setFontSize(20);
        doc.text(180, currHeight, 'Created on ' + (new Date()).toDateString() + ".");
        currHeight += 30;
        
        doc.setFontSize(16);
        doc.addPage(maxXSize, maxYSize);
        
        var svgCount = 0;
        $("svg.chart").each(function(index, element) {
            var $element = $(element),
                widget = GLOBAL.widgets[index];
            svgCount++;
                
            function addImage(blob, image) {
                console.log(blob);
                doc.addImage(blob, 'PNG',
                            image.naturalWidth * widget.col / widget.sizeX + 20,
                            image.naturalHeight * widget.row / widget.sizeY + 20,
                            image.naturalWidth, image.naturalHeight, 
                            null, "NONE");
                
                if (--svgCount === 0) {
                    doc.save('Dumfries-Galloway Dashboard Export.pdf');
                }
            }
            
            element.toDataURL("image/png", {
                callback: function(data) {
                    var i = new Image(); 
                    i.onload = function() {
                        addImage(data, i);
                    };
                    i.src = data; 
                }
            });
        });
    };
    
    // Sets src and starts loading. image.onLoad will be called when image is loaded.
    image.src = $("#banner").attr('src');
}