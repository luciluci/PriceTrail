function deleteItem(itemId, token) {
     var urlApi = "http://localhost:8006";

    var payload = {
    'csrfmiddlewaretoken': token,
    'product-id': itemId
    };

    var data = new FormData();
    data.append( "json", JSON.stringify( payload ) );

    function validate(response) {
        console.log(response);
    }

    if (itemId) {
        fetch(urlApi + '/delete-tail/1', {
          method: 'GET'
        })
        .then(response => response.json())
        .then(response => validate(response));
    }
}

function checkUrl(input, token) {

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
        })
        .then(response => response.json())
        .then(response => validate(response));
    }
};

function checkProfileChanges(){
    document.getElementById("register-profile-submit").disabled = false;
}