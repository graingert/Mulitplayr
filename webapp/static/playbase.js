(function( $ ) {
	if ($.game == null)
		$.game = {};

	$.game.last_sequence_number = -1;
	$.game.actions = [];
	
	$.game.refresh_state = function(event){
		$.get("", {action:"state"},
		function(data){
			$(".current-player").text(data["current_player"]);
			if (data["last_sequence_number"] > $.game.last_sequence_number){
				$.game.refresh_actions();
				$.game.last_sequence_number = data["last_sequence_number"];
			}
			$(document).trigger("game.new-state", data);
		}, "json");
	}

	$.game.refresh_actions = function(){
		$.get("", {action:"actions",since:$.game.last_sequence_number},
		function(data){
			$.game.actions = $.game.actions.concat(data["actions"]);
			var actions = data["actions"]
			for(i in actions)
				$(document).trigger("game.action-made", actions[i]);
		}, "json");
	}

	$.game.process_action = function(action){
		$.game.last_sequence_number = action["sequence_number"];
		$(document).trigger("game.action-made", action);
	}

	$(document).ready(function(){
		$(document).on("game.refresh-state", $.game.refresh_state);
		$(document).trigger("game.refresh-state");
	})
})( jQuery );
