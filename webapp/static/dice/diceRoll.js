(function( $ ) {
	if ($.dice == null)
		$.dice = $({});

	var stopAttackRollID = 0;
	var stopDefenceRollID;
	
	var attackDice = new Array();
	var attackDiceBlur = new Array();
	var defenceDice = new Array();
	var defenceDiceBlur = new Array();
	
	//Preload images
	$.get("/static/dice/White1.svg", function(data){defenceDice[1] = $(data)},"html");
	$.get("/static/dice/White2.svg", function(data){defenceDice[2] = $(data)},"html");
	$.get("/static/dice/White3.svg", function(data){defenceDice[3] = $(data)},"html");
	$.get("/static/dice/White4.svg", function(data){defenceDice[4] = $(data)},"html");
	$.get("/static/dice/White5.svg", function(data){defenceDice[5] = $(data)},"html");
	$.get("/static/dice/White6.svg", function(data){defenceDice[6] = $(data)},"html");
	
	$.get("/static/dice/Red1.svg", function(data){attackDice[1] = $(data)},"html");
	$.get("/static/dice/Red2.svg", function(data){attackDice[2] = $(data)},"html");
	$.get("/static/dice/Red3.svg", function(data){attackDice[3] = $(data)},"html");
	$.get("/static/dice/Red4.svg", function(data){attackDice[4] = $(data)},"html");
	$.get("/static/dice/Red5.svg", function(data){attackDice[5] = $(data)},"html");
	$.get("/static/dice/Red6.svg", function(data){attackDice[6] = $(data)},"html");
	
	$.get("/static/dice/White1blur.svg", function(data){defenceDiceBlur[1] = $(data)},"html");
	$.get("/static/dice/White2blur.svg", function(data){defenceDiceBlur[2] = $(data)},"html");
	$.get("/static/dice/White3blur.svg", function(data){defenceDiceBlur[3] = $(data)},"html");
	$.get("/static/dice/White4blur.svg", function(data){defenceDiceBlur[4] = $(data)},"html");
	$.get("/static/dice/White5blur.svg", function(data){defenceDiceBlur[5] = $(data)},"html");
	$.get("/static/dice/White6blur.svg", function(data){defenceDiceBlur[6] = $(data)},"html");
	
	$.get("/static/dice/Red1blur.svg", function(data){attackDiceBlur[1] = $(data)},"html");
	$.get("/static/dice/Red2blur.svg", function(data){attackDiceBlur[2] = $(data)},"html");
	$.get("/static/dice/Red3blur.svg", function(data){attackDiceBlur[3] = $(data)},"html");
	$.get("/static/dice/Red4blur.svg", function(data){attackDiceBlur[4] = $(data)},"html");
	$.get("/static/dice/Red5blur.svg", function(data){attackDiceBlur[5] = $(data)},"html");
	$.get("/static/dice/Red6blur.svg", function(data){attackDiceBlur[6] = $(data)},"html");
	
	
	$.dice.animate = function(noAttackDice, noDefenceDice){
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
	
	$.dice.stop = function(attack_rolls, defend_rolls){
		clearInterval(stopAttackRollID);
		clearInterval(stopDefenceRollID);
		stopAttackRollID = stopDefenceRollID = 0;

		function setDie(dieNo, idBase, dieArray, dieResult) {
			var dieId = idBase + (parseInt(dieNo) + 1);
			$(dieId).empty();
			$(dieId).append(dieArray[dieResult].clone());
			$(dieId).fadeTo(500, 1);
		}

		for (dieNo in attack_rolls) {
			setDie(dieNo, '#attackDie', attackDice, attack_rolls[dieNo]);
		}

		for (dieNo in defend_rolls) {
			setDie(dieNo, '#defenceDie', defenceDice, defend_rolls[dieNo]);
		}
	}
})( jQuery );
