	if ($.templates == null)
		$.templates = {};

	function update_from_state(event, state){
		$("#last-guess").text(state["current_number"]);
	}

	function process_action(event, action){
		var template = $.templates.guess_result;
		if(action["new_state"]!=null)
			template = $.templates.guess_win_result;
		var r_message = $(template(action));
		$("#results").prepend(r_message);
		r_message.hide().slideDown(400);
	}

	function increase_units(region, units){
		region.data("units", region.data("units") + units)
		region.find("text").text(region.data("units"))
	}

	function decrease_units(region, units){
		region.data("units", region.data("units") - units)
		region.find("text").text(region.data("units"))
	}

	function place_units(event){
		event.preventDefault();
		$("#map g.region").each(function(index, region){
			var id = $(region).attr('id')
			var units = $(region).data('units')
			console.log(id)
			console.log(units)
		});
		alert("place")
	}
	
	function prepmap() {
		$('#map g.region').click(function() {
			$.game.trigger("region-select", $(this))
		});

		$('#map g.region').data("units", 0);
		$('#map g.region').each(attach_incr)

	};
	
	$(document).ready(function() {
		$('#map').load('/static/board/map.svg', prepmap);
		
		$.game.on("region-select", function(event, region){
			increase_units($(region), 1)
		})

		$('#place').click(place_units)
	});
