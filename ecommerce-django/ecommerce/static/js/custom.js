$(document).ready(function(){
    // Maximum quantity allowed per item
    var maxQuantity = 3;

    // Increment quantity
    $(".increment-btn").on('click', function(){
        var cartItemId = $(this).data('cart-item-id');
        var $qtyInput = $(this).closest('.input-group').find(".qty-input");
        var qty = parseInt($qtyInput.val());
        
        if (qty < maxQuantity) {
            qty++;
            $qtyInput.val(qty);
            updateCart(cartItemId, qty);
        } else {
            alert("Maximum quantity for this item is " + maxQuantity);
        }
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

    // Handle direct input of quantity
    $(".qty-input").on('input', function() {
        var cartItemId = $(this).data('cart-item-id');
        var newQuantity = parseInt($(this).val());

        if (newQuantity < 1) {
            newQuantity = 1;
        } else if (newQuantity > maxQuantity) {
            newQuantity = maxQuantity;
            alert("Maximum quantity for this item is " + maxQuantity);
        }

        $(this).val(newQuantity); // Update the input value to reflect the valid quantity
        updateCart(cartItemId, newQuantity);
    });

    // Function to send the update to the server
    function updateCart(cartItemId, newQuantity) {
        console.log(cartItemId, newQuantity);
        var csrftoken = getCookie('csrftoken');
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
                $("#cart").html(res.data);
            }
        });
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
