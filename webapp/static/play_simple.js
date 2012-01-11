if ($.templates == null)
	$.templates = {};

function make_guess(event){
	event.preventDefault();
	var guess_val = $("#guess_input").val();
	$.game.run_action({
		action:"guess",
		guess:guess_val,
	});
	$("#guess_input").val("");
}

function update_from_state(event, state){
	$("#last-guess").text(state["current_number"]);
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
	$("#make_guess").click(make_guess);
	$.game.on("new-state", update_from_state);
	$.game.on("guess-action", process_action);
})
