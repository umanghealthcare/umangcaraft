from django.shortcuts import render,redirect
from .models import User,Product,Wishlist,Cart,Transaction
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt


def initiate_payment(request):
	user=User.objects.get(email=request.session['email'])
	try:
		amount = int(request.POST['amount'])
	except:
		return render(request, 'pay.html', context={'error': 'Wrong Accound Details or amount'})
		transaction = Transaction.objects.create(made_by=user, amount=amount)
	transaction.save()
	merchant_key = settings.PAYTM_SECRET_KEY
	params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )
	paytm_params = dict(params)
	checksum = generate_checksum(paytm_params, merchant_key)

	transaction.checksum = checksum
	transaction.save()
	carts=Cart.objects.filter(user=user)
	for i in carts:
		i.status='paid'
		i.save()

	paytm_params['CHECKSUMHASH'] = checksum
	print('SENT: ', checksum)
	return render(request, 'payments/redirect.html', context=paytm_params)

# Create your views here.
def index(request):
	product=Product.objects.all()
	return render(request,'index.html',{'product':product})

def header(request):
	return render(request,'header.html')
def contact(request):
	return render(request,'contact.html')

def products(request):
	return render(request,'products.html')

def clients(request):
	return render(request,'clients.html')

def category(request):
	return render(request,'category.html')
def log(request):
	if request.method=='POST':
		try:
			user=User.objects.get(	
					email=request.POST['email'],
					password=request.POST['password'],
					)
			if user.usertype=='user':
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['profile_pic']=user.profile_pic.url
				carts=Cart.objects.filter(user=user, status='pending')
				net_price=0
				for i in carts:
					net_price=net_price+i.total_price
				request.session['cart_count']=len(carts)
				return redirect('index')
			else:
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['profile_pic']=user.profile_pic.url
				return redirect('seller_index')
		except Exception as e :
			print(e)
			msg='email id does not match'
			return render(request,'log.html',{'msg':msg})
	else:
		return render(request,'log.html')

def signup(request):
	if request.method=='POST':
		try:
			user=User.objects.get(email=request.POST['email'])
			msg='email alredy register'
			return render(request,'signup.html',{'msg':msg})
		except:
			pass
		if request.POST['password']==request.POST['cpassword']:
			User.objects.create(
				fname=request.POST['fname'],
				usertype=request.POST['usertype'],
				lname=request.POST['lname'],
				email=request.POST['email'],
				mobile=request.POST['mobile'],
				address=request.POST['address'],
				profile_pic=request.FILES['profile_pic'],
				password=request.POST['password'],
				dob=request.POST['dob'],
				)
			msg='signup successfuly'
			return render(request,'log.html',{'msg':msg})
		else:
			msg='password and confirm password does not match'
			return render(request,'signup.html')
	else:
		return render(request,'signup.html')

def logout(request):
	del request.session['email']
	del request.session['fname']
	del request.session['profile_pic']
	return redirect('log')
		

def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=='POST':
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.email=request.POST['email']
		user.address=request.POST['address']
		user.mobile=request.POST['mobile']
		try:
			user.profile_pic=request.FILES['profile_pic']
		except:
			pass
		user.save()
		msg='update successfuly'
		return render(request,'profile.html',{'user':user,'msg':msg})
	else:
		return render(request,'profile.html',{'user':user})

def change_pass(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=='POST':
		if user.password== request.POST['opassword']:
			if request.POST['npassword']==request.POST['cpassword']:
				user.password=request.POST['npassword']
				user.save()
				msg='password change successful'
				return render(request,'change_pass.html',{'msg':msg})
			else:
				msg=' new passwor and confirm password does not match '
				return render(request,'change_pass.html',{'msg':msg})
		else:
			msg= 'old password does not match '
			return render(request,'change_pass.html',{'msg':msg})
	else:
		return render(request,'change_pass.html')
def seller_index(request):
	products=Product.objects.all()
	return render(request,'seller_index.html',{'products':products})

def seller_header(request):
	return render(request,'seller_header.html')

def add_product(request):
	if request.method=='POST':
		seller=User.objects.get(email=request.session['email'])
		Product.objects.create(
			seller=seller,
			product_name=request.POST['product_name'],
			product_dis=request.POST['product_dis'],
			product_detail=request.POST['product_detail'],
			product_pic=request.FILES['product_pic'],
			)
		msg='itme add successfuly'
		return render(request,'add_product.html',{'msg':msg})
	else:
		return render(request,'add_product.html')

def seller_product_details(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller_product_details.html',{'product':product})

def seller_edit_product(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=='POST':
		product.product_name=request.POST['product_name']
		product.product_dis=request.POST['product_dis']
		product.product_detail=request.POST['product_detail']
		product.product_price=request.POST['product_price']
		try:
			product.product_pic=request.FILES['product_pic']
		except:
			pass
		product.save()
		msg='product edit successfuly'
		return render(request,'seller_edit_product.html',{'product':product,'msg':msg})
	else:
		return render(request,'seller_edit_product.html',{'product':product})

def seller_delete_product(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return	render(request,'seller_index.html')

def single_product(request,pk):
	product=Product.objects.get(pk=pk)
	if "email" in request.session:
		wishlist_flag=False
		user=User.objects.get(email=request.session['email'])
		try:
			Wishlist.objects.filter(user=user,product=product)
			wishlist_flag=True
		except:
			pass
		cart_flag=False
		try:
			Cart.objects.get(user=user,product=product)
			cart_flag=True
		except:
			pass
		return	render(request,'single_product.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})
	else:
		return	render(request,'single_product.html',{'product':product})
def add_to_wishlist(request,pk):
	if "email" in request.session:
		product=Product.objects.get(pk=pk)
		user=User.objects.get(email=request.session['email'])
		Wishlist.objects.create(
			product=product,
			user=user
			)
		return render(request,'wishlist.html')
	else:
		return render(request,'log.html')
def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	return render(request,'wishlist.html',{'wishlists':wishlists})

def remove_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.filter(user=user)
	wishlist.delete()
	return render(request,'wishlist.html')

def add_to_cart(request,pk):
	if "`email" in request.session:
		product=Product.objects.get(pk=pk)
		user=User.objects.get(email=request.session['email'])
		Cart.objects.create(
			user=user,
			product=product,
			product_price=product.product_price,
			total_price=product.product_price,
			)
		return redirect('cart')
	else:
		return render(request,'log.html')
def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.filter(user=user,status='pending')
	for i in cart:
		net_price=net_price+i.total_price
	request.session['cart_count']=len(cart)	
	return render(request,'cart.html',{'cart':cart,'net_price':net_price})

def remove_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.filter(user=user)
	cart.delete()
	return redirect('cart')
 
def change_qty(request,pk):
 	carts=Cart.objects.get(pk=pk)
 	product_qty=int(request.POST['product_qty'])
 	carts.product_qty=product_qty
 	carts.total_price=product_qty*carts.product_price
 	carts.save()
 	return render(request,'cart.html',{'product_qty':product_qty})

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)
