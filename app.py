from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
import os
import db
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import json, math

app=Flask(__name__)
app.secret_key=os.getenv('SHOPSPHERE_SECRET','shopsphere-demo-secret')
ADMIN_USER=os.getenv('SHOPSPHERE_ADMIN_USER','admin')
ADMIN_PASS=os.getenv('SHOPSPHERE_ADMIN_PASS','shopsphere@123')
db.init_db()

IMG={'P001': 'https://img.drz.lazcdn.com/static/bd/p/7b08972aa26045bb4a0daf055e530ac2.jpg_720x720q80.jpg', 'P002': 'https://i.mi.ua/media/catalog/product/cache/1/image/710x600/602f0fa2c1f0d1ba5e241f914e856ff9/1/1/1111_32_4.webp', 'P003': 'https://bludiode.com/img/p/4/5/7/9/1/45791.jpg', 'P004': 'https://down-ph.img.susercontent.com/file/cn-11134207-7r98o-ly8247xxkmg23f', 'P005': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=85', 'P006': 'https://images.unsplash.com/photo-1609592424613-b6d8f3f9f6b0?auto=format&fit=crop&w=900&q=85', 'P007': 'https://images.unsplash.com/photo-1609592424613-b6d8f3f9f6b0?auto=format&fit=crop&w=900&q=85', 'P008': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=85', 'P009': 'https://images.unsplash.com/photo-1606904825846-647eb07f5be2?auto=format&fit=crop&w=900&q=85', 'P010': 'https://images.unsplash.com/photo-1527814050087-3793815479db?auto=format&fit=crop&w=900&q=85', 'P011': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=85', 'P012': 'https://images.unsplash.com/photo-1603252110481-7ba873bf42ab?auto=format&fit=crop&w=900&q=85', 'P013': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=85', 'P014': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=85', 'P015': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=85'}
CATEGORY_META={
 'Electronics':('◈','Tech that fits your life','https://images.unsplash.com/photo-1468495244123-6c6c332eeece?auto=format&fit=crop&w=900&q=85'),
 'Fashion':('◇','Everyday style, elevated','https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=900&q=85'),
 'Home & Kitchen':('⌂','Make your space smarter','https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=900&q=85'),
 'Beauty':('✦','Small rituals, big glow','https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=900&q=85'),
 'Sports':('△','Move better. Go further.','https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=900&q=85'),
 'Books':('▤','Ideas worth carrying','https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=900&q=85')}

IMAGE_POOLS={
 'Electronics':[
  'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=900&q=85'],
 'Fashion':[
  'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1603252110481-7ba873bf42ab?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85'],
 'Home & Kitchen':[
  'https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1583845112203-454c38f4f5f8?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85'],
 'Beauty':[
  'https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1612817288484-6f916006741a?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=900&q=85'],
 'Sports':[
  'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1517649763962-0c623066013b?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1599058917212-d750089bc07e?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1552674605-db6ffd4facb5?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1538805060514-97d9cc17730c?auto=format&fit=crop&w=900&q=85'],
 'Books':[
  'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1526243741027-444d633d7365?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=900&q=85']}

def img_for(pid):
    if pid in IMG: return IMG[pid]
    try:
        n=int(str(pid)[1:]); cat_idx=(n-1)//10; pos=(n-1)%5
        cat=db.CATEGORIES[cat_idx]
        return IMAGE_POOLS[cat][pos]
    except Exception:
        return 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=900&q=85' 
def money(x): return f'₹{float(x):,.0f}'
app.jinja_env.filters['money']=money

def current_customer():
    cid=session.get('customer_id')
    return db.get_customer(cid) if cid else None

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin sign-in required to access business intelligence.')
            return redirect(url_for('admin_login', next=request.path))
        return view(*args, **kwargs)
    return wrapped

def enrich(df):
    if df is None or len(df)==0: return []
    rows=df.to_dict('records')
    for r in rows:
        r['image']=img_for(r.get('product_id'))
        r['sale_price']=round(float(r['price'])*(1-float(r.get('discount',0))/100),2)
    return rows

def cart_items():
    return session.get('cart',{})

def cart_products():
    result=[]
    for pid,qty in cart_items().items():
        p=db.get_product(pid)
        if p:
            p['qty']=int(qty); p['image']=img_for(pid); p['sale_price']=round(float(p['price'])*(1-float(p['discount'])/100),2)
            result.append(p)
    return result

def cart_total(): return round(sum(p['sale_price']*p['qty'] for p in cart_products()),2)

@app.context_processor
def globals():
    return {'customer':current_customer(),'cart_count':sum(cart_items().values()),'categories':db.CATEGORIES,'category_meta':CATEGORY_META,'admin_logged_in':bool(session.get('admin_logged_in'))}

@app.route('/')
def home():
    products=enrich(db.get_products(sort='Rating: High to Low').head(8))
    stats=db.get_stats();
    return render_template('home.html', products=products, stats=stats)

@app.route('/shop')
def shop():
    cat=request.args.get('category','All'); q=request.args.get('q',''); sort=request.args.get('sort','Featured')
    minp=request.args.get('min',''); maxp=request.args.get('max',''); minr=request.args.get('rating','')
    df=db.get_products(category=cat,search=q,sort=sort)
    if minp: df=df[df.price*(1-df.discount/100)>=float(minp)]
    if maxp: df=df[df.price*(1-df.discount/100)<=float(maxp)]
    if minr: df=df[df.rating>=float(minr)]
    return render_template('shop.html',products=enrich(df),cat=cat,q=q,sort=sort,minp=minp,maxp=maxp,minr=minr)

@app.route('/product/<pid>')
def product(pid):
    p=db.get_product(pid)
    if not p: return redirect(url_for('shop'))
    p['image']=img_for(pid); p['sale_price']=round(p['price']*(1-p['discount']/100),2)
    avg,n=db.get_product_reviews(pid)
    related=enrich(db.get_products(category=p['category']).query("product_id != @pid").head(4))
    return render_template('product.html',p=p,avg=avg or p['rating'],reviews=n,related=related)

@app.route('/cart/add/<pid>', methods=['GET', 'POST'])
def add_cart(pid):
    """Add a product to the session cart.

    Supports both GET and POST so the storefront remains usable even if a
    browser/proxy follows the product link as a normal GET request.
    """
    try:
        p = db.get_product(pid)
        if not p:
            flash('Product not found.')
            return redirect(url_for('shop'))

        cart = dict(session.get('cart') or {})

        if request.method == 'POST':
            raw_qty = request.form.get('qty', '1')
        else:
            raw_qty = request.args.get('qty', '1')

        try:
            qty = max(1, min(int(raw_qty), 99))
        except (TypeError, ValueError):
            qty = 1

        current = cart.get(pid, 0)
        try:
            current = int(current)
        except (TypeError, ValueError):
            current = 0

        cart[pid] = min(current + qty, 99)
        session['cart'] = cart
        session.modified = True
        flash(f"{p['product_name']} added to your cart.")
        return redirect(request.referrer or url_for('cart'))

    except Exception as exc:
        # Keep the storefront usable even if an unexpected cart/session
        # problem occurs. The full exception is visible in Render logs.
        print(f"CART ERROR for {pid}: {exc!r}")
        session['cart'] = {pid: 1}
        session.modified = True
        return redirect(url_for('cart'))

@app.post('/cart/update')
def update_cart():
    c=cart_items()
    for pid in list(c):
        try: q=int(request.form.get(pid,0))
        except: q=0
        if q<=0: c.pop(pid,None)
        else: c[pid]=min(q,99)
    session['cart']=c; return redirect(url_for('cart'))

@app.route('/cart')
def cart(): return render_template('cart.html',products=cart_products(),subtotal=cart_total())

@app.post('/wishlist/toggle/<pid>')
def wishlist(pid):
    w=set(session.get('wishlist',[]));
    if pid in w: w.remove(pid)
    else: w.add(pid)
    session['wishlist']=list(w); return redirect(request.referrer or url_for('shop'))

@app.route('/wishlist')
def wishlist_page():
    ps=[]
    for pid in session.get('wishlist',[]):
        p=db.get_product(pid)
        if p: ps.append(enrich(pd.DataFrame([p]))[0])
    return render_template('wishlist.html',products=ps)

@app.route('/checkout',methods=['GET','POST'])
def checkout():
    customer=current_customer()
    if request.method=='POST':
        if not customer:
            name=request.form.get('name','Guest Customer'); age=int(request.form.get('age',25)); loc=request.form.get('location','Pune'); email=request.form.get('email','guest@example.com')
            cid=db.add_customer(name,age,loc,email); session['customer_id']=cid; customer=db.get_customer(cid)
        if not cart_products(): return redirect(url_for('shop'))
        address=request.form.get('address','Demo delivery address, '+customer['location'])
        method=request.form.get('payment','UPI')
        try:
            latitude=float(request.form.get('latitude')) if request.form.get('latitude') else None
            longitude=float(request.form.get('longitude')) if request.form.get('longitude') else None
        except ValueError:
            latitude=longitude=None
        order_id=db.place_order(customer,[(p,p['qty']) for p in cart_products()],method,address,latitude,longitude)
        session['cart']={}; session['last_order']=order_id
        return redirect(url_for('order_success',order_id=order_id))
    return render_template('checkout.html',products=cart_products(),subtotal=cart_total())

@app.route('/order-success/<order_id>')
def order_success(order_id):
    c=current_customer()
    df=db.get_order(order_id, c['customer_id'] if c else None)
    if df.empty:
        return redirect(url_for('orders'))
    total=float(df.total_amount.sum())
    return render_template('success.html',order_id=order_id,total=total)

@app.route('/track/<order_id>')
def track_order(order_id):
    c=current_customer()
    df=db.get_order(order_id, c['customer_id'] if c else None)
    if df.empty:
        flash('Order not found for this account.')
        return redirect(url_for('orders'))
    row=df.iloc[0].to_dict()
    try:
        placed=pd.to_datetime(row['order_date'])
        age_hours=max(0,(pd.Timestamp.now()-placed).total_seconds()/3600)
    except Exception:
        age_hours=0
    if age_hours >= 72: stage=4
    elif age_hours >= 36: stage=3
    elif age_hours >= 12: stage=2
    elif age_hours >= 2: stage=1
    else: stage=0
    stages=['Placed','Confirmed','Packed','Shipped','Delivered']
    return render_template('track.html',order_id=order_id,row=row,total=float(df.total_amount.sum()),stage=stage,stages=stages)

@app.route('/orders')
def orders():
    c=current_customer(); df=db.get_orders(c['customer_id']) if c else pd.DataFrame()
    groups=[]
    if not df.empty:
        for oid,g in df.groupby('order_id',sort=False):
            groups.append({'id':oid,'date':g.order_date.max(),'total':g.total_amount.sum(),'items':int(g.quantity.sum()),'method':g.payment_method.iloc[0],'status':g.order_status.iloc[0] if 'order_status' in g else 'Placed'})
    return render_template('orders.html',orders=groups)

@app.route('/account')
def account():
    c=current_customer()
    if not c:
        cs=db.get_customers().head(1)
        c=cs.iloc[0].to_dict() if not cs.empty else None
    df=db.get_orders(c['customer_id']) if c else pd.DataFrame()
    total=float(df.total_amount.sum()) if not df.empty else 0
    return render_template('account.html',c=c,total=total,orders=len(df.order_id.unique()) if not df.empty else 0)

@app.post('/demo-login')
def demo_login():
    session['customer_id']=request.form.get('customer_id')
    return redirect(request.referrer or url_for('home'))

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        username=request.form.get('username','').strip()
        password=request.form.get('password','')
        if username==ADMIN_USER and password==ADMIN_PASS:
            session['admin_logged_in']=True
            session['admin_user']=username
            flash('Admin mode enabled. Business intelligence is now unlocked.')
            return redirect(request.args.get('next') or request.form.get('next') or url_for('admin'))
        flash('Invalid admin credentials.')
    return render_template('admin_login.html', next=request.args.get('next',''))

@app.post('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in',None)
    session.pop('admin_user',None)
    flash('Admin session ended.')
    return redirect(url_for('home'))

# ---------------- Business intelligence ----------------
def tx():
    df=db.query('SELECT * FROM transactions')
    if not df.empty:
        df['order_date']=pd.to_datetime(df.order_date); df['sale']=df.total_amount.astype(float)
    return df

@app.route('/insights')
@admin_required
def insights():
    d=tx()
    revenue=float(d.sale.sum()) if not d.empty else 0
    orders=int(d.order_id.nunique()) if not d.empty else 0
    customers=int(d.customer_id.nunique()) if not d.empty else 0
    avg=revenue/orders if orders else 0
    cat=d.groupby('category',as_index=False).sale.sum().sort_values('sale',ascending=False) if not d.empty else pd.DataFrame()
    monthly=d.set_index('order_date').resample('ME').sale.sum().reset_index() if not d.empty else pd.DataFrame()
    top=d.groupby('product_name',as_index=False).agg(sales=('sale','sum'),qty=('quantity','sum')).sort_values('sales',ascending=False).head(6) if not d.empty else pd.DataFrame()
    return render_template('insights.html',revenue=revenue,orders=orders,customers=customers,avg=avg,cat=cat.to_dict('records'),monthly=monthly.to_dict('records'),top=top.to_dict('records'))

@app.route('/insights/customers')
@admin_required
def customer_insights():
    d=tx()
    if d.empty: return render_template('customer_insights.html',rows=[],segments=[])
    c=d.groupby(['customer_id','customer_name','age'],as_index=False).agg(total_spend=('sale','sum'),orders=('order_id','nunique'),avg_order=('sale','mean'),quantity=('quantity','sum'),discount=('discount','mean'),rating=('rating','mean'))
    c['segment_score']=c.total_spend.rank(pct=True)
    c['segment']=pd.cut(c.segment_score,[0,.33,.66,1.0],labels=['Occasional','Regular','Premium'],include_lowest=True).astype(str)
    seg=c.groupby('segment').size().reset_index(name='customers').to_dict('records')
    return render_template('customer_insights.html',rows=c.sort_values('total_spend',ascending=False).head(20).to_dict('records'),segments=seg)

@app.route('/insights/predict',methods=['GET','POST'])
@admin_required
def predict():
    d=tx(); result=None
    if len(d)>=20:
        features=['price','quantity','discount','rating','age']; target='sale'
        x=d[features].fillna(d[features].median()); y=d[target]
        Xtr,Xte,ytr,yte=train_test_split(x,y,test_size=.2,random_state=42)
        model=LinearRegression().fit(Xtr,ytr); pred=model.predict(Xte)
        r2=r2_score(yte,pred); rm=math.sqrt(mean_squared_error(yte,pred))
        if request.method=='POST':
            vals=[float(request.form.get(k,0)) for k in features]
            result=float(model.predict([vals])[0])
    else: r2=rm=0; model=None
    return render_template('predict.html',result=result,r2=r2,rmse=rm)

@app.route('/insights/segments')
@admin_required
def segments():
    d=tx(); data=[]; k=3; inertia=[]; pca_points=[]
    if not d.empty:
        c=d.groupby('customer_id',as_index=False).agg(total_spend=('sale','sum'),orders=('order_id','nunique'),avg_order=('sale','mean'),quantity=('quantity','sum'),discount=('discount','mean'),rating=('rating','mean'),age=('age','first'))
        feats=['total_spend','orders','avg_order','quantity','discount']; X=StandardScaler().fit_transform(c[feats].fillna(c[feats].median()))
        for kk in range(2,7): inertia.append({'k':kk,'inertia':float(KMeans(n_clusters=kk,n_init=10,random_state=42).fit(X).inertia_)})
        km=KMeans(n_clusters=k,n_init=10,random_state=42).fit(X); c['cluster']=km.labels_+1
        profile=c.groupby('cluster')[feats].mean().round(1).reset_index().to_dict('records')
        z=PCA(n_components=2,random_state=42).fit_transform(X)
        pca_points=[{'x':float(a),'y':float(b),'cluster':int(cl)} for (a,b),cl in zip(z,c.cluster)]
        data=c[['customer_id','total_spend','orders','avg_order','cluster']].sort_values('total_spend',ascending=False).head(20).to_dict('records')
    else: profile=[]
    return render_template('segments.html',profile=profile,inertia=inertia,points=pca_points,rows=data)

@app.route('/insights/data')
@admin_required
def data_quality():
    d=tx(); miss=int(d.isna().sum().sum()) if not d.empty else 0; dup=int(d.duplicated().sum()) if not d.empty else 0
    return render_template('data_quality.html',rows=len(d),cols=len(d.columns) if not d.empty else 0,missing=miss,duplicates=dup,columns=list(d.columns) if not d.empty else [])

@app.route('/api/chart/sales')
@admin_required
def sales_api():
    d=tx()
    if d.empty:return jsonify({'labels':[],'values':[]})
    m=d.set_index('order_date').resample('ME').sale.sum()
    return jsonify({'labels':[x.strftime('%b %Y') for x in m.index],'values':[round(float(x),2) for x in m.values]})

@app.route('/admin')
@admin_required
def admin():
    d=tx(); products=db.get_products(); low=products[products.price>0].head(6)
    recent=d.sort_values('order_date',ascending=False).head(8).to_dict('records') if not d.empty else []
    return render_template('admin.html',revenue=float(d.sale.sum()) if not d.empty else 0,orders=int(d.order_id.nunique()) if not d.empty else 0,customers=int(d.customer_id.nunique()) if not d.empty else 0,products=enrich(low),recent=recent)

if __name__=='__main__': app.run(debug=True)
