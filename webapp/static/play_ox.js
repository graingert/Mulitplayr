if ($.templates == null)
	$.templates = {};

function place_marker(event){
	event.preventDefault();
	var target = $(event.target);
	var position = target.attr("position");
	$.game.run_action({
		action:"place",
		position:position,
	});
}

function update_from_state(event, state){
	$(".ox-grid .cell").each(function(index){
		var position = $(this).attr("position");
		var val = state.grid[position];
		var text = ""
		switch(val){
			case -1:
			text = "_"
			break;
			case 0:
			text = "O"
			break;
			case 1:
			text = "X"
			break;
		}
		$(this).text(text);
	});
}

function process_action(event, action){
	var template = $.templates.guess_result;
	if(action["new_state"]!=null)
		template = $.templates.guess_win_result;
	var r_message = $(template(action));
	$("#results").prepend(r_message);
	r_message.hide().slideDown(400);
}

$(document).ready(function(){
	// Load templates
	$.templates.guess_result = Handlebars.compile($("#guess-template").html());
	$.templates.guess_win_result = Handlebars.compile($("#win-template").html());

	// Bind events
	$(".ox-grid .cell").click(place_marker);
	$.game.on("new-state", update_from_state);
	$.game.on("guess-action", process_action);
})
