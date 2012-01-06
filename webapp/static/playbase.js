(function( $ ) {
	if ($.game == null)
		$.game = $({});

	$.game.last_sequence_number = -1;
	$.game.state = null;
	$.game.actions = [];

	$.game.refresh = function(event){
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
