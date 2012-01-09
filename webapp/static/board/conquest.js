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

	this.update_dom = function(delta){
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
	ui: {},
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
	// Cannot just add a class due to bug with SVG dom in JQuery
	if (this.origin == region) {
		$(region.region_svg).attr('origin','');
		this.origin = null;
		if (this.destination) {
			$(this.destination.region_svg).attr('destination','');
			this.destination = null;
		}
		$("#map").removeClass('has-selected');
		$('g.region').attr('valid-selection','false');
	}
	else if (this.destination == region) {
		$(region.region_svg).attr('destination','');
		this.destination = null;
	}
	else if (!this.origin) {
		$(region.region_svg).attr('origin','true');
		this.origin = region;
		$("#map").addClass('has-selected');
		$('g.region').attr('valid-selection','false');
		for(i in region.connected_regions){
			var connected = region.connected_regions[i];
			$(connected.region_svg).attr('valid-selection','true');
		}
	}
	else {
		if($(region.region_svg).attr('valid-selection') == 'true'){
			if(this.destination != null)
				$(this.destination.region_svg).attr('destination','false');
			$(region.region_svg).attr('destination','true');
			this.destination = region;
		}
	}
}

conquest.right_click_region= function(region){
	
}

conquest.clear_selected = function(){
	$("#map").removeClass('has-selected');
	$('g.region').attr('valid-selection','false')
		.attr('origin','false').attr('destination','false');
	conquest.origin = null;
	conquest.destination = null;
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

conquest.attack_action = function(units){
	event.preventDefault();
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
}

conquest.move_action = function(event){
	event.preventDefault();
	$.game.run_action({
		action:"move",
		origin:conquest.origin.id,
		destination:conquest.destination.id,
		units:1,
	});
	conquest.clear_selected();
}

conquest.end_phase_action = function(event){
	event.preventDefault();
	if ($.game.state.state == 'attack'){
		$.game.run_action({
			action:"end_attack",
		});
		conquest.clear_selected();
	}
	if ($.game.state.state == 'fortify'){
		$.game.run_action({
			action:"end_move",
		});
		conquest.clear_selected();
	}
}

conquest.update_from_state = function(event, state){
	$.each(state.territories, function(index, region){
		region_data = conquest.regions[region.id];
		region_data.set_data(region.units, 0, region.player);
		region_data.index = region.index
	})
	conquest.update_border_connections();
	conquest.placed_units = 0;
	conquest.update_dom();
	$('#map').attr('state', state.state);
	if (state.players[state.current_player_index].is_me) {
		$('#map').addClass('active');
		$('#controls-place').show();
		$('#controls-place').children().hide();
		$('#' + state.state + '-controls').show();
		$('#end_phase').show();
	} else {
		$('#map').removeClass('active');
		$('#controls-place').hide();
	}
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

conquest.ui.place_unit = function(event, region){
	if (!$.game.is_my_turn()) { return; }
	if ($.game.state.state == 'place' ||
		$.game.state.state == 'reinforce'){
		get_region_obj(region).place_units(1);
	}
}

conquest.ui.subtract_unit =  function(event, region){
	if (!$.game.is_my_turn()) { return; }
	if ($.game.state.state == 'place' || $.game.state.state == 'reinforce'){
		get_region_obj(region).place_units(-1);
	}
}

conquest.ui.select_region = function(event, region){
	if (!$.game.is_my_turn()) { return; }
	if ($.game.state.state == 'attack' ||
		$.game.state.state == 'fortify'){
		region_obj = get_region_obj(region);
		conquest.select_region(region_obj);
	}
}


conquest.ui.setup_modals = function(){
	$(".move-unit-slider").slider({range: "min", min:1, max:3, slide:function(event,ui){
		$(this).parent().find(".move-unit-text").text(ui.value);
	}});
	var that = this;
	this.attack_victory_modal = $('#attack-victory-modal').modal({backdrop:'static'});
	fix_modal_margin(this.attack_victory_modal);
	this.attack_victory_modal.find('.primary').click(function(){
		that.attack_victory_modal.modal('hide');
		conquest.attack_victory_action(that.attack_victory_modal.find('.move-unit-slider').slider('value'));
	});
}

function process_attack_action(event, action, latest, state){
	if (!latest) return;
	if (action.new_state != 'attack_victory') return;
	if (action.player_index == $.game.my_player_index){
		var can_move = conquest.regions[action.origin].units - 1 - action.loose_rolls;
		var dice_rolled = action.attack_rolls.length;
		var min_move = Math.min(dice_rolled, can_move);
		var slider = conquest.ui.attack_victory_modal.find('.move-unit-slider');
		slider.slider('option','min',min_move);
		slider.slider('option','max',can_move);
		slider.slider('option','value',min_move);
		slider.parent().find(".move-unit-text").text(min_move);
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

function fix_modal_margin(modal){
	modal.css('margin-top',-modal.height()/2);
}

$(function() {
	$('#map').load('/static/board/map.svg', prepmap);
	
	$.game.on("region-select", conquest.ui.place_unit)
	$.game.on("region-select", conquest.ui.select_region)
	$.game.on("region-right-click", conquest.ui.subtract_unit)
	$('#place').click(conquest.place_action)
	$('#reinforce').click(conquest.reinforce_action)
	$('#attack').click(function(){
		conquest.attack_action($('#attack-controls .move-unit-slider').slider("value"))
	})
	$('#end-attack').click(conquest.end_phase_action)
	$('#skip-fortify').click(conquest.end_phase_action)
	$('#move').click(conquest.move_action)
	
	$.game.on("new-state", conquest.update_from_state);
	$.game.on("attack-action", process_attack_action);
	conquest.ui.setup_modals();
});
