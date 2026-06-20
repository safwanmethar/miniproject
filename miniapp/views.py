from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Q
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Sum
from django.contrib import messages








from .models import Product, Customer, Review, Cart, Wishlist, Order, OrderItem, Category, Brand, Payment


# ---------------- HOME ----------------
def home(request):
    return render(request, 'Home.html')


# ---------------- LOGIN ----------------
def login(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            if user.is_superuser:
                return redirect('adminhome')
            else:
                return redirect('userhome')

        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')


# ---------------- REGISTER ----------------
def register(request):

    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')

        # 1. Create Django User (login system)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # 2. Create Customer (your requirement)
        Customer.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email
        )

        messages.success(request, "Customer account created successfully")
        return redirect('login')

    return render(request, 'register.html')


# ---------------- USER HOME ----------------
def userhome(request):

    featured_products = Product.objects.all()[:8]

    return render(request, 'user/userhome.html', {
        'featured_products': featured_products
    })


# ---------------- PRODUCTS ----------------
def products(request):

    search = request.GET.get('search')
    product_list = Product.objects.all()

    if search:
        product_list = product_list.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    return render(request, 'user/products.html', {
        'products': product_list
    })


def product_details(request,id):

    product = get_object_or_404(
        Product,
        id=id
    )

    reviews = Review.objects.filter(
        product=product
    )

    if request.method == "POST":

        rating = request.POST.get('rating')

        comment = request.POST.get('comment')

        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment
        )

        return redirect(
            'product_details',
            id=id
        )

    context = {
        'product': product,
        'reviews': reviews
    }

    return render(
        request,
        'user/product_details.html',
        context
    )
# ---------------- CART VIEW ----------------
@login_required
def cart_view(request):

    cart_items = Cart.objects.filter(user=request.user)

    total_items = 0
    total_price = 0

    for item in cart_items:
        total_items += item.quantity
        total_price += item.product.price * item.quantity

    return render(request, 'user/cart.html', {
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price
    })


# ---------------- ADD TO CART ----------------
@login_required
def add_to_cart(request, id):

    product = get_object_or_404(Product, id=id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1

    cart_item.save()

    return redirect('cart')


# ---------------- REMOVE FROM CART ----------------
@login_required
def remove_from_cart(request, id):

    item = get_object_or_404(Cart, id=id, user=request.user)
    item.delete()

    return redirect('cart')


# ---------------- WISHLIST ----------------
@login_required
def wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    )

    return render(
        request,
        'user/wishlist.html',
        {'wishlist_items': wishlist_items}
    )

