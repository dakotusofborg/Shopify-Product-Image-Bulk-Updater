# Shopify Product Image Bulk Updater

A Python script that automatically updates Shopify product images from a Google Drive folder, matching images to products by SKU.

## Overview

This tool reads image files from a Google Drive folder organized by product SKU, finds matching products in your Shopify store, and uploads the images as product gallery images. Perfect for bulk image management across hundreds of products.

**Features:**
- Recursive folder scanning on Google Drive
- SKU-based product matching
- Batch image upload to Shopify
- Rate limit handling with automatic retries
- Progress tracking and detailed logging

## Prerequisites

- Python 3.10+
- A Shopify store with products that have SKUs
- A Google Cloud project with Drive API enabled
- Google Drive folder containing product images organized by SKU

## Installation

### 1. Clone or Download the Script

```bash
git clone <repository-url>
cd shopify-image-updater
```

### 2. Install Python Dependencies

```bash
pip3 install google-auth google-auth-oauthlib google-cloud-storage google-api-python-client requests
```

### 3. Set Up Shopify API Access

1. Go to your Shopify admin dashboard
2. Navigate to **Settings > Apps and integrations > Develop apps**
3. Click **Create an app** and name it "Image Updater"
4. Go to **Configuration** tab
5. Under **Admin API scopes**, enable:
   - `read_products`
   - `write_products`
6. Click **Save** and **Install app**
7. Go to **API credentials** tab and copy your **Access Token**
8. Copy your store name (the part before `.myshopify.com` in your admin URL)

### 4. Set Up Google Cloud & Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Go to **APIs & Services > Library**
4. Search for and enable **Google Drive API**
5. Go to **Credentials > Create Credentials > Service Account**
6. Name it "Shopify Image Updater" and create it
7. On the service account page, go to **Keys > Add Key > Create new key**
8. Choose **JSON** format and download the file
9. Rename the downloaded file to `credentials.json` and save it in your script directory
10. Copy the service account email from the JSON file
11. Share your Google Drive folder with that email (grant **Editor** access)

### 5. Configure the Script

Open `shopify-updater.py` and update these lines:

```python
SHOPIFY_STORE = "your-store-name.myshopify.com"
SHOPIFY_ACCESS_TOKEN = "your-access-token-here"
GDRIVE_FOLDER_ID = "your-google-drive-folder-id"
```

To get your Google Drive folder ID, open the folder in a browser—the URL will be:
```
https://drive.google.com/drive/folders/FOLDER_ID_HERE
```

## File Structure

Your Google Drive folder should be organized like this:

```
Product Images/
├── [SKU]/
│   ├── version/
│   │   ├── SKU_transparent_box.png
│   │   ├── SKU_pieces.png
│   │   └── SKU_gamesetup.png
│   └── other_subfolder/
│       └── SKU_variation.jpg
├── [ANOTHER_SKU]/
│   ├── version/
│   │   └── ANOTHER_SKU_transparent_box.png
```

**Important:** Image files must start with the product SKU followed by an underscore:
- ✅ `OMD-O_transparent_box.png`
- ✅ `WG5_gamesetup_neutral.png`
- ❌ `transparent_box.png` (will be skipped)

## Usage

Run the script:

```bash
python3 shopify-updater.py
```

The script will:
1. Authenticate with Google Drive
2. Recursively scan your folder for image files
3. Extract SKUs from filenames
4. Fetch all products from your Shopify store
5. Match images to products by exact SKU match
6. Upload matched images to Shopify
7. Display progress and a summary

### Example Output

```
🔄 Starting Shopify Product Image Update...
📂 Fetching files from GDrive...
✅ Found 3657 image files
🔍 Processing: OMD-O_transparent_box.png (SKU: OMD-O)
   ✓ Found product: 100 Glow Skulls (SKU: OMD-O)
   ✅ Updated successfully
...
✨ Complete! Updated: 342, Skipped: 3315
```

## How It Works

### SKU Extraction

Filenames are parsed by splitting on the first underscore. For `OMD-O_transparent_box.png`, the SKU is `OMD-O`.

### Product Matching

The script fetches all products from your Shopify store and searches for an exact SKU match in each product's variants. This ensures accurate product identification.

### Image Upload

Matched images are uploaded as new gallery images to the product (not replacing existing ones). Images are referenced from Google Drive using public URLs.

### Rate Limiting

The script respects both Shopify and Google API rate limits:
- Automatic retry on 429 rate limit errors
- 0.5 second delay between requests
- 2 second wait on rate limit hits

## Troubleshooting

### "No module named 'google.auth'"

Install missing dependencies:
```bash
pip3 install --upgrade google-auth-oauthlib google-api-python-client
```

### "403 - This action requires merchant approval for read_products scope"

You need to approve the API scopes in Shopify:
1. Go to your app configuration in Shopify admin
2. Ensure `read_products` and `write_products` are enabled
3. Save and reinstall the app

### "No product with SKU: XYZ"

The SKU doesn't exist in your Shopify store. Options:
- Verify the SKU is correct in Shopify
- Check that image filename starts with the exact SKU
- Remember: SKUs are case-sensitive

### Script takes a long time

The script processes each image sequentially with rate limiting to avoid API throttling. With thousands of images, this is normal. The status updates will show progress.

### Images added to wrong product

Ensure your Shopify SKUs are unique. If two products share the same SKU, images will be added to whichever is fetched first.

## Performance Notes

- **400 products with multiple images each:** ~15-30 minutes depending on API response times
- **3600+ images:** Expect 1-2 hours for full processing
- The script processes images sequentially to maintain API compliance

## API Documentation

- [Shopify Admin API](https://shopify.dev/docs/admin-api)
- [Google Drive API](https://developers.google.com/drive/api)

## License

MIT

## Support

For issues or questions, check the troubleshooting section or review the script output for specific error messages.# Shopify-Product-Image-Bulk-Updater
A Python script that automatically updates Shopify product images from a Google Drive folder, matching images to products by SKU.
