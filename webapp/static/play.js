function ViewController() {
	this.countTo = 5;
	this.count = 0;
	this.refreshActive = true;

	// Keep this in callbacks
	var self = this;

	$.game.on("new-state", function(event, state){
		if (state["state"] == "finished") {
			$('#refresh-timer').text("Game is finished");
			$('#refresh').css('display', 'none');
			self.refreshActive = false;
		}
	});

	$.game.on("update-received", function(event) {
		if (self.count == 0) {
			self.startRefreshTimer();
			self.count = self.countTo;
		}
	});
};
ViewController.prototype.startRefreshTimer = function() {
	var self = this;
	setTimeout(function() { self.refreshState(); }, 1000);
}
ViewController.prototype.stopRefreshTimer = function() {
	this.refreshActive = false;
}
ViewController.prototype.refreshState = function() {
		if (!this.refreshActive) {
			return;
		}
		if (this.count > 0) {
			this.count--;
		}
		// TODO: Make these use templates & CSS tricks
		if (this.count <= 0) {
			$('#refresh-timer').text("Refreshing");
			$.game.trigger("refresh");
		} else {
			$('#refresh-timer').text("Refresh in " + this.count);
			this.startRefreshTimer();
		}
}
viewControl = new ViewController();
$(document).ready(function(){
	$.templates.player_list =
		Handlebars.compile($("#player-list-template").html());

	$("#refresh").click(function(event){
		$.game.trigger("refresh");
		event.preventDefault();
	});

	$("#stop-refresh").click(function(event){
		viewControl.stopRefreshTimer();
		event.preventDefault();
	});
});

$.game.on("new-state", function(event, state){
	$(".current-player").text(state["current_player"]);
	$(".current-state").text(state["state"]);
	$("#player-list").html($($.templates.player_list(state)))
});
