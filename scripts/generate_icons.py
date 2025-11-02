# Create a simple script to generate placeholder icons
# Run: python scripts/generate_icons.py

from PIL import Image, ImageDraw, ImageFont

# Create 192x192 icon
img192 = Image.new('RGB', (192, 192), color='#0ea5e9')
draw = ImageDraw.Draw(img192)
draw.rectangle([10, 10, 182, 182], outline='white', width=5)
draw.text((96, 96), 'RAG', fill='white', anchor='mm')
img192.save('frontend/public/icon-192.png')

# Create 512x512 icon
img512 = Image.new('RGB', (512, 512), color='#0ea5e9')
draw = ImageDraw.Draw(img512)
draw.rectangle([20, 20, 492, 492], outline='white', width=15)
draw.text((256, 256), 'RAG', fill='white', anchor='mm')
img512.save('frontend/public/icon-512.png')

print('Icons generated successfully!')
