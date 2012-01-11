function fix_modal_margin(modal){
	modal.css('margin-top',-modal.height()/2);
}

(function( $ ) {
	if ($.game == null)
		$.game = $({});

	$.game.last_sequence_number = -2; // -1 is server no state
	$.game.state = null;
	$.game.actions = [];
	$.game.suspend_update = false;
	$.game.my_player_index = -1;
	$.game.my_user_data = null;

	$.game.refresh = function(event){
		if ($.game.suspend_update)
			return;
		var request = {
			action:"update",
			from:$.game.last_sequence_number
		}
		$.get("./",request,$.game.process_update,"json");
	}

	$.game.process_update = function(data){
		$.game.trigger("update-received");
		var error = data["error"];
		if (error != null){
			$.error(error);
			return
		}

		var state = data["state"];
		var actions = data["actions"];

		for(i in state.players)
		{
			var player = state.players[i];
			if (player.is_me){
				$.game.my_player_index = i;
				$.game.my_user_data = state.players[i];
			}
		}
		if ($.game.state != null){
			for(i in actions){
				if (actions[i]['sequence_number'] > $.game.last_sequence_number) {
					var evt_name = actions[i]['action_type'] + "-action-animate";
					$.game.trigger(evt_name, [actions[i]]);
				}
			}
		}
		$.game.state = state;
		var seq_num = state['last_sequence_number'];
		if (seq_num > $.game.last_sequence_number){
			$.game.trigger("new-state", state);
		}
		$.game.actions = $.game.actions.concat(actions);
		for(i in actions){
			if (actions[i]['sequence_number'] > $.game.last_sequence_number) {
				var latest = actions[i]['sequence_number'] == seq_num;
				$.game.trigger("action-made", [actions[i],latest]);
				var evt_name = actions[i]['action_type'] + "-action";
				$.game.trigger(evt_name, [actions[i],latest]);
			}
		}
		$.game.last_sequence_number = state['last_sequence_number'];
	}

	$.game.run_action = function(request){
		request["last_sequence_number"] = $.game.last_sequence_number;
		$.ajax({
			type: "POST",
			data: JSON.stringify(request),
			contentType: "application/json; charset=utf-8",
			success: $.game.process_update,
			dataType: "json"
		});
	}

	$.game.is_my_turn = function(){
		return $.game.state.current_player_index == $.game.my_player_index;
	}

	$.game.check_finish = function(event, state){
		if (state.state == 'finished'){
			fix_modal_margin($('#finish-game-modal'));
			$('#finish-game-modal').modal('show');
			this.attack_victory_modal.find('.primary').click(function(){
				$('#finish-game-modal').modal('hide');
			})

		}
	}

	$(document).ready(function(){
		$.game.on("refresh", $.game.refresh);
		$.game.trigger("refresh");
		$.game.on("new-state", $.game.check_finish)
	})
})( jQuery );
