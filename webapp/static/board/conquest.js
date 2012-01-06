if ($.templates == null)
	$.templates = {};

$.game.suspend_update = true;

function Region(id, region_svg){
	this.id = id;
	this.region_svg = region_svg;
	this.units = 0;
	this.placed_units = 0;
	this.owner = -1;

	this.modify_units = function(delta){
		this.units += delta;
		this.update_dom();
	}

	this.place_units = function(delta){
		this.placed_units += delta;
		this.update_dom();
	}

	this.set_data = function(units, placed_units, owner){
		this.units = units;
		this.placed_units = placed_units;
		this.owner = owner;
		this.update_dom();
	}

	this.update_dom = function(delta){
		var total_units = this.units + this.placed_units;
		var unit_text = ""
		if (this.units > 0){
			unit_text += this.units;
		}
		if (this.placed_units > 0){
			unit_text += "+" + this.placed_units;
		}
		$(this.region_svg).attr("data-units", total_units);
		$(this.region_svg).attr("data-owner", this.owner);
		$(this.region_svg).find("text").text(unit_text);
	}
}

var conquest = {
	regions: {},
	get_placements: function(){
		var placements = [];
		for (i in conquest.regions){
			var region = conquest.regions[i];
			if (region.placed_units > 0){
				placements.push({
					id: region.id,
					units: region.placed_units
				});
			}
		}
		return placements;
	}
}

function place_action(event){
	event.preventDefault();
	$.game.run_action({
		action:"place",
		placements:conquest.get_placements(),
	});
}

function reinforce_action(event){
	event.preventDefault();
	$.game.run_action({
		action:"reinforce",
		placements:conquest.get_placements(),
	});
}

function update_from_state(event, state){
	$.each(state.territories, function(index, region){
		conquest.regions[region.id].set_data(region.units, 0, region.owner);
	})
}

function prepmap() {
	$('#map g.region').click(function() {
		$.game.trigger("region-select", $(this))
	});

	$('#map g.region').each(function(index, region){
		conquest.regions[region.id] = new Region(region.id, region);
	});
	$.game.suspend_update = false;
	$.game.trigger("refresh");
};

$(document).ready(function() {
	$('#map').load('/static/board/map.svg', prepmap);
	
	$.game.on("region-select", function(event, region){
		conquest.regions[$(region).attr('id')].place_units(1);
	})

	$('#place').click(place_action)
	$('#reinforce').click(reinforce_action)
	
	$.game.on("new-state", update_from_state);
});
