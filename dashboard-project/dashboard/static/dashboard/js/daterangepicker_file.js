/*jshint*/
/*global moment, console, drawAllGraphs, GLOBAL */

var applyDatePickerStats=function(){
    function cb(start, end, label) {
       $('.daterange span').html(start.format('MMM, YYYY') + ' - ' + end.format('MMM, YYYY'));
       GLOBAL.startDateRange = start.clone().toDate();
       GLOBAL.endDateRange = end.clone().toDate();
       console.log("New date range selected: " + start.format('YYYY-MM-DD') + " to " + end.format('YYYY-MM-DD') + " (predefined range: " + label + ")");
    }
    
    cb(moment([1990, 0, 1]).startOf("year"), moment());
    
	$('.daterange').daterangepicker({
	    showDropdowns: true,
	    showWeekNumbers: true,
	    autoApply: true,
	    autoUpdateInput: true,
	    startDate: moment([1990, 0, 1]).startOf("year"),
	    endDate: moment().endOf("month"),
	    minDate: moment([1990, 0, 1]).startOf("year"),
	    maxDate: moment().endOf("month"),
	    dateLimit: {"year": 100},
	    opens: "left",
	    linkedCalendars: false,
	    ranges: {
           'Last 3 Months': [moment().subtract(3, 'months').startOf('month'), moment().endOf("month")],
           'Last 6 Months': [moment().subtract(6, 'months').startOf('month'), moment().endOf("month")],
           'This Year': [moment().startOf('year'), moment().endOf('year')],
           'Last 12 Months': [moment().subtract(12, 'months').startOf('month'), moment().endOf("month")],
           'Last 3 Years': [moment().subtract(3, 'years').startOf('year'), moment().endOf("month")],
           'Last 10 Years': [moment().subtract(10, 'years').startOf('year'), moment().endOf("month")],
        }
	}, cb);
	
	$('.daterange').on('apply.daterangepicker', function(ev, picker) {
        console.log("applied");
	  drawAllGraphs();
	});
};
