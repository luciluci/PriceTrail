var validateURL = function(url) {
  return new Promise(function(resolve, reject) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                resolve(xhttp.responseText);
                console.log(this.status);
            }
        };
        xhttp.open("POST", "http://shopping-list.ro/validate-product/", true);
        //xhttp.open("POST", "http://localhost:8006/validate-product/", true);

        var payload = {
            'product-url': url,
        };

        var data = new FormData();
        data.append( "json", JSON.stringify( payload ) );

        console.log("send before");
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
        xhttp.open("POST", "http://shopping-list.ro/add-new-product/", true);
        //xhttp.open("POST", "http://localhost:8006/add-new-product/", true);

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
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", '/delete-product/'+pid, false ); // false for synchronous request
        xmlHttp.send( null );
        window.open("/my-products/", "_self");
    }
}

//$('#btnStep1').click(function(){
function btnStep1Click(){
    document.getElementById("btnStep1").innerHTML = '<i class="fa fa-spinner fa-spin"></i>  Next'
    document.getElementById("btnStep1").disabled = true;

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
        console.log("VALIDATE PRODUCT")
        document.getElementById("btnStep1").innerHTML = 'Next'
        document.getElementById("btnStep1").disabled = false;

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
            document.getElementById("invalidURLId").innerHTML = json_result.message;
        }
    }

    validateURL(currentURL)
    .then(response => validate(response));
};

function btnStep2Click(){
    document.getElementById("btnStep2").innerHTML = '<i class="fa fa-spinner fa-spin"></i>  Next'
    document.getElementById("btnStep2").disabled = true;

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
        document.getElementById("btnStep2").innerHTML = 'Next'
        document.getElementById("btnStep2").disabled = false;
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
};

function btnStep3Click(){
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
};

function editEmail(){
    document.getElementById("update-profile").removeAttr("style");
}
