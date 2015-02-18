function remove_item(event, id, type) {
   (event.preventDefault) ? event.preventDefault() : event.returnValue = false;
    var r=confirm("Do you really want to remove " + type + "?");
    if (r == true) {
			$.post("{{ request.get_full_path }}", {
				delete_request : 1,
				type: type,
				item_id : id,
				csrfmiddlewaretoken: getCookie('csrftoken')
			},
			function(data) {
				window.location.reload();
			});
	}
}

	
function refresh_captcha() {
	$.getJSON($(this).data('url'), {'refresh_captcha' : 1}, function(json) {
		$('img[class="captcha"]').attr('src', json['new_cptch_image'])
		$('#id_captcha_0').val(json['new_cptch_key'])
		$('#id_captcha_1').val('')
    });
};

function upload_image(event){
	// (event.preventDefault) ? event.preventDefault() : event.returnValue = false;
	
	$("#loading_info").removeClass('hidden')
	
	var images = $('#id_article_images').val()
	
	var formData = new FormData($('#image_form')[0]);

	$.ajax({
	        url: "{{ request.get_full_path }}",
	        type: 'POST',
	        success: function (data) {
	        	$("#loading_info").addClass('hidden')
	        	var obj = $.parseJSON(data);
	        	if (data != '') {
		        	$('#id_image').val('')
		        	$('#form_div').append("<div id='image_div_" + obj.id + "' style='margin-bottom:10px;'><img src='" + obj.url + "' width='40px'/>&nbsp;&nbsp;" + obj.name + "<a class='btn btn-mini' onclick=\"remove_image(event, " + obj.id + ")\"><i class='icon-minus'></i></a></div>");
					$('#id_article_images').val(images + ',' + obj.id)
	        	}
	        },
	        // Form data
	        data: formData,
	        //Options to tell jQuery not to process data or worry about content-type.
	        cache: false,
	        contentType: false,
	        processData: false
		    }).done(function(data) {
				$("#loading_info").addClass('hidden')
			}).fail(function(data) {
				$("#loading_info").addClass('hidden')
			})
	}


function remove_image(event, id) {
	(event.preventDefault) ? event.preventDefault() : event.returnValue = false;
	
	var images = $('#id_article_images').val()
	
	$.post("{{ request.get_full_path }}", {
				delete_request : 1,
				type: 'image',
				item_id : id,
				csrfmiddlewaretoken: getCookie('csrftoken')
			},
			function(data) {
				$('#image_div_' + id).remove();
				$('#id_article_images').val(images.replace(',' + id, ''))
			});
}
