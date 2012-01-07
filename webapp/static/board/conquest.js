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
		$(this.region_svg).attr("is-mine", $.game.my_player_index == this.owner);
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
		placements:conquest.get_placements(),
	});
}

conquest.reinforce_action = function(event){
	event.preventDefault();
	$.game.run_action({
		action:"reinforce",
		placements:conquest.get_placements(),
	});
}

conquest.attack_action = function(event){
	event.preventDefault();
	$.game.run_action({
		action:"attack",
		origin:conquest.origin.id,
		destination:conquest.destination.id,
		attackers:1,
	});
}

conquest.attack_victory_action = function(event){
	event.preventDefault();
	$.game.run_action({
		action:"attack_victory",
		units:1,
	});
}

conquest.move_action = function(event){
	event.preventDefault();
	$.game.run_action({
		action:"move",
		origin:conquest.origin.id,
		destination:conquest.destination.id,
		units:1,
	});
}

conquest.end_phase_action = function(event){
	event.preventDefault();
	if ($.game.state.state == 'attack'){
		$.game.run_action({
			action:"end_attack",
		});
	}
	if ($.game.state.state == 'fortify'){
		$.game.run_action({
			action:"end_move",
		});
	}
}

conquest.update_from_state = function(event, state){
	$.each(state.territories, function(index, region){
		conquest.regions[region.id].set_data(region.units, 0, region.player);
	});
	if (state.players[state.current_player_index].is_me) {
		$('#controls-place').show();
		$('#controls-place').children().hide();
		$('#' + state.state + '-controls').show();
		$('#end_phase').show();
	} else {
		$('#controls-place').hide();
	}
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
		$.game.state.state == 'fortify'){
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
	$('#attack').click(conquest.attack_action)
	$('#attack_victory').click(conquest.attack_victory_action)
	$('#end_phase').click(conquest.end_phase_action)
	$('#move').click(conquest.move_action)
	
	$.game.on("new-state", conquest.update_from_state);
});
