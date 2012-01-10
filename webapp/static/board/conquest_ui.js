function fix_modal_margin(modal){
	modal.css('margin-top',-modal.height()/2);
}

function ConquestUi(conquest){
	var that = this;
	this.conquest = conquest;
	this.waiting_animation_queue = [];
	this.blocking_animation_count = 0;

	this.animation_started = function() {
		this.blocking_animation_count++;
	}

	this.queue_post_animation = function(closure) {
		this.waiting_animation_queue.push(closure);
	}

	this.animation_finished = function() {
		this.blocking_animation_count--;
		if (this.blocking_animation_running()) { return; }
		for (var i in this.waiting_animation_queue) {
			this.waiting_animation_queue[i]();
		}
		this.waiting_animation_queue = []
	}

	this.blocking_animation_running = function() {
		return this.blocking_animation_count > 0;
	}

	this.place_unit = function(event, region){
	if (!$.game.is_my_turn()) { return; }
		if ($.game.state.state == 'place' || $.game.state.state == 'reinforce'){
			get_region_obj(region).place_units(1);
		}
	}

	this.subtract_unit = function(event, region){
		if (!$.game.is_my_turn()) { return; }
		if ($.game.state.state == 'place' || $.game.state.state == 'reinforce'){
			get_region_obj(region).place_units(-1);
		}
	}

	this.select_region = function(event, region){
		if (!$.game.is_my_turn()) { return; }
		if ($.game.state.state == 'attack' ||
			$.game.state.state == 'fortify'){
			region_obj = get_region_obj(region);
			conquest.select_region(region_obj);
		}
	}

	this.select_origin = function(region){
		var max_move = region.units - 1;
		if ($.game.state.state == 'attack')
			max_move = Math.min(max_move, 3)
		$('#controls-place .move-max').text(max_move);
		var slider = $('#controls-place .move-unit-slider');
		slider.slider('option','max',max_move);
		slider.slider('value',max_move);
		$('#controls-place .move-unit-text').text(max_move);
	}

	this.animate_attack_action_complete = function(event, action) {
		$.dice.stop(action.attack_rolls, action.defend_rolls);
		that.animation_finished();
	}

	this.animate_attack_action = function(event, action) {
		setTimeout(function () {
			that.animate_attack_action_complete(event, action);
		}, 1000);
		that.animation_started();
		$('#dice-holder').show();
		$.dice.animate(action.attack_rolls.length, action.defend_rolls.length);
	}

	$.game.on("region-select", this.place_unit)
	$.game.on("region-select", this.select_region)
	$.game.on("region-right-click", this.subtract_unit)

	$('#map').load('/static/board/map.svg', prepmap);
	$('#place').click(conquest.place_action)
	$('#reinforce').click(conquest.reinforce_action)
	$('#attack').click(function(){
		var units = $(this).siblings('.move-unit-slider').slider('value')
		conquest.attack_action(units)
	})
	$('#end-attack').click(conquest.end_phase_action)
	$('#fortify').click(function(event){
		var units = $(this).siblings('.move-unit-slider').slider('value')
		conquest.move_action(units)
	})
	$('#skip-fortify').click(conquest.end_phase_action)

	$(".move-unit-slider").slider({range: "min", min:1, max:3, slide:function(event,ui){
		$(this).siblings(".move-unit-text").text(ui.value);
	}});

	this.attack_victory_modal = $('#attack-victory-modal').modal({backdrop:'static'});
	fix_modal_margin(this.attack_victory_modal);
	this.attack_victory_modal.find('.primary').click(function(){
		that.attack_victory_modal.modal('hide');
		var attack_units = that.attack_victory_modal.find('.move-unit-slider').slider('value')
		conquest.attack_victory_action(attack_units);
	});
	unit_text = this.attack_victory_modal.find(".move-unit-text")
	this.attack_victory_modal.find(".move-unit-slider").bind("slide", function(event, ui){
		unit_text.text(ui.value);
	});
}
