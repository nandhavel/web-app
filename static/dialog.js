//function CustomAlert(){
//    this.render = function(dialog){
//        var winW = window.innerWidth;
//        var winH = window.innerHeight;
//        var dialogoverlay = document.getElementById('dialogoverlay');
//        var dialogbox = document.getElementById('dialogbox');
//        dialogoverlay.style.display = "block";
//        dialogoverlay.style.height = winH+"px";
//        dialogbox.style.left = (winW/2) - (550 * .5)+"px";
//        dialogbox.style.top = "100px";
//        dialogbox.style.display = "block";
//        document.getElementById('dialogboxhead').innerHTML = "WARNING!!!";
//        document.getElementById('dialogboxbody').innerHTML = dialog;
//        document.getElementById('dialogboxfoot').innerHTML = '<button onclick="Alert.ok()">OK</button> <button onclick="Alert.revoke()">Revoke</button>';
//
//    }
//	this.ok = function(){
//		document.getElementById('dialogbox').style.display = "none";
//		document.getElementById('dialogoverlay').style.display = "none";
//	}
//	this.revoke = function(){
//	    document.getElementById('dialogbox').style.display = "none";
//		document.getElementById('dialogoverlay').style.display = "none";
//	    var xhttp = new XMLHttpRequest();
//	    xhttp.onreadystatechange = function(){
//	        if(xhttp.readystate == 4 && xhttp.status == 200){
//	            document.getElementById('dialogbox').style.display = xhttp.responseText;
//
//	        }
//	        else{
//	            if(xhttp.status == 404){
//	                console.log('file not found');
//
//
//	            }
//	        }
//	    };
//	    xhttp.open('GET','http://localhost:8080/revoke','true');
//	    xhttp.send();
//
//
//	}
//}
//var Alert = new CustomAlert();


function load_session(){

    var xml_request = new XMLHttpRequest();
    var main_div = document.getElementById("display_session");
    xml_request.onreadystatechange = function(){
	        if(this.readyState == 4 && this.status == 200){
	            var js_object  = JSON.parse(this.responseText);
	            console.log(js_object);
	            var str = '';
	            for(var i=0;i<js_object.length; i++){
	            str = '';
	            var my_div = document.createElement("div");
	            str +=
                   ("browser_name:"+" " + js_object[i].browser + "<br>"+
                    "ip_address: " + " " + js_object[i].ip_address + "<br>"+
                    "sign_in_time: " + " " + js_object[i].sign_in_time + "<br>");
                    console.log(str);


               	    my_div.innerHTML = str+"<br>";


               	    var form = document.createElement("form");
                    form.setAttribute('method',"post");
                    form.setAttribute('action',"/revoke");

                    //create input element
                    var inp = document.createElement("input");
                    inp.setAttribute("type", "hidden");
                    inp.name = "session_id";
                    inp.value = js_object[i].id;

                    //create a button
                    var s = document.createElement("input");
                    s.type = "submit";
                    s.value = "revoke";

                    form.appendChild(inp);
                    form.appendChild(s);

               	    my_div.style.margin = "0";

               	    my_div.appendChild(form);
                    main_div.appendChild(my_div);

               	    }

            }
	        else{
	            if(this.status == 404){
	                console.log('file not found');


	            }
	        }
	    };
	    xml_request.open('GET','/active_session','true');
	    xml_request.send();

}


function createButton() {
var btn = document.createElement("BUTTON");
                    var t = document.createTextNode("REVOKE");
                    btn.appendChild(t);
                    return btn;
}