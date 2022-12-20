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
function generate_report(url){
    var data={
        'topics_number':$('#topics_number').val(),
        'method':$("#method option:selected").val(),
        'samples_length':$('#samples_length').val(),
    };
    console.log(data);
    fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers:{
            'Accept': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
    },
        body: JSON.stringify(
            data
        ) //JavaScript object of data to POST
    })
    .then(response => {
            return response.json() //Convert response to JSON
    })
    .then(data => {
        $('#report-content').html(data['html'])
    })
}