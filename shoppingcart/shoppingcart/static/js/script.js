try{
    books_data = JSON.parse(books)
    books = books_data.items;
    var track = 0;
    var link = '';
    display(track)
}
catch(err){
    
}

function display(i){
    link = '/addtocart/'+i;
    document.getElementById("authors").innerText = books[i].volumeInfo.authors[0];
    try{
        document.getElementById("addtocart").style.visibility = 'visible';
        document.getElementById("retailPrice").innerText = books[i].saleInfo.retailPrice.amount +" "+ books[i].saleInfo.retailPrice.currencyCode;
    }
    catch(err){
        document.getElementById("addtocart").style.visibility = 'hidden';
        document.getElementById("retailPrice").innerText = 'NOT FOR SALE';
    }
    document.getElementById("publisher").innerText = books[i].volumeInfo.publisher;
    document.getElementById("publishedDate").innerText = books[i].volumeInfo.publishedDate;
    document.getElementById("smallThumbnail").src = books[i].volumeInfo.imageLinks.smallThumbnail;
    document.getElementById("title").innerText = books[i].volumeInfo.title;
    document.getElementById("description").innerText = books[i].volumeInfo.description;
    document.getElementById("previewLink").href = books[i].volumeInfo.previewLink;
    if(i == 0){
        document.getElementById("previous").style.visibility = 'hidden';
        document.getElementById("next").style.visibility = 'visible';
    }
    else if(i == books.length-1){
        document.getElementById("previous").style.visibility = 'visible';
        document.getElementById("next").style.visibility = 'hidden';
    }
    else{
        document.getElementById("previous").style.visibility = 'visible';
        document.getElementById("next").style.visibility = 'visible';
    }
    document.getElementById("cart_full").innerText = ''
}

function next(){
    if(track == books.length-1) {
        return
    }
    track++;
    display(track)
}

function previous(){
    
    if(track == 0) {
        return
    }
    track--;
    display(track);
}
// var Model = require('web.Model');
// var c
$(function() {
    $('button#addtocart').bind('click', function() {
        $.getJSON(link,
            function(data) {
                if(data=="full"){
                    document.getElementById("cart_full").innerText = 'Limit Exceeded'
                }
                else{
                    toaster()
                }
                console.log(data)
        });
        return false;
    });
});

$(function() {
    $('button#clear').bind('click', function() {
        $.getJSON("/clear_cart",
            function(data) {
                window.location.href='/checkout'      
        });
        return false;
    });
});

$(function() {
    $('button#proceed').bind('click', function() {
        $.getJSON("/proceed",
            function(data) {
                window.location.href='/orders'
        });
        return false;
    });
});

function plus(id){
    
    $.getJSON('/plus/'+id,
        function(data) {
            if (data=='full'){
                document.getElementById("error_"+id).innerText = "Full"
            }
            else{
                document.getElementById("quantity_"+id).innerText = parseInt(document.getElementById("quantity_"+id).innerText)+1;
                document.getElementById("total").innerText = parseInt(document.getElementById("total").innerText)+1;
                document.getElementById("error_"+id).innerText = ""
            }
            console.log(data)
    });
    return false;

}

function minus(id){
    $.getJSON('/minus/'+id,
        function(data) {
            if (data=='empty'){
                var el = document.getElementById( 'row_'+id );
                el.parentNode.removeChild( el );
                document.getElementById("total").innerText = parseInt(document.getElementById("total").innerText)-1;
            }
            else{
                document.getElementById("quantity_"+id).innerText = parseInt(document.getElementById("quantity_"+id).innerText)-1
                document.getElementById("total").innerText = parseInt(document.getElementById("total").innerText)-1;
                document.getElementById("error_"+id).innerText = ""
            }
            console.log(data)
    });
    return false;
}

function toaster() {
    // Get the snackbar DIV
    var x = document.getElementById("snackbar")

    // Add the "show" class to DIV
    x.className = "show";

    // After 3 seconds, remove the show class from DIV
    setTimeout(function(){ x.className = x.className.replace("show", ""); }, 800);
}