import os
import json
import requests
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time

# Configuration
SHOPIFY_STORE = "your-store-name.myshopify.com"
SHOPIFY_ACCESS_TOKEN = "your-access-token"
GDRIVE_FOLDER_ID = "1tox-3H8doyjlhF_cIl-cWd64VCp8AYlN"

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_gdrive():
    """Authenticate with GDrive using service account"""
    try:
        creds = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"❌ GDrive auth failed: {e}")
        return None

def get_gdrive_files(folder_id, service):
    """Recursively get all files from GDrive folder"""
    files = []
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name, mimeType)', pageSize=1000).execute()
        items = results.get('files', [])
        
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                files.extend(get_gdrive_files(item['id'], service))
            else:
                files.append(item)
    except Exception as e:
        print(f"Error reading GDrive: {e}")
    
    return files

def parse_sku_from_filename(filename):
    """Extract SKU from filename"""
    name = filename.split('_')[0]
    return name.strip()

def get_shopify_product_by_sku(sku):
    """Search for product by exact SKU match - fetch all pages"""
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/products.json"
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}
    
    try:
        all_products = []
        limit = 250
        last_id = None
        
        while True:
            params = {"fields": "id,title,variants", "limit": limit}
            if last_id:
                params["since_id"] = last_id
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 429:
                print(f"   ⏳ Rate limited, waiting...")
                time.sleep(2)
                continue
            
            if response.status_code != 200:
                print(f"   Error {response.status_code}: {response.text}")
                return None
            
            products = response.json().get('products', [])
            if not products:
                break
            
            all_products.extend(products)
            last_id = products[-1]['id']
            time.sleep(0.5)  # Rate limit safety
        
        # Search for exact SKU match across all products
        for product in all_products:
            for variant in product.get('variants', []):
                if variant.get('sku', '').strip() == sku:
                    print(f"   ✓ Found product: {product['title']} (SKU: {sku})")
                    return product
        
        print(f"   ⏭️  No product with SKU: {sku}")
        return None
    
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_gdrive_file_url(file_id):
    """Generate shareable GDrive URL for image"""
    return f"https://drive.google.com/uc?export=view&id={file_id}"

def update_product_image(product_id, image_url):
    """Update product image in Shopify"""
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/products/{product_id}/images.json"
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}
    
    payload = {"image": {"src": image_url}}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"      Error {response.status_code}")
            return False
    except Exception as e:
        print(f"Error updating image: {e}")
        return False

def main():
    """Main execution"""
    print("🔄 Starting Shopify Product Image Update...")
    
    # Authenticate with GDrive
    service = authenticate_gdrive()
    if not service:
        return
    
    # Get all image files from GDrive
    print("📂 Fetching files from GDrive...")
    files = get_gdrive_files(GDRIVE_FOLDER_ID, service)
    print(f"✅ Found {len(files)} image files\n")
    
    # Process each file
    updated = 0
    skipped = 0
    
    for file in files:
        # Skip non-image files
        if not file['name'].lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            continue
        
        sku = parse_sku_from_filename(file['name'])
        print(f"🔍 Processing: {file['name']} (SKU: {sku})")
        
        # Find product in Shopify
        product = get_shopify_product_by_sku(sku)
        if not product:
            skipped += 1
            time.sleep(0.5)
            continue
        
        # Update image
        image_url = get_gdrive_file_url(file['id'])
        if update_product_image(product['id'], image_url):
            print(f"   ✅ Updated successfully\n")
            updated += 1
        else:
            print(f"   ❌ Update failed\n")
            skipped += 1
        
        # Respect API rate limits
        time.sleep(0.5)
    
    print(f"✨ Complete! Updated: {updated}, Skipped: {skipped}")

if __name__ == "__main__":
    main()
