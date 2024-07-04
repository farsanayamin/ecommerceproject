from itertools import product
from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from carts.models import CartItem
from .forms import OrderForm
from .models import *
import datetime
import json

from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO


def render_to_pdf(template_path, context):
    template = get_template(template_path)
    html = template.render(context)
    response = BytesIO()
    
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")),
        response,
        pagesize='letter'  # Set the page size to letter (8.5 x 11 inches)
    )
    
    if not pdf.err: #type:ignore
        response.seek(0)
        return response
    return None


# ======================================= DOWNLOAD INVOICE ===============================================================================================================================

def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    discount = 0
    if order.coupon:
        discount  = order.coupon.discount_price
    ordered_products = OrderProduct.objects.filter(order_id=order.id) #type:ignore
    payment = Payment.objects.get(transaction_id=order.payment.transaction_id) #type:ignore
    subtotal = 0
   
    for item in ordered_products:
        subtotal += item.product_price * item.quantity

    context = {
        'order': order,
        'order_number': order.order_number,
        'transID': payment.transaction_id,
        'ordered_products': ordered_products,
        'subtotal': subtotal,
        'status': payment.status,
        'discount': discount,
        'grand_total': order.order_total
    }

    template_path = 'orders/invoice.html'  # Replace with the path to your HTML template
    pdf_response = render_to_pdf(template_path, context)

    if pdf_response:
        response = HttpResponse(pdf_response.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=invoice_{order.order_number}.pdf'
        return response

    # Handle the case where PDF generation fails
    return HttpResponse('PDF generation failed', status=500)

# --------------------------------------------------------------------------------------------------------------'


def cod_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    discount = 0
    if order.coupon:
        discount  = order.coupon.discount_price
    ordered_products = OrderProduct.objects.filter(order_id=order.id) #type:ignore
    subtotal = 0
   
    for item in ordered_products:
        subtotal += item.product_price * item.quantity

    context = {
        'order': order,
        'order_number': order.order_number,
        'transID': "N.A",
        'ordered_products': ordered_products,
        'subtotal': subtotal,
        'status': "NOT COMPLETED",
        'discount': discount,
        'grand_total': order.order_total -discount
    }

    template_path = 'orders/invoice.html'  # Replace with the path to your HTML template
    pdf_response = render_to_pdf(template_path, context)

    if pdf_response:
        response = HttpResponse(pdf_response.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=invoice_{order.order_number}.pdf'
        return response

    # Handle the case where PDF generation fails
    return HttpResponse('PDF generation failed', status=500)


# ================================================ PAYMENTS =======================================================================================================================

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered = False, order_number = body['orderID'])
    # Transactions details 
    payment = Payment(
        user = request.user,
        transaction_id = body['transID'],
        payment_id = body['paymentID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']
    )
    if order.coupon:
        payment.amount_paid -= order.coupon.discount_price  #type:ignore
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move Cart Items to Order Product 
    cart_items = CartItem.objects.filter(user = request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order = order
        orderproduct.payment = payment
        orderproduct.user= request.user
        orderproduct.product = item.product
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.variation.discounted_price    #type:ignore
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id = item.pk)

        orderproduct = OrderProduct.objects.get(id = orderproduct.pk)
        orderproduct.variation = cart_item.variation
        orderproduct.save()
        
    # Reduce the Stock
        variation = Variation.objects.get(product = item.product, id = item.variation.pk) #type:ignore
        variation.quantity -= item.quantity
        variation.save()
    #  Clear Cart
    CartItem.objects.filter(user = request.user).delete()

    # Send order recieved mail to customer
    mail_subject = 'Order Placed'
    message = render_to_string('orders/order_received_email.html',{
        'user':request.user,
        'order': order,
    })            
    to_email = request.user.email
    send_mail = EmailMessage(mail_subject, message, to = [to_email])
    send_mail.send()
    

    # Send order number and transaction id back to send Data

    data = {
        'order_number' : order.order_number,
        'transID' : payment.transaction_id,

    }
    return JsonResponse(data)




# ================================ PLACE ORDER ===================================================================================================================


def place_order(request, total=0, quantity = 0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    discount_price = 0
        
    for cart_item in cart_items:
        total += (cart_item.variation.discounted_price * cart_item.quantity) #type: ignore
        quantity += cart_item.quantity
        
        
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data["last_name"]
            data.phone = form.cleaned_data["phone"]
            data.email = form.cleaned_data["email"]
            data.address_line_1 = form.cleaned_data["address_line_1"]
            data.address_line_2 = form.cleaned_data["address_line_2"]
            data.country = form.cleaned_data["country"]
            data.state = form.cleaned_data["state"]
            data.city = form.cleaned_data["city"]
            data.pincode = form.cleaned_data["pincode"]
            data.order_note = form.cleaned_data["order_note"]
            data.tax = tax
            data.order_total = grand_total
            data.ip = request.META.get('REMOTE_ADDR')
            try:
                code = request.POST['coupon']
                coupon_obj = Coupon.objects.get(code = code)
                data.coupon = coupon_obj
                coupon_obj.is_used = True
                coupon_obj.save()
                discount_price = data.coupon.discount_price
            except:
                pass


            data.save()

            # Generate Order No
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")

            ordernumber = current_date + str(data.id) # type: ignore
            data.order_number = ordernumber
            data.save()


            order = Order.objects.get(user = current_user, is_ordered=False, order_number = ordernumber)
            
            context = {
                'order' : order,
                'cart_items': cart_items,
                'total' : total,
                'tax':tax,
                'grand_total': grand_total - discount_price,
                'discount': discount_price
            }

            return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')




# ============================================= ORDER COMPLETE ============================================================================================================================





def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('transaction_id')

    try:
        order = Order.objects.get(order_number = order_number, is_ordered = True)
        ordered_products = OrderProduct.objects.filter(order_id = order.id) # type: ignore
        payment = Payment.objects.get(transaction_id = transID)
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        grand_total = order.order_total
        if order.coupon:
            grand_total -= order.coupon.discount_price
            
        
        
        context ={
            'order':order,
            'ordered_products': ordered_products,
            'order_number':order.order_number,
            'transID' : payment.transaction_id,
            'payment' : payment,
            'subtotal' :subtotal,
            'grand_total':grand_total 
        }



    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

    return render(request, 'orders/order_complete.html', context)






# ======================================================= CANCEL ORDER ========================================================================================================================



def cancel_order(request,order_id):
    order = Order.objects.get(id = order_id, user=request.user )

    order.status = 'Cancelled'
    order.save()
    return redirect('my_orders')




# =================================================================== CASH ON DELIVERY ==============================================================================================
def cash_on_delivery(request):
    order_number = request.POST['order_number']
    print(order_number)
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_number )
    payment = Payment(
        user = request.user,
        payment_method = "Cash On Delivery",
        amount_paid = order.order_total,
        status = "NOT PAID"
    )
    if order.coupon :
        payment.amount_paid -= order.coupon.discount_price # type: ignore
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user = request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order = order
        orderproduct.payment = payment
        orderproduct.user = request.user
        orderproduct.product = item.product
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.variation.price #type:ignore
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id = item.pk)

        product_variation = cart_item.variation
        orderproduct = OrderProduct.objects.get(id = orderproduct.pk)

        product_variation = cart_item.variation
        orderproduct = OrderProduct.objects.get(id = orderproduct.pk)
        orderproduct.variation=product_variation
        orderproduct.save()

        variation = item.variation
        variation.quantity -= item.quantity #type:ignore
        variation.save()    #type:ignore
    
    CartItem.objects.filter(user = request.user).delete()
    mail_subject = 'Order Placed'
    message = render_to_string('orders/order_received_email.html',{
        'user':request.user,
        'order': order,
    })            
    to_email = request.user.email
    send_mail = EmailMessage(mail_subject, message, to = [to_email])
    send_mail.send()
    
    ordered_products = OrderProduct.objects.filter(order_id = order.id) #type:ignore
    subtotal = 0
    for i in ordered_products:
        subtotal += i.variation.discounted_price * i.quantity #type:ignore
    grand_total = order.order_total
    if order.coupon:
        grand_total -= order.coupon.discount_price
    context ={
            'order':order,
            'ordered_products': ordered_products,
            'order_number':order.order_number,
            'transID' : payment.transaction_id,
            'payment' : payment,
            'subtotal' :subtotal,
            'grand_total': grand_total
        }
    
    return render(request, 'orders/cod_complete.html', context)



# ============================ REFUND ====================================================================================================================

def process_refund(request):
    pass