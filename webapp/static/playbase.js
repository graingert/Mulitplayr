(function( $ ) {
	if ($.game == null)
		$.game = {};

	$.game.last_sequence_number = -1;
	$.game.state = null;
	$.game.actions = [];
	
	$.game.refresh = function(event){
		var request = {
			action:"update",
			from:$.game.last_sequence_number
		}
		$.get("",request,$.game.process_update,"json");
	}

	$.game.process_update = function(data){
		var error = data["error"];
		if (error != null){
			$.error(error);
			return
		}

		var state = data["state"];
		var actions = data["actions"];

		$.game.actions = $.game.actions.concat(actions);
		for(i in actions)
			$(document).trigger("game.action-made", actions[i]);

		$.game.state = state;
		$(document).trigger("game.new-state", state);
	}

	$.game.run_action = function(request){
		request["last_sequence_number"] = $.game.last_sequence_number;
		$.post("",request,$.game.process_update,"json");
	}

	$(document).ready(function(){
		$(document).on("game.refresh", $.game.refresh);
		$(document).trigger("game.refresh");
	})
})( jQuery );
