$(function(e) {
	'use strict';
	$('#example').DataTable();
	var table = $('#example1').DataTable();
	$(document).on('click', 'button', function(e) {
		var data = table.$('input, select').serialize();
		
		return false;
	});
	$('#example2').DataTable({
		"scrollY": "200px",
		"scrollCollapse": true,
		"paging": false
	});
	$('#example3').DataTable({
		responsive: {
			details: {
				display: $.fn.dataTable.Responsive.display.modal({
					header: function(row) {
						var data = row.data();
						return 'Details for ' + data[0] + ' ' + data[1];
					}
				}),
				renderer: $.fn.dataTable.Responsive.renderer.tableAll({
					tableClass: 'table'
				})
			}
		}
	});
});