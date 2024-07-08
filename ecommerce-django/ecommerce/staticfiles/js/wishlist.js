// Function to handle AJAX request for adding to wishlist
function addToWishlist(productId, size, color) {
    $.ajax({
        url: `http://127.0.0.1:8001/wishlist/add_to_wishlist/${productId}`,
        method: 'GET',
        data: {
            size: size,
            color: color
        },
        success: function(response) {
            console.log(response); // Log response for debugging
            if (response.bool) {
                alert(response.message); // Display success message to user
            } else {
                alert(response.message); // Display error message to user
            }
        },
        error: function(xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText); // Log any errors
            alert("Error adding to wishlist. Please try again."); // Notify user of error
        }
    });
}
