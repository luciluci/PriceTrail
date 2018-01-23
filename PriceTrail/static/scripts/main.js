// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            //var cookie = jQuery.trim(cookies[i]);
            var cookie = cookies[i].trim()
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
//var csrftoken = getCookie('csrftoken');

function checkUrl(input, token) {

    console.log('B:' + token)
    token = getCookie("csrftoken")
    console.log('A:' + token)

    var urlApi = "http://localhost:8006";
    document.getElementById("valid-item").style.display = "none";
    document.getElementById("invalid-item").style.display = "none";
    document.getElementById("add-tail-submit").disabled = true;
    document.getElementById("product_name").value = ''
    document.getElementById("product_price").value = ''
    document.getElementById("product_url").value = ''
    document.getElementById("product_shop").value = ''

    function validate(response) {
        console.log(response);

        if (response.status === "valid") {
            document.getElementById("valid-item").style.display = "block";
            document.getElementById("product_name").value = response.pname;
            document.getElementById("product_price").value = response.pprice;
            document.getElementById("product_url").value = response.purl
            document.getElementById("product_shop").value = response.pshop

            document.getElementById("add-tail-submit").disabled = false;
        } else {
            document.getElementById("invalid-item").style.display = "block";
        }
    }
    function error (code) {
        console.log("error try again" + code);
    }

    var payload = {
    'csrfmiddlewaretoken': token,
    'product-url': input.value,
    b: 2
    };

    var data = new FormData();
    data.append( "json", JSON.stringify( payload ) );

    var myHeaders = new Headers({
    'Content-Type': 'application/json',
    'X-CSRFToken': token
    });

    if (input.value) {
        fetch(urlApi + '/add-tail/', {
          method: 'POST',
          body: data
//          credentials: 'include',
//          headers: {
//            'Accept': 'application/json',
//            'X-Requested-With': 'XMLHttpRequest',
//            'Content-Type': 'application/json',
//            'X-CSRFToken': token
//          }
        })
        .then(response => response.json())
        .then(response => validate(response));
    }
};