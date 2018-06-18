function CustomAlert(){
    this.render = function(dialog){
        var winW = window.innerWidth;
        var winH = window.innerHeight;
        var dialogoverlay = document.getElementById('dialogoverlay');
        var dialogbox = document.getElementById('dialogbox');
        dialogoverlay.style.display = "block";
        dialogoverlay.style.height = winH+"px";
        dialogbox.style.left = (winW/2) - (550 * .5)+"px";
        dialogbox.style.top = "100px";
        dialogbox.style.display = "block";
        document.getElementById('dialogboxhead').innerHTML = "WARNING!!!";
        document.getElementById('dialogboxbody').innerHTML = dialog;
        document.getElementById('dialogboxfoot').innerHTML = '<button onclick="Alert.ok()">OK</button> <button onclick="Alert.revoke()">Revoke</button>';

    }
	this.ok = function(){
		document.getElementById('dialogbox').style.display = "none";
		document.getElementById('dialogoverlay').style.display = "none";
	}
	this.revoke = function(){
	    document.getElementById('dialogbox').style.display = "none";
		document.getElementById('dialogoverlay').style.display = "none";
	    var xhttp = new XMLHttpRequest();
	    xhttp.onreadystatechange = function(){
	        if(xhttp.readystate == 4 && xhttp.status == 200){
	            document.getElementById('dialogbox').style.display = xhttp.responseText;

	        }
	        else{
	            if(xhttp.status == 404){
	                console.log('file not found');


	            }
	        }
	    };
	    xhttp.open('GET','http://localhost:8080/revoke','true');
	    xhttp.send();


	}
}
var Alert = new CustomAlert();