@login_required
def add_to_wishlist(request, id):

    product = get_object_or_404(Product, id=id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect('/wishlist')

@login_required
def remove_from_wishlist(request, id):

    item = get_object_or_404(
        Wishlist,
        id=id,
        user=request.user
    )

    item.delete()

    return redirect('/wishlist')

@login_required
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    total_price = 0
    total_items = 0

    for item in cart_items:
        total_price += item.product.price * item.quantity
        total_items += item.quantity

    if request.method == "POST":

        order = Order.objects.create(
            user=request.user,
            total_price=total_price
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()

        # clear cart after order
        cart_items.delete()

        return redirect('/orders')

    return render(
        request,
        'user/checkout.html',
        {
            'cart_items': cart_items,
            'total_price': total_price,
            'total_items': total_items
        }
    )

@login_required
def orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'user/orders.html',
        {'orders': orders}
    )


# ---------------- HOME ----------------
def adminhome(request):

    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()

    return render(
        request,
        'admin/adminhome.html',
        {
            'total_products': total_products,
            'total_orders': total_orders,
            'total_users': total_users,
            'pending_orders': pending_orders
        }
    )

def admin_orders(request):

    orders = Order.objects.all().order_by('-created_at')

    return render(
        request,
        'admin/adminorders.html',
        {'orders': orders}
    )

def update_order(request, id):

    order = get_object_or_404(Order, id=id)

    if request.method == "POST":

        status = request.POST.get('status')

        order.status = status
        order.save()

    return redirect('/admin-orders')

def admin_products(request):

    products = Product.objects.all().order_by('-id')

    return render(
        request,
        'admin/adminproducts.html',
        {'products': products}
    )
def add_product(request):

    categories = Category.objects.all()
    brands = Brand.objects.all()

    if request.method == "POST":

        Product.objects.create(
            name=request.POST.get('name'),
            category_id=request.POST.get('category'),
            brand_id=request.POST.get('brand'),
            description=request.POST.get('description'),
            price=request.POST.get('price'),
            stock=request.POST.get('stock'),
            image=request.FILES.get('image')
        )

        return redirect('/admin-products')

    return render(
        request,
        'admin/addproduct.html',
        {
            'categories': categories,
            'brands': brands
        }
    )

def edit_product(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    categories = Category.objects.all()
    brands = Brand.objects.all()

    if request.method == "POST":

        product.name = request.POST.get('name')
        product.category_id = request.POST.get('category')
        product.brand_id = request.POST.get('brand')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()

        return redirect('/admin-products')

    return render(
        request,
        'admin/editproduct.html',
        {
            'product': product,
            'categories': categories,
            'brands': brands
        }
    )

def delete_product(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    product.delete()

    return redirect('/admin-products')

def admin_categories(request):

    categories = Category.objects.all()

    return render(
        request,
        'admin/admincategories.html',
        {'categories': categories}
    )

def add_category(request):

    if request.method == "POST":

        Category.objects.create(
            name=request.POST.get('name')
        )

        return redirect('/admin-categories')

    return render(
        request,
        'admin/addcategory.html'
    )

def edit_category(request, id):

    category = get_object_or_404(
        Category,
        id=id
    )

    if request.method == "POST":

        category.name = request.POST.get('name')
        category.save()

        return redirect('/admin-categories')

    return render(
        request,
        'admin/editcategory.html',
        {'category': category}
    )

def delete_category(request, id):

    category = get_object_or_404(
        Category,
        id=id
    )

    category.delete()

    return redirect('/admin-categories')

def admin_brands(request):

    brands = Brand.objects.all()

    return render(
        request,
        'admin/adminbrands.html',
        {'brands': brands}
    )

def add_brand(request):

    if request.method == "POST":

        Brand.objects.create(
            name=request.POST.get('name')
        )

        return redirect('/admin-brands')

    return render(
        request,
        'admin/addbrand.html'
    )

def edit_brand(request, id):

    brand = get_object_or_404(
        Brand,
        id=id
    )

    if request.method == "POST":

        brand.name = request.POST.get('name')
        brand.save()

        return redirect('/admin-brands')

    return render(
        request,
        'admin/editbrand.html',
        {'brand': brand}
    )

def delete_brand(request, id):

    brand = get_object_or_404(
        Brand,
        id=id
    )

    brand.delete()

    return redirect('/admin-brands')

def logout_view(request):

    logout(request)
    return redirect('home')


def admin_customers(request):

    customers = User.objects.all()

    return render(
        request,
        'admin/admincustomers.html',
        {'customers': customers}
    )
@login_required
def profile(request):

    return render(
        request,
        'user/profile.html'
    )

def reports(request):

    total_orders = Order.objects.count()

    total_sales = (
        Order.objects.aggregate(
            Sum('total_price')
        )['total_price__sum']
        or 0
    )

    total_products = Product.objects.count()

    return render(
        request,
        'admin/reports.html',
        {
            'total_orders': total_orders,
            'total_sales': total_sales,
            'total_products': total_products
        }
    )

def products(request):

    search = request.GET.get('search')

    products = Product.objects.all()

    if search:

        products = products.filter(

            Q(name__icontains=search) |

            Q(description__icontains=search)

        )

    return render(
        request,
        'user/products.html',
        {'products': products}
    )
def settings(request):

    return render(
        request,
        'admin/settings.html'
    )
def admin_reviews(request):
    return render(request, 'admin/adminReviews.html')






@login_required
def payment(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if request.method == "POST":

        Payment.objects.get_or_create(
            order=order,
            defaults={
                'amount': order.total_price,
                'payment_method': request.POST.get('payment_method'),
                'payment_status': 'Success'
            }
        )

        # ✅ FIX: mark as Paid, NOT Shipped
        order.status = 'Paid'
        order.save()

        messages.success(request, "Payment successful!")
        return redirect('payment_success', order_id=order.id)

    return render(
        request,
        'user/payment.html',
        {'order': order}
    )
@login_required
def payment_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        'user/payment_success.html',
        {'order': order}
    )
@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # ✅ allow cancel before shipping
    if order.status in ["Pending", "Paid"]:

        order.status = "Cancelled"
        order.save()

    return redirect('orders')