"""
Setup script to populate sample data for testing
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from services.database import SessionLocal, AppRegistry, ProductCatalog, ProductType
from decimal import Decimal
import secrets
import hashlib


def setup_sample_data():
    """Create sample app and products"""
    db: Session = SessionLocal()
    
    try:
        print("🚀 Setting up sample data...")
        
        # Check if app already exists
        existing_app = db.query(AppRegistry).filter(
            AppRegistry.app_name == "resumerobotai-web"
        ).first()
        
        if existing_app:
            print("⚠️  App 'resumerobotai-web' already exists. Skipping app creation.")
            app = existing_app
        else:
            # Create sample app
            app_secret = f"sk_anikets_app_{secrets.token_urlsafe(32)}"
            app_secret_hash = hashlib.sha256(app_secret.encode()).hexdigest()
            
            app = AppRegistry(
                app_name="resumerobotai-web",
                app_display_name="Resume Robot AI - Web",
                app_secret_key=app_secret_hash,
                callback_url="http://localhost:8001/payment/webhook",
                success_redirect_base="http://localhost:5173/payment/success",
                cancel_redirect_base="http://localhost:5173/payment/cancel",
                credits_enabled=True,
                subscription_enabled=True,
                currency="USD",
                is_active=True,
                extra_data={"features": ["credits", "subscriptions", "refunds"], "version": "1.0"}
            )
            
            db.add(app)
            db.commit()  # Commit app creation separately
            
            print(f"✅ Created app: {app.app_name}")
            print(f"   App Secret: {app_secret}")
        
        # Create sample products
        products = [
            {
                "product_id": "starterr",
                "product_name": "25 Credits",
                "description": "Perfect for trying out",
                "price": Decimal("2.99"),
                "credits_granted": 25,
                "is_popular": False,
                "display_order": 1
            },
            {
                "product_id": "pro",
                "product_name": "60 Credits",
                "description": "Most popular package",
                "price": Decimal("5.99"),
                "credits_granted": 60,
                "is_popular": True,
                "display_order": 2
            },
            {
                "product_id": "popular",
                "product_name": "120 Credits",
                "description": "Best value for money",
                "price": Decimal("9.99"),
                "credits_granted": 120,
                "is_popular": False,
                "display_order": 3
            },
            {
                "product_id": "credits_500",
                "product_name": "500 Credits",
                "description": "For power users",
                "price": Decimal("199.99"),
                "credits_granted": 500,
                "is_popular": False,
                "display_order": 4
            },
            {
                "product_id": "sub_monthly",
                "product_name": "Pro Monthly",
                "description": "Unlimited resumes + premium features",
                "price": Decimal("9.99"),
                "credits_granted": 0,
                "product_type": ProductType.SUBSCRIPTION,
                "is_popular": False,
                "display_order": 5
            },
            {
                "product_id": "sub_yearly",
                "product_name": "Pro Yearly",
                "description": "Unlimited resumes + premium features",
                "price": Decimal("49.99"),
                "credits_granted": 0,
                "product_type": ProductType.SUBSCRIPTION,
                "is_popular": False,
                "display_order": 5
            }
        ]
        
        created_count = 0
        for product_data in products:
            # Check if product exists
            existing_product = db.query(ProductCatalog).filter(
                ProductCatalog.app_name == app.app_name,
                ProductCatalog.product_id == product_data["product_id"]
            ).first()
            
            if not existing_product:
                # Set default product_type if not provided
                if "product_type" not in product_data:
                    product_data["product_type"] = ProductType.ONE_TIME
                
                product = ProductCatalog(
                    app_name=app.app_name,
                    currency="USD",
                    is_active=True,
                    **product_data
                )
                db.add(product)
                created_count += 1
                print(f"✅ Created product: {product_data['product_name']}")
        
        if created_count > 0:
            db.commit()
            print(f"\n🎉 Setup complete! Created {created_count} products.")
        else:
            print(f"\n⚠️  All products already exist. No new products created.")
        
        print("\n📋 Summary:")
        print(f"   App Name: {app.app_name}")
        print(f"   Display Name: {app.app_display_name}")
        print(f"   Callback URL: {app.callback_url}")
        print(f"   Credits Enabled: {app.credits_enabled}")
        print(f"   Subscription Enabled: {app.subscription_enabled}")
        
        # Show products
        all_products = db.query(ProductCatalog).filter(
            ProductCatalog.app_name == app.app_name
        ).order_by(ProductCatalog.display_order).all()
        
        print(f"\n📦 Products ({len(all_products)}):")
        for p in all_products:
            print(f"   - {p.product_name}: ${p.price} ({p.credits_granted} credits)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    setup_sample_data()

