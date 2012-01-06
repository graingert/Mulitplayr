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
		update_region_text(region)
	}

	function decrease_units(region, units){
		region.data("units", region.data("units") - units)
		update_region_text(region)
	}
	
	function update_region_text(region){
		region.find("text").text(region.data("units"))
		region.attr("data-units", region.data("units"));
	}
	
	function set_teritory(region_id, units, owner){
		region = $('#' + region_id);
		
		region.data("units", units)
		region.attr("data-owner", owner)
		update_region_text(region)
	}

	function place_units(event){
		event.preventDefault();
		var placements = [];
		
		$("#map g.region").each(function(index, region){
			var country = {}

			country.id = $(region).attr('id')
			country.units = $(region).data('units')
			
			if (country.units > 0){
				placements.push(country)
			}
			
		});
		
		$.game.run_action({
			action:"place",
			placements:placements,
		});
		
	}
	
	function update_from_state(event, state){
		$.each(state.territories, function(index, region){
			set_teritory(region.id, region.units, region.owner)
		})
	}
	
	function prepmap() {
		$('#map g.region').click(function() {
			$.game.trigger("region-select", $(this))
		});

		$('#map g.region').data("units", 0);
	};
	
	$(document).ready(function() {
		$('#map').load('/static/board/map.svg', prepmap);
		
		$.game.on("region-select", function(event, region){
			increase_units($(region), 1)
		})

		$('#place').click(place_units)
		
		$.game.on("new-state", update_from_state);
	});
