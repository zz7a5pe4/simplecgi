$(document).ready(function(){
	var fieldsetCount = $('#paramForm').children().length;
	var autoload = 0;
	var jsonObj = "";

	initConfigurationPage();
	stop(); //init the iframe

	$("#FLAT_INTERFACE").change(function(){
		var flat_interface = $("#FLAT_INTERFACE").val();
		if(flat_interface != "" || flat_interface != null){
			
			jQuery.ajax({
				type: "get",
				url: "http://127.0.0.1:8000/ip_query?i="+flat_interface,
				dataType: "text",
				
				success: function(data, dataStatus){
					var obj = JSON.parse(data);
					$("#FLOATING_RANGE").val(obj.brdcast+"\/25");
				},
				complete: function(XMLHttpRequest, textStatus){
					//do something
				},
				error: function(){
					alert("Connection Error!");
		   			return;
				}
			});
		}
	});
	
	$("#submitBtn").click(function(){
		
		validateSteps();
		
		//if there are errors don't allow the user to submit
		if($('#paramForm').data('errors')){
	        alert('Please correct the errors in the Form');
	        return false;
        }
		else {
			$("#wrapper").hide();
			$("iframe").show();
			postTheX7Configuration();
			refresh();
		}
	});
	
	/*
	 * post the x7 configuration to the backend
	 */
	function postTheX7Configuration(){
		var x7selected = $(":radio[name='Select_x7']:checked").val();
		
		var flat_interface = $("#FLAT_INTERFACE").val();
		var fixed_range = $("#FIXED_RANGE").val();
		var fixed_network_size = $("#FIXED_NETWORK_SIZE").val();
		var floating_range = $("#FLOATING_RANGE").val();
		
		var mysql_password = $("#MYSQL_PASSWORD").val();
		var rabbit_password = $("#RABBIT_PASSWORD").val();
		var service_password = $("#SERVICE_PASSWORD").val();
		var admin_password = $("#ADMIN_PASSWORD").val();
		
		var ssd_path = $("#SSD_PATH").val();
		var volumn_selected = $(":radio[name='VOLUMN_SELECTED']:checked").val();
		var volumn_selected_result;
		if(volumn_selected == "File"){
			volumn_selected_result = $("#FILE_SIZE").val();
		}
		else if(volumn_selected == "Device"){
			volumn_selected_result = $("#DEVICE_PATH").val();
		}
		
		jsonObj = {"Select_x7":x7selected, "FLAT_INTERFACE":flat_interface, "FIXED_RANGE":fixed_range, "FIXED_NETWORK_SIZE":fixed_network_size,
				"MYSQL_PASSWORD":mysql_password,"RABBIT_PASSWORD":rabbit_password,"SERVICE_PASSWORD":service_password,"ADMIN_PASSWORD":admin_password,
				"SSD_PATH":ssd_path, "VOLUMN_SELECTED":volumn_selected, "VOLUMN_SELECTED_RESULT":volumn_selected_result, "FLOATING_RANGE":floating_range};
		
		// jQuery.ajax({
		// 	type: "post",
		// 	url: "http://127.0.0.1:8000/x7",
		// 	dataType: "json",
		// 	data: jsonObj,
			
		// 	success: function(data, dataStatus){
		// 		//something
		// 		//refresh();
		// 	},
		// 	complete: function(XMLHttpRequest, textStatus){
		// 		//HideLoading();
	 //   		},
	 //   		error: function(){
	 //   			//alert("Connection Error!");
	 //   			//return;
	 //   		}
		// });
	}
	
	/*
	 * get x7 install callback information
	 */
	function refresh() {
		document.getElementById('submitBtn').style.visibility='hidden';
		post_to_url("http://127.0.0.1:8000/ping", jsonObj);
		autoload = window.setInterval('autoscroll()', 100);
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
	
	/*
	 * init the configuration for the radios.
	 */
	function initConfigurationPage(){
		var volumnPara = null;
		
		$("[name='Select_x7']").click(function(){
			$("textarea").hide();
			$(".textarea_name").hide();
			
			if($("[name='Select_x7']:checked")[0].checked){
				$(this).nextAll("textarea").show();
				$(this).nextAll("textarea").prev(".textarea_name").show();
			}
		});
		
		$(":radio[name='VOLUMN_SELECTED']").click(function(){
			$(".hidden-1").hide();
			$(".hidden-2").hide();
			$("input.hidden-1").val("");
			$("input.hidden-2").val("");
			
			if($(":radio[name='VOLUMN_SELECTED']:checked")[0].checked){
				volumnPara = $(this).val();
				if(volumnPara == "File"){
					$(this).nextAll(".hidden-1").css("display","inline-block").show();
				}
				else if(volumnPara == "Device"){
					$(this).nextAll(".hidden-2").css("display","inline-block").show();
				}
			}
		});
	}
	
	/*
    validates errors on all the fieldsets records if the Form has errors in $('#paramForm').data()
    */
    function validateSteps(){
        var FormErrors = false;
        for(var i = 1; i < fieldsetCount; ++i){
            var error = validateStep(i);
            if(error == -1){
            	FormErrors = true;
            }
        }
        $('#paramForm').data('errors',FormErrors);
    }
    
    /*
    validates one fieldset and returns -1 if errors found, or 1 if not
    */
    function validateStep(step){
    	if(step == fieldsetCount) return;
        
        var error = 1;
        var hasError = false;
        var radioChecked = 0;
        $('#paramForm').children(':nth-child('+ parseInt(step) +')').find(':input:not(button):visible').each(function(){
            var $this = $(this);
            var valueLength = jQuery.trim($this.val()).length;
            
            if($this.is(":radio")){
            	if(!$this[0].checked){
            		radioChecked = radioChecked + 1;
            	}
            	
            	if(radioChecked == 2){
            		valueLength = '';
            	}
            }
            
            if(valueLength == ''){
                hasError = true;
                $this.css('background-color','#FFEDEF');
            }
            else{
            	$this.css('background-color','#FFFFFF');
            }
        });
        var $link = $('#navigation li:nth-child(' + parseInt(step) + ') a');
        $link.parent().find('.error,.checked').remove();
        
        var valclass = 'checked';
        if(hasError){
	        error = -1;
	        valclass = 'error';
        }
        $('<span class="'+valclass+'"></span>').insertAfter($link);
        return error;
    }
	
});