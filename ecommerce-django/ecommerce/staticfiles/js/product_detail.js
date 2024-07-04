$(document).ready(function () {

  $('.p_img').ezPlus()
    $('.p_img').addClass('hidden')
    $('.p_img').first().removeClass('hidden').addClass('focused')
    $(".thumbnail").on('click', function(e){
    e.preventDefault()
    var _img = $(this).data('image')
    $(".p_img").addClass('hidden')
    $("#image-" + _img).removeClass('hidden').addClass('focused')
  })
// --------------------------------------------------------------------------

  // Product Variation
  $(".choose-size").hide();


  $(".choose-color").on('click', function(){
    $(".choose-color").removeClass('focused')
    $(this).addClass('focused')
    $('.p_img').addClass('hidden')
    var _color = $(this).attr('data-color')
    var _img = $(this).attr('data-image')
    $("#image-" + _img).removeClass('hidden').addClass('focused')
    $(".choose-size").removeClass('active')
    $(".choose-size").hide()

    $(".color-"+ _color).show()
    $(".color-"+ _color).first().addClass('active')
    var _price = $(".color-"+_color).first().attr('data-price')
    $(".product-price").text(_price)


  })

  
  var _color = $(".choose-color").first().attr('data-color')
  $(".color-"+_color).show()
  $(".choose-color").first().addClass('focused')
  $(".color-"+ _color).first().addClass('active')
  var _price = $(".active").attr('data-price')
  $(".product-price").text(_price)

  

  $(".choose-size").on('click', function(){
    $(".choose-size").removeClass('active')
    $(this).addClass('active')
    var _price=$(this).attr('data-price')
    $(".product-price").text(_price)
  })


  // -------------------------------------------------
  // Add to cart Button:
  $("#addToCartBtn").on('click', function(){
    var _vm = $(this)
    var _qty = 1
    var _productID = $(".product-id").val()
    var _productName = $(".product-name").val()
    var _productPrice = $(".product-price").text()
    var _color = $(".active").data('color')
    var _size = $(".active").data('size')
    console.log(_color);
    // Ajax
    $.ajax({
      url: '/cart/add_cart/'+_productID + '/',
      data:{
        'id': _productID,
        'qty': _qty,
        'name': _productName,
        'price': _productPrice,
        'color': _color,
        'size': _size
      },
      dataType: 'json',
      beforeSend: function(){
          _vm.attr('disabled', true)
      },
      success: function(res){
          console.log(res.bool);
          _vm.attr('disabled', false)
          window.location.reload()
      }
  });
    // Ajax end
  })

  
}) // Document Ready end
   
