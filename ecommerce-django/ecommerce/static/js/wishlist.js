$.ajax({
    url: `http://127.0.0.1:8001/wishlist/add_to_wishlist/${productId}`,
    method: 'POST',
    data: {
        'csrfmiddlewaretoken': csrf_token,
        'size': size,
        'color': color
    },
    success: function(response) {
        console.log(response); // Log response for debugging
        if (response.bool) {
            alert(response.message); // Display success message to user
        } else {
            alert(response.message); // Display error message to user
        }
    },
    error: function(xhr, status, error) {
        console.log(xhr.status + ": " + xhr.responseText); // Log any errors
        alert("Error adding to wishlist. Please try again."); // Notify user of error
    }
});
