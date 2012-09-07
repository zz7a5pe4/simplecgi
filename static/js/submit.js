$(document).ready(function(){
	
	stop();
	
	jQuery.ajax({
		type: "post",
		url: "http://127.0.0.1:8000/default",
		dataType: "text",
		
		success: function(data, textStatus){
			var msg = data;
			var first = msg.substring(msg.indexOf("<p>")+3,msg.indexOf("</p>"));
			var last = msg.substring(msg.indexOf("<b>")+3,msg.indexOf("</b>"));
			var maincontent = msg.substring(msg.indexOf("</p>")+4, msg.indexOf("<b>")-5);
			var msgobj = JSON.parse(maincontent);
			
			$("#HOST_IP").val(msgobj.HOST_IP);
			$("#MULTI_HOST").val(msgobj.MULTI_HOST);
//			$("#GLANCE_HOSTPORT").val(msgobj.HOST_IP);
//			$("#GLANCE_HOSTPORT").val("9292");
			$("#FLAT_INTERFACE").val(msgobj.FLAT_INTERFACE);
			$("#FIXED_RANGE").val(msgobj.FIXED_RANGE);
			$("#FIXED_NETWORK_SIZE").val(msgobj.FIXED_NETWORK_SIZE);
			$("#FLOATING_RANGE").val(msgobj.FLOATING_RANGE);
//			$("#MYSQL_HOST").val(msgobj.MYSQL_HOST);
//			$("#MYSQL_HOST").val("172.16.1.106");
			$("#MYSQL_PASSWORD").val(msgobj.MYSQL_PASSWORD);
			$("#SERVICE_TOKEN").val(msgobj.SERVICE_TOKEN);
			$("#RABBIT_PASSWORD").val(msgobj.RABBIT_PASSWORD);
			$("#SERVICE_PASSWORD").val(msgobj.SERVICE_PASSWORD);
			$("#ADMIN_PASSWORD").val(msgobj.ADMIN_PASSWORD);
			$("#ENABLED_SERVICES").val(msgobj.ENABLED_SERVICES);
		},
		complete: function(XMLHttpRequest, textStatus){
			//HideLoading();
   		},
   		error: function(){
   			alert("Connection Error!");
   			return;
   		}
	});
	
	$("#submitBtn").click(function(){
		//if there are errors don't allow the user to submit
		if($('#paramForm').data('errors')){
	        alert('Please correct the errors in the Form');
	        return false;
        }
		else {
			$("#wrapper").hide();
			$("iframe").show();
			refresh();
		}
	});
});

var autoload = 0
	
function refresh() {
	document.getElementById('submitBtn').style.visibility='hidden';
	post_to_url("http://127.0.0.1:8000/ping", {'q':'a'});
	autoload = window.setInterval('autoscroll()', 1000);
}

function post_to_url(path, params, method) {
	method = method || "post"; // Set method to post by default, if not specified.
	
	// The rest of this code assumes you are not using a library.
	// It can be made less wordy if you use one.
	var form = document.createElement("form");
	form.setAttribute("method", method);
	form.setAttribute("action", path);
	form.setAttribute("target", "resultframe");
	for(var key in params) {
		if(params.hasOwnProperty(key)) {
			var hiddenField = document.createElement("input");
			hiddenField.setAttribute("type", "hidden");
			hiddenField.setAttribute("name", key);
			hiddenField.setAttribute("value", params[key]);
			form.appendChild(hiddenField);
		}
	}
	
	document.body.appendChild(form);
	form.submit();
}

function autoscroll() {
	var pos_y =  document.getElementById("resultframe").contentWindow.document.body.scrollHeight + 10;
	document.getElementById("resultframe").contentWindow.scrollTo(0, pos_y );
}

function stop(){
	autoscroll();
	window.clearInterval(autoload);
	$("#resultframe").hide();
}