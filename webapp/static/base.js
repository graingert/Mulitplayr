if ($.templates == null)
	$.templates = {};

$(document).ready(function(event) {
	$.templates.active_games_dropdown =
		Handlebars.compile($('#active-games-dropdown-template').html());
	$.getJSON('/game/active', function(data) {
		var awaiting = 0;
		for(i in data.games) {
			awaiting += (data.games[i].awaitingPlayerMove ? 1 : 0);
		}
		$('#active-games-await').text(awaiting);
		$('#active-games-dropdown').html($.templates.active_games_dropdown(data));
	});
});
