$(document).ready(function(){
    $('.ajaxLoader').hide();
    
    // Initialize the selectedSortValue to an empty string.
    var selectedSortValue = '';

    // Event handler for the "Sort By" dropdown.
    $('#sort-list').on('change', function(){
        selectedSortValue = $(this).val();
        filterAndSortProducts(selectedSortValue); // Pass the selectedSortValue to the function.
    });

    // Event handler for other filters.
    $(".filter-checkbox, #priceFilterBtn").on('click', function(){
        filterAndSortProducts(selectedSortValue); // Pass the selectedSortValue to the function.
    });

    function filterAndSortProducts(sortValue) {
        var _filterObj = {};
        var _minPrice = $('#maxPrice').attr('min');
        var _maxPrice = $('#maxPrice').val();
        _filterObj.minPrice = _minPrice;
        _filterObj.maxPrice = _maxPrice;
        _filterObj.sort = sortValue; // Use the passed sortValue.

        $('.filter-checkbox').each(function(index, ele){
            var _filterVal = $(this).val();
            var _filterKey = $(this).data('filter');
            _filterObj[_filterKey] = Array.from(document.querySelectorAll('input[data-filter='+ _filterKey +']:checked')).map(function(el){
                return el.value;
            });
        });

        // Ajax 
        $.ajax({
            url: '/store/filter_data',
            data: _filterObj,
            dataType: 'json',
            beforeSend: function(){
                $('.ajaxLoader').show();
            },
            success: function(res){
                console.log(res);
                $("#filteredProducts").html(res.data);
                $('.ajaxLoader').hide();
            }
        });
    }
});

