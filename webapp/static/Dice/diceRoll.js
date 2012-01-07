$(function() {
	var stopAttackRollID = 0;
	var stopDefenceRollID;
	
	var attackDice = new Array();
	var attackDiceBlur = new Array();
	var defenceDice = new Array();
	var defenceDiceBlur = new Array();
	
	//Preload images
	$.get("/static/Dice/White1.svg", function(data){attackDice[1] = $(data)},"html");
	$.get("/static/Dice/White2.svg", function(data){attackDice[2] = $(data)},"html");
	$.get("/static/Dice/White3.svg", function(data){attackDice[3] = $(data)},"html");
	$.get("/static/Dice/White4.svg", function(data){attackDice[4] = $(data)},"html");
	$.get("/static/Dice/White5.svg", function(data){attackDice[5] = $(data)},"html");
	$.get("/static/Dice/White6.svg", function(data){attackDice[6] = $(data)},"html");
	
	$.get("/static/Dice/Red1.svg", function(data){defenceDice[1] = $(data)},"html");
	$.get("/static/Dice/Red2.svg", function(data){defenceDice[2] = $(data)},"html");
	$.get("/static/Dice/Red3.svg", function(data){defenceDice[3] = $(data)},"html");
	$.get("/static/Dice/Red4.svg", function(data){defenceDice[4] = $(data)},"html");
	$.get("/static/Dice/Red5.svg", function(data){defenceDice[5] = $(data)},"html");
	$.get("/static/Dice/Red6.svg", function(data){defenceDice[6] = $(data)},"html");
	
	$.get("/static/Dice/White1blur.svg", function(data){attackDiceBlur[1] = $(data)},"html");
	$.get("/static/Dice/White2blur.svg", function(data){attackDiceBlur[2] = $(data)},"html");
	$.get("/static/Dice/White3blur.svg", function(data){attackDiceBlur[3] = $(data)},"html");
	$.get("/static/Dice/White4blur.svg", function(data){attackDiceBlur[4] = $(data)},"html");
	$.get("/static/Dice/White5blur.svg", function(data){attackDiceBlur[5] = $(data)},"html");
	$.get("/static/Dice/White6blur.svg", function(data){attackDiceBlur[6] = $(data)},"html");
	
	$.get("/static/Dice/Red1blur.svg", function(data){defenceDiceBlur[1] = $(data)},"html");
	$.get("/static/Dice/Red2blur.svg", function(data){defenceDiceBlur[2] = $(data)},"html");
	$.get("/static/Dice/Red3blur.svg", function(data){defenceDiceBlur[3] = $(data)},"html");
	$.get("/static/Dice/Red4blur.svg", function(data){defenceDiceBlur[4] = $(data)},"html");
	$.get("/static/Dice/Red5blur.svg", function(data){defenceDiceBlur[5] = $(data)},"html");
	$.get("/static/Dice/Red6blur.svg", function(data){defenceDiceBlur[6] = $(data)},"html");
	
	
	function animateDice(noAttackDice, noDefenceDice){
		//Don't reaminate if dice are already spinning
		if (stopAttackRollID != 0){return;}
		
		if (noAttackDice == 1){
			$("#attackDie1").fadeTo(500, 0.4);
			$("#attackDie2").fadeTo(500, 0);
			$("#attackDie3").fadeTo(500, 0);
			stopAttackRollID = setInterval(function() { rollAttackDice([$("#attackDie1")]); }, 250);
		}
		if (noAttackDice == 2){
			$("#attackDie1").fadeTo(500, 0.4);
			$("#attackDie2").fadeTo(500, 0.4);
			$("#attackDie3").fadeTo(500, 0);
			stopAttackRollID = setInterval(function() { rollAttackDice([$("#attackDie1"), $("#attackDie2")]); }, 250);
		}
		if (noAttackDice == 3){
			$("#attackDie1").fadeTo(500, 0.4);
			$("#attackDie2").fadeTo(500, 0.4);
			$("#attackDie3").fadeTo(500, 0.4);
			stopAttackRollID = setInterval(function() { rollAttackDice([$("#attackDie1"), $("#attackDie2"), $("#attackDie3")]); }, 250);
		}
		
		if (noDefenceDice == 1){
			$("#defenceDie1").fadeTo(500, 0.4);
			$("#defenceDie2").fadeTo(500, 0);
			stopDefenceRollID = setInterval(function() { rollDefenceDice([$("#defenceDie1")]); }, 250);
		}
		if (noDefenceDice == 2){
			$("#defenceDie1").fadeTo(500, 0.4);
			$("#defenceDie2").fadeTo(500, 0.4);
			stopDefenceRollID = setInterval(function() { rollDefenceDice([$("#defenceDie1"), $("#defenceDie2")]); }, 250);
		}
	}

	function rollAttackDice(diceArray){
		var i = 0;
		for (i=0;i<diceArray.length;i++){
			var randomNum = Math.ceil(Math.random()*6);
			diceArray[i].empty(); $(diceArray[i]).append(attackDiceBlur[randomNum].clone());
		}
	}
	function rollDefenceDice(diceArray){
		var i = 0;
		for (i=0;i<diceArray.length;i++){
			var randomNum = Math.ceil(Math.random()*6);
			diceArray[i].empty(); $(diceArray[i]).append(defenceDiceBlur[randomNum].clone());
		}
	}
	
	function animateDie(objDie){
		objDie.fadeTo(500, 0.4);
		stopRollID = setInterval(function() { rollDie(objDie); }, 100);
	}
	
	function rollDie(objDie){
		var randomNum = Math.ceil(Math.random()*6);
		objDie.attr("src", "/static/Dice/White" + randomNum + "blur.svg");
	}
	
	function stopDice(attack1, attack2, attack3, defence1, defence2){
		clearInterval(stopAttackRollID);
		clearInterval(stopDefenceRollID);
		

		$("#attackDie1").empty();$("#attackDie1").append(attackDice[attack1].clone());
		$("#attackDie2").empty();$("#attackDie2").append(attackDice[attack2].clone());
		$("#attackDie3").empty();$("#attackDie3").append(attackDice[attack3].clone());
				
		$("#defenceDie1").empty();$("#defenceDie1").append(defenceDice[defence1].clone());
		$("#defenceDie2").empty();$("#defenceDie2").append(defenceDice[defence2].clone());
		
		$("#attackDie1").fadeTo(500, 1);
		if (attack2 != 0) {$("#attackDie2").fadeTo(500, 1);}
		if (attack3 != 0) {$("#attackDie3").fadeTo(500, 1);}
		
		$("#defenceDie1").fadeTo(500, 1);
		if (defence2 != 0) {$("#defenceDie2").fadeTo(500, 1);}
	}
	
	$("#start").click(function() {
		animateDice(3,2);
		return false;
	})
	
	$( "#stop" ).click(function() {
		stopDice(2, 3, 4, 5, 6);
		return false;
	});
	
	$("#test").click(function() {
		$("#attackDie1").empty();$("#attackDie1").append(attackDice[1].clone);
		$("#attackDie2").empty();$("#attackDie2").append(attackDice[2].clone);
		$("#attackDie3").empty();$("#attackDie3").append(attackDice[3].clone);
		
		$("#defenceDie1").empty();$("#defenceDie1").append(defenceDice[4].clone);
		$("#defenceDie2").empty();$("#defenceDie2").append(defenceDice[5].clone);
	})
});