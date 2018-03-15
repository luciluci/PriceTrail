//function deleteItem(itemId, token) {
//     var urlApi = "http://localhost:8006";
//
//    var payload = {
//    'csrfmiddlewaretoken': token,
//    'product-id': itemId
//    };
//
//    var data = new FormData();
//    data.append( "json", JSON.stringify( payload ) );
//
//    function validate(response) {
//        console.log(response);
//    }
//
//    if (itemId) {
//        fetch(urlApi + '/delete-tail/1', {
//          method: 'GET'
//        })
//        .then(response => response.json())
//        .then(response => validate(response));
//    }
//}

//function checkUrl(input, token) {
//
//    var urlApi = "http://localhost:8006";
//    document.getElementById("valid-item").style.display = "none";
//    document.getElementById("invalid-item").style.display = "none";
//    document.getElementById("add-tail-submit").disabled = true;
//    document.getElementById("product_name").value = ''
//    document.getElementById("product_price").value = ''
//    document.getElementById("product_url").value = ''
//    document.getElementById("product_shop").value = ''
//
//    function validate(response) {
//        console.log(response);
//
//        if (response.status === "valid") {
//            document.getElementById("valid-item").style.display = "block";
//            document.getElementById("product_name").value = response.pname;
//            document.getElementById("product_price").value = response.pprice;
//            document.getElementById("product_url").value = response.purl
//            document.getElementById("product_shop").value = response.pshop
//
//            document.getElementById("add-tail-submit").disabled = false;
//        } else {
//            document.getElementById("invalid-item").style.display = "block";
//        }
//    }
//    function error (code) {
//        console.log("error try again" + code);
//    }
//
//    var payload = {
//    'csrfmiddlewaretoken': token,
//    'product-url': input.value,
//    b: 2
//    };
//
//    var data = new FormData();
//    data.append( "json", JSON.stringify( payload ) );
//
//    var myHeaders = new Headers({
//    'Content-Type': 'application/json',
//    'X-CSRFToken': token
//    });
//
//    if (input.value) {
//        fetch(urlApi + '/add-tail/', {
//          method: 'POST',
//          body: data
//        })
//        .then(response => response.json())
//        .then(response => validate(response));
//    }
//};

var validateURL = function(url) {
  return new Promise(function(resolve, reject) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                resolve(xhttp.responseText);
            }
        };
        xhttp.open("POST", "http://localhost:8006/validate-product/", true);

        var payload = {
        'product-url': url,
        };

        var data = new FormData();
        data.append( "json", JSON.stringify( payload ) );

        xhttp.send(data);
  });
}

var addNewProduct = function(pname, pprice, purl, pshop) {
  return new Promise(function(resolve, reject) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                resolve(xhttp.responseText);
            }
        };
        xhttp.open("POST", "http://localhost:8006/add-new-product/", true);

        var payload = {
        'product_name': pname,
        'product_price': pprice,
        'product_url': purl,
        'product_shop': pshop,
        };

        var data = new FormData();
        data.append( "json", JSON.stringify( payload ) );

        xhttp.send(data);
  });
}

//function validateURL(url){
//    var xhttp = new XMLHttpRequest();
//    xhttp.onreadystatechange = function() {
//        if (this.readyState == 4 && this.status == 200) {
//            return true;
//        }
//        else{
//            return false;
//        }
//    };
//    xhttp.open("POST", "http://localhost:8006/add-tail/", true);
//
//    var payload = {
//    'product-url': url,
//    };
//
//    var data = new FormData();
//    data.append( "json", JSON.stringify( payload ) );
//
//    xhttp.send(data);
//}

function checkProfileChanges(){
    document.getElementById("register-profile-submit").disabled = false;
}

function openModalGraph(id, address)
{
    document.querySelector("#gotoProductButton").setAttribute('data-url', address)
    document.querySelector("#graphBody iframe").src = '/display-product/' + id.toString()
}

function openNewWindow()
{
    url = document.querySelector("#gotoProductButton").getAttribute('data-url')
    window.open(url+'/?type=individual');
}

function deleteProduct(pid)
{
    if (confirm("Are you sure you want to delete it?")) {
        window.open('/delete-product/'+pid);
    }
}

$('#btnStep1').click(function(){
    var curStep = $('#step-1'),
        curStepBtn = curStep.attr("id"),
        nextStepWizard = $('div.setup-panel div a[href="#' + curStepBtn + '"]').parent().next().children("a"),
        curInputs = curStep.find("input[type='text'],input[type='url']"),
        isValid = true;

    var currentURL = "";
     if (curInputs.length > 0){
        currentURL = curInputs[0].value;
     }

    $(".form-group").removeClass("has-error");
    for(var i=0; i<curInputs.length; i++){
        if (!curInputs[i].validity.valid){
            isValid = false;
            $(curInputs[i]).closest(".form-group").addClass("has-error");
        }
    }

    function validate(response) {
        var json_result = JSON.parse(response);
        if (json_result.status === "valid") {
            document.getElementById("invalidURLId").style.display = "none";
            document.getElementById("productNameId").innerHTML = json_result.pname;
            document.getElementById("productPriceId").innerHTML = json_result.pprice;
            document.getElementById("productURLId").innerHTML = json_result.purl;
            document.getElementById("productShopId").innerHTML = json_result.pshop;
            if (isValid)
                nextStepWizard.removeAttr('disabled').trigger('click');
        }
        else
        {
            document.getElementById("invalidURLId").style.display = "block";
        }
    }

    validateURL(currentURL)
    .then(response => validate(response));
});

$('#btnStep2').click(function(){

    var curStep = $('#step-2'),
        curStepBtn = curStep.attr("id"),
        nextStepWizard = $('div.setup-panel div a[href="#' + curStepBtn + '"]').parent().next().children("a"),
        curProductNameDivs = curStep.find("p[id='productNameId']"),
        curProductPriceDivs = curStep.find("p[id='productPriceId']"),
        curProductName = "",
        curProductPrice = "",
        isValid = true;

    $(".form-group").removeClass("has-error");
    if (curProductNameDivs.length > 0){
        curProductName = curProductNameDivs[0].innerHTML;
    }

    if (curProductPriceDivs.length > 0){
        curProductPrice = curProductPriceDivs[0].innerHTML;
    }

    if (!curProductName || !curProductPrice){
        isValid = false;
        $(".form-group").addClass("has-error");
    }

    function validate(response){
        console.log(response)
        nextStepWizard.removeAttr('disabled').trigger('click');
    }

    if (isValid)
    {
        var pname = document.getElementById("productNameId").innerHTML;
        var pprice = document.getElementById("productPriceId").innerHTML;
        var purl = document.getElementById("productURLId").innerHTML;
        var pshop = document.getElementById("productShopId").innerHTML;
        addNewProduct(pname, pprice, purl, pshop)
        .then(response => validate(response));
    }
});

$('#btnStep3').click(function(){

    var curStep = $('#step-3'),
        curStepBtn = curStep.attr("id"),
        nextStepWizard = $('div.setup-panel div a[href="#' + curStepBtn + '"]').parent().next().children("a"),
        curInputs = curStep.find("input[type='text'],input[type='url']"),
        isValid = true;

    $(".form-group").removeClass("has-error");
    for(var i=0; i<curInputs.length; i++){
        if (!curInputs[i].validity.valid){
            isValid = false;
            $(curInputs[i]).closest(".form-group").addClass("has-error");
        }
    }

    if (isValid)
        nextStepWizard.removeAttr('disabled').trigger('click');
});