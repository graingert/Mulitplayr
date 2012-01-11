if ($.templates == null)
	$.templates = {};

$.game.suspend_update = true;

function Region(id, region_svg){
	this.id = id;
	this.region_svg = region_svg;
	this.units = 0;
	this.placed_units = 0;
	this.owner = -1;
	this.index = null;
	this.connected_regions = [];

	this.modify_units = function(delta){
		this.units += delta;
		this.update_dom();
		conquest.update_dom();
	}

	this.place_units = function(delta){
		if (this.owner != $.game.my_player_index)
			return;
		if ((conquest.placed_units + delta) > $.game.my_user_data.unit_pool)
			return;
		if ((conquest.placed_units + delta) < 0){
			return;
		}
		this.placed_units += delta;
		conquest.placed_units += delta;
		this.update_dom();
		conquest.update_dom();
	}

	this.set_data = function(units, placed_units, owner){
		this.units = units;
		this.placed_units = placed_units;
		this.owner = owner;
		this.update_dom();
	}

	this.update_dom = function(){
		var total_units = this.units + this.placed_units;
		var unit_text = ""
		if (this.units > 0){
			unit_text += this.units;
		}
		if (this.placed_units > 0){
			unit_text += "+" + this.placed_units;
		}
		this.update_token_size(unit_text);
		$(this.region_svg).attr("data-units", total_units);
		$(this.region_svg).attr("data-owner", this.owner);
		$(this.region_svg).find("text").text(unit_text);
		$(this.region_svg).attr("is-mine", $.game.my_player_index == this.owner);
	}
	
	this.update_token_size = function(unit_text){
		circles = $(this.region_svg).find("circle");
		var radius = 7 + (unit_text.length * 1.8);
		$(circles[0]).attr("r",radius);
	}
	
}

var conquest = {
	regions: {},
	origin: null,
	destination: null,
	placed_units: 0,
}

