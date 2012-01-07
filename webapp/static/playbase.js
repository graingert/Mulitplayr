(function( $ ) {
	if ($.game == null)
		$.game = $({});

	$.game.last_sequence_number = -2; // -1 is server no state
	$.game.state = null;
	$.game.actions = [];
	$.game.suspend_update = false;
	$.game.my_player_index = -1;

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
			}
		}

		$.game.actions = $.game.actions.concat(actions);
		for(i in actions){
			if (actions[i]['sequence_number'] > $.game.last_sequence_number) {
				$.game.trigger("action-made", actions[i]);
				var evt_name = actions[i]['type'] + "-action";
				$.game.trigger(evt_name, actions[i]);
			}
		}

		$.game.state = state;
		var seq_num = state['last_sequence_number'];
		if (seq_num > $.game.last_sequence_number){
			$.game.last_sequence_number = state['last_sequence_number'];
			$.game.trigger("new-state", state);
		}
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

	$(document).ready(function(){
		$.game.on("refresh", $.game.refresh);
		$.game.trigger("refresh");
	})
})( jQuery );
