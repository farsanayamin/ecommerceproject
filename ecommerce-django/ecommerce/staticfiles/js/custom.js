$(document).ready(function(){
    // Increment quantity
    $(".increment-btn").on('click', function(){
        var cartItemId = $(this).data('cart-item-id');
        var $qtyInput = $(this).closest('.input-group').find(".qty-input");
        var qty = parseInt($qtyInput.val());
        
            qty++;
            $qtyInput.val(qty);
            updateCart(cartItemId, qty);
        
    });

    // Decrement quantity
    $(".decrement-btn").on('click', function(){
        var cartItemId = $(this).data('cart-item-id');
        var $qtyInput = $(this).closest('.input-group').find(".qty-input");
        var qty = parseInt($qtyInput.val());
        if (qty > 1) {
            qty--;
            $qtyInput.val(qty);
            updateCart(cartItemId, qty);
        }
    });


    $(".qty-input").on('input', function() {
        var productQuantity = $(this).data('productquantity'); 
        console.log("productQuantity", productQuantity);
    
        var cartItemId = $(this).data('cart-item-id');
        var newQuantity = $(this).val();
    
        if (newQuantity < 1) {
            newQuantity = 1;
            $(this).val(newQuantity); 
            // location.reload();
        } else if (newQuantity > productQuantity) {
            newQuantity = productQuantity;
            $(this).val(newQuantity);
        //     // location.reload();
        }
    
        updateCart(cartItemId, newQuantity);
    });
    

    // Function to send the update to the server
    
    function updateCart(cartItemId, newQuantity) {
        console.log(cartItemId, newQuantity);
        var csrftoken = getCookie('csrftoken')
        $.ajax({
            method: 'POST',
            url: '/cart/update_cart',
            data: {
                cart_item_id: cartItemId,
                new_quantity: newQuantity
            },
            dataType: 'json',
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(res){
                console.log(res);
                $("#cart").html(res.data)
            }
        });
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