conquest.update_dom = function(){
	var unit_pool = $.game.my_user_data.unit_pool - this.placed_units;
	$('.unit-pool-count').text(unit_pool);
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

$.getJSON('/static/board/borders.json', function(data) {
	conquest.border_json = data;
});

conquest.select_region = function(region){
	if (region == this.origin){
		this.deselect_origin();
	}
	else if (region == this.destination){
		this.deselect_destination();
	}
	else if (this.is_valid_destination(region)){
		this.select_destination(region);
	}
	else if (this.is_valid_origin(region)){
		this.select_origin(region);
	}
}

conquest.is_valid_origin = function(region){
	return region.owner == $.game.my_player_index
		&& region.units > 1;
}

conquest.is_valid_destination = function(region){
	if (this.origin != null &&
			this.origin.connected_regions.indexOf(region) >= 0)
	{
		if ($.game.state.state == 'attack' && region.owner != $.game.my_player_index)
			return true;
		if ($.game.state.state == 'fortify' && region.owner == $.game.my_player_index)
			return true;
	}
	return false;
}

conquest.deselect_origin = function(){
	if (this.destination){
		this.deselect_destination();
	}
	if (this.origin){
		$(this.origin.region_svg).attr('origin',false);
		this.origin = null;
		this.destination = null;
		this.set_valid_selection(this.is_valid_origin);
		$("#map").removeClass('has-selected');
	}
	this.ui.deselect_origin();
}

conquest.deselect_destination = function(){
	$(this.destination.region_svg).attr('destination',false);
	this.destination = null;
	this.set_valid_selection(this.is_valid_destination);
	$(this.origin.region_svg).attr('valid-selection', true);

	this.ui.deselect_destination();
}

conquest.select_origin = function(region){
	if(this.origin) this.deselect_origin();
	this.origin = region;
	this.set_valid_selection(this.is_valid_destination);
	$(this.origin.region_svg).attr('valid-selection', true);
	$("#map").addClass('has-selected');
	$(this.origin.region_svg).attr('origin',true);
	for (var i in this.regions){
		var i_region = this.regions[i];
		$(i_region.region_svg).attr('valid-alt-origin',this.is_valid_origin(i_region));
	}
	$(this.origin.region_svg).attr('valid-alt-origin', false);

	this.ui.select_origin(region);
}

conquest.select_destination = function(region){
	if(this.destination) this.deselect_destination();
	this.destination = region;
	$(this.destination.region_svg).attr('destination',true);

	this.ui.select_destination(region);
}

conquest.set_valid_selection = function(validator){
	for (var i in this.regions){
		var region = this.regions[i];
		$(region.region_svg).attr('valid-selection',validator.call(this,region));
	}
}

conquest.place_action = function(){
	$.game.run_action({
		action:"place",
		placements:conquest.get_placements(),
	});
}

conquest.reinforce_action = function(){
	$.game.run_action({
		action:"reinforce",
		placements:conquest.get_placements(),
	});
}

conquest.attack_action = function(units){
	$.game.run_action({
		action:"attack",
		origin:conquest.origin.id,
		destination:conquest.destination.id,
		attackers:units,
	});
}

conquest.attack_victory_action = function(units){
	$.game.run_action({
		action:"attack_victory",
		units:units,
	});
	conquest.deselect_origin();
}

conquest.move_action = function(units){
	$.game.run_action({
		action:"move",
		origin:conquest.origin.id,
		destination:conquest.destination.id,
		units:units,
	});
	conquest.deselect_origin();
}

conquest.end_phase_action = function(){
	if ($.game.state.state == 'attack'){
		$.game.run_action({
			action:"end_attack",
		});
		conquest.deselect_origin();
	}
	if ($.game.state.state == 'fortify'){
		$.game.run_action({
			action:"end_move",
		});
		conquest.deselect_origin();
	}
}

conquest.update_from_state = function(event, state){
	if (conquest.ui.blocking_animation_running()) {
		conquest.ui.queue_post_animation(function() {
			conquest.update_from_state(event, state);
		});
		return;
	}
	$.each(state.territories, function(index, region){
		region_data = conquest.regions[region.id];
		region_data.set_data(region.units, 0, region.player);
		region_data.index = region.index
	})
	conquest.update_border_connections();
	conquest.placed_units = 0;
	conquest.update_dom();
	$('#map').attr('state', state.state);
	if (state.players[state.current_player_index].is_me && state.state != 'finished') {
		$('#map').addClass('active');
		$('#controls-place').show();
		$('#controls-place').children().hide();
		$('#' + state.state + '-controls').show();
		$('#end_phase').show();
	} else {
		$('#map').removeClass('active');
		$('#controls-place').hide();
	}
	$('#controls-place .unit-move').hide();
	// Try to re-select the origin and destination
	var old_origin = conquest.origin;
	var old_destination = conquest.destination;
	conquest.deselect_origin();
	conquest.select_region(old_origin);
	conquest.select_region(old_destination);
	if (conquest.origin == null)
		conquest.set_valid_selection(conquest.is_valid_origin);
}

conquest.update_border_connections = function(){
	if(conquest.border_json == null)
		return;
	index_mappings = {};
	for (i in conquest.regions){
		var region = conquest.regions[i];
		index_mappings[region.index] = region;
	}
	for (i in conquest.border_json){
		var border = conquest.border_json[i];
		for(j in border.borders){
			var border_to = border.borders[j];
			index_mappings[border.id].connected_regions.push(index_mappings[border_to]);
		}
	}
}

function get_region_obj(region_dom){
	return conquest.regions[$(region_dom).attr('id')];
}

function process_attack_action(event, action, latest, state){
	if (conquest.ui.blocking_animation_running()) {
		conquest.ui.queue_post_animation(function() {
			process_attack_action(event, action, latest, state);
		});
		return;
	}
	if (!latest) return;
	if (action.new_state != 'attack_victory') return;
	if (action.player_index == $.game.my_player_index){
		var can_move = conquest.regions[action.origin].units - 1 - action.loose_rolls;
		var dice_rolled = action.attack_rolls.length;
		var min_move = Math.min(dice_rolled, can_move);
		var slider = conquest.ui.attack_victory_modal.find('.move-unit-slider');
		slider.slider('option','min',min_move);
		slider.slider('option','max',can_move);
		slider.slider('option','value',can_move);
		slider.parent().find(".move-unit-text").text(can_move);
		conquest.ui.attack_victory_modal.find('.move-min').text(min_move);
		conquest.ui.attack_victory_modal.find('.move-max').text(can_move);
		conquest.ui.attack_victory_modal.modal('show');
	}
}

function prepmap() {
	$('#map g.region').click(function() {
		$.game.trigger("region-select", $(this))
	});
	//Assume that when the context menu is requested, the user has right clicked
	$("#map g.region").bind("contextmenu", function(e) {
		$.game.trigger("region-right-click", $(this));
		return false;
	});
	

	$('#map g.region').each(function(index, region){
		conquest.regions[region.id] = new Region(region.id, region);
	});
	$.game.suspend_update = false;
	$.game.trigger("refresh");
};

$(function() {
	conquest.ui = new ConquestUi(conquest);
	$.game.on("new-state", conquest.update_from_state);
	$.game.on("attack-action-animate", conquest.ui.animate_attack_action);
	$.game.on("attack-action", process_attack_action);
});
