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
	origin: null,
	destination: null,
	ui: {}
}

conquest.get_placements = function(){
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

conquest.select_region = function(region){
	// Cannot just add a class due to bug with SVG dom in JQuery
	console.log(region)
	if (this.origin == region) {
		$(region.region_svg).attr('origin','');
		this.origin = null;
		if (this.destination) {
			$(this.destination.region_svg).attr('destination','');
			this.destination = null;
		}
		$("#map").removeClass('has-selected');
	}
	else if (this.destination == region) {
		$(region.region_svg).attr('destination','');
		this.destination = null;
	}
	else if (!this.origin) {
		$(region.region_svg).attr('origin','true');
		this.origin = region;
		$("#map").addClass('has-selected');
	}
	else if (!this.destination) {
		$(region.region_svg).attr('destination','true');
		this.destination = region;
	}
}

conquest.place_action = function(event){
	event.preventDefault();
	$.game.run_action({
		action:"place",
		placements:this.get_placements(),
	});
}

conquest.reinforce_action = function(event){
	event.preventDefault();
	$.game.run_action({
		action:"reinforce",
		placements:this.get_placements(),
	});
}

conquest.update_from_state = function(event, state){
	$.each(state.territories, function(index, region){
		conquest.regions[region.id].set_data(region.units, 0, region.owner);
	})
}

function get_region_obj(region_dom){
	return conquest.regions[$(region_dom).attr('id')];
}

conquest.ui.place_unit = function(event, region){
	if ($.game.state.state == 'place' ||
		$.game.state.state == 'reinforce'){
		get_region_obj(region).place_units(1);
	}
}

conquest.ui.select_region = function(event, region){
	if ($.game.state.state == 'attack' ||
		$.game.state.state == 'move'){
		region_obj = get_region_obj(region);
		conquest.select_region(region_obj);
	}
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

$(function() {
	$('#map').load('/static/board/map.svg', prepmap);
	
	$.game.on("region-select", conquest.ui.place_unit)
	$.game.on("region-select", conquest.ui.select_region)
	$('#place').click(conquest.place_action)
	$('#reinforce').click(conquest.reinforce_action)
	
	$.game.on("new-state", conquest.update_from_state);
});
