$(document).ready(function(){
    $('.ajaxLoader').hide();
    
    var selectedSortValue = '';

    // Event handler for the "Sort By" dropdown.
    $('#sort-list').on('change', function(){
        selectedSortValue = $(this).val();
        console.log('Selected Sort Value:', selectedSortValue); // Debugging
        filterAndSortProducts(selectedSortValue);
    });

    // Event handler for other filters (checkboxes and price filter).
    $(".filter-checkbox, #priceFilterBtn").on('click', function(){
        filterAndSortProducts(selectedSortValue);
    });

    function filterAndSortProducts(sortValue) {
        var _filterObj = {
            minPrice: $('#maxPrice').attr('min'),
            maxPrice: $('#maxPrice').val(),
            sort: sortValue
        };

        // Handle checkboxes
        $('.filter-checkbox:checked').each(function(index, ele){
            var _filterKey = $(this).data('filter');
            if (!_filterObj[_filterKey]) {
                _filterObj[_filterKey] = [];
            }
            _filterObj[_filterKey].push($(this).val());
        });

        // Print the filter object for debugging
        console.log('Filters being sent:', _filterObj);

        // Ajax request
        $.ajax({
            url: '/store/filter_data',
            data: _filterObj,
            dataType: 'json',
            beforeSend: function(){
                $('.ajaxLoader').show();
            },
            success: function(res){
                console.log('Response:', res);
                $("#filteredProducts").html(res.data);

                // Check if the response correctly reflects the sort value
                console.log('Sort applied:', sortValue);
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            },
            complete: function(){
                $('.ajaxLoader').hide();
            }
        });
    }
});
