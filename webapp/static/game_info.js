function joingame(event){
	$.post("./", {action:"join"},
	function(data){
		if (data.success)
			location.reload();
	}, "json");
	event.preventDefault();
}

function startgame(event){
	event.preventDefault();
	if ($(this).hasClass("disabled")) {
		return;
	}
	$.post("./", {action:"start"},
	function(data){
		if (data.success)
			location.reload();
	}, "json");
	event.preventDefault();
}

$(document).ready(function(){
	$("#joingame").click(joingame);
	$("#startgame").click(startgame);
})
