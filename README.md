# ShopSphere — B.Tech E-Commerce & Computational Analytics

A professional Flask + SQLite e-commerce project with a customer storefront and a **private admin intelligence workspace**.

## Run
```bash
pip install -r requirements.txt
python app.py
```
Open: http://127.0.0.1:5000

## Customer experience
- Modern storefront with actual product photography
- Product search, categories, filters and sorting
- Product detail pages, wishlist and cart
- Normal checkout + Place Order flow
- UPI / Card / Cash on Delivery demo payment choices
- Delivery address + interactive OpenStreetMap delivery pin
- **Use my current location** browser-geolocation button
- Click/drag map pin manually when location permission is unavailable
- Order confirmation and order tracking timeline
- Customer account and order history

## Admin experience
Business Intelligence is **not visible to normal customers**. Use:

- Admin Login: `/admin/login`
- Username: `admin`
- Password: `shopsphere@123`

After login, the admin can access:
- Business Intelligence dashboard
- Customer Intelligence
- Sales Prediction / Regression
- Customer Segmentation / PCA / K-Means
- Data Quality Center
- Admin Command Center
- Transaction feed and operational shortcuts

## Academic integration
The customer-facing interface uses normal e-commerce language. The computational-statistics methods are implemented behind the private analytics layer so the project can be explained in the PBL report and viva without exposing academic unit headings to shoppers.

Payments are simulation only. Browser location is used only when the user explicitly clicks the location button and grants permission; otherwise the map can be selected manually.
