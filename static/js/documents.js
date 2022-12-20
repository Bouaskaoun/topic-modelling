$(document).ready(function() { 
    $('#upload-form').validate({
        rules:{
            fileupload:"required",
            name:{
                required:true,
                minlength:4,
            },
            column:{
                required:true,
                chk:true,
            },
        }
    });
    $.validator.addMethod('chk', function (value) { 
        return values.includes(value);
    }, 'Please enter a valid column name');
});


function readURL(input) {
    if (input.files && input.files[0]) {

        var reader = new FileReader();
        
        reader.onload = function (e) {
            $('.image-upload-wrap').hide();

            $('.file-upload-content').show();

            $('.image-title').html(input.files[0].name);

            $('#upload-btn').html('Change '+input.files[0].name)
        };

        reader.readAsDataURL(input.files[0]);

    } else {
        removeUpload();
    }
}

function removeUpload() {
    $('.file-upload-input').replaceWith($('.file-upload-input').clone());
    $('.file-upload-content').hide();
    $('.row.mt-2.p-0').hide();
    $('#upload-btn').html('ADD FILE');
    $('.image-upload-wrap').show();
}
$('.image-upload-wrap').bind('dragover', function () {
    $('.image-upload-wrap').addClass('image-dropping');
});
$('.image-upload-wrap').bind('dragleave', function () {
    $('.image-upload-wrap').removeClass('image-dropping');
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function uploadFile(url) {
    var formData = new FormData();
    csrftoken=getCookie('csrftoken');
    formData.append('datafile',  $('#fileupload')[0].files[0])
    $.ajax(
        {
            url: url,
            method: 'post',
            data:formData,
            cache: false,
            processData: false,
            contentType: false,
            enctype: 'multipart/form-data',
            contentType: "application/html; charset=utf-8",
            success: function (result) {   
                $('.row.mt-2.p-0').show();
                $('.card-body.p-0').html(result)
            },
        }
    );
}

function clearInputFile(f){
    if(f.value){
        try{
            f.value = null; //for IE11, latest Chrome/Firefox/Opera...
        }catch(err){ }
    }
}

