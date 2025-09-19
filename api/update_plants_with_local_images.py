#!/usr/bin/env python3
"""
Script pour mettre à jour les plantes avec les images locales du projet
"""

import sys
sys.path.append('/app')

import base64
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Models
from models.plant import Plant

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_nSZE6jjB7cgm@ep-spring-bonus-agd7s9t1-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def image_to_base64(image_path):
    """Convert image file to base64 string"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            # Detect image type
            ext = image_path.split('.')[-1].lower()
            mime_type = f"image/{ext}" if ext in ['jpg', 'jpeg', 'png', 'gif'] else "image/jpeg"
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"   ⚠️ Error converting {image_path}: {e}")
        return None


def update_plants_with_local_images():
    """Update existing plants with local project images"""
    db = SessionLocal()

    try:
        print('🖼️ Updating plants with local project images...')

        # Get all existing plants
        plants = db.query(Plant).all()

        if not plants:
            print('   ⚠️ No plants found in database')
            return

        print(f'   Found {len(plants)} plants:')
        for plant in plants:
            print(f'     - "{plant.name}" (ID: {plant.id})')

        # Local images in the project (accessible from Docker container)
        available_images = [
            '/app/assets/plants/11471877.png',  # Snake Plant
            '/app/assets/plants/11471878.png',  # Bird of Paradise
            '/app/assets/plants/b928e83d-d68e-4be2-af5d-53a37c589f92.jpg',  # Monstera
            '/app/assets/plants/fe70ee54-62c7-49ff-a1cc-ed1cbf7b0092.jpg',  # Pothos
            '/app/assets/plants/c30fa0f2-f6f5-49ae-831d-db6f2e101156.jpg',  # Philodendron
            '/app/assets/plants/f7250849-a325-4d8f-aff0-6938a440c4ab.jpg',  # Palm
            '/app/assets/plants/3ec6b4c8-f0bd-44e5-929e-3000b28e891c.jpg',  # Indoor Palm
            '/app/assets/plants/plante-de-palmier-en-pot.jpg'  # Yucca/Dracaena
        ]

        updated_count = 0

        # Assign images to plants (cycling through available images)
        for i, plant in enumerate(plants):
            image_path = available_images[i % len(available_images)]

            # Convert image to base64
            base64_image = image_to_base64(image_path)

            if base64_image:
                plant.photo_base64 = base64_image
                updated_count += 1
                image_name = image_path.split('/')[-1]
                print(f'   ✅ Updated "{plant.name}" with {image_name}')
            else:
                print(f'   ❌ Failed to update "{plant.name}"')

        if updated_count > 0:
            db.commit()
            print(f'\n🎉 Successfully updated {updated_count} plants with beautiful images!')
            print('\n🌿 Your plants now have real photos:')
            print('   - Snake Plant (Sansevieria)')
            print('   - Bird of Paradise (Tropical)')
            print('   - Monstera Deliciosa (Split leaves)')
            print('   - Pothos (Round leaves)')
            print('   - Philodendron varieties')
            print('   - Palm trees')
            print('   - And more beautiful plants!')
            print('\n📱 Check your mobile app to see the updated plant images!')
        else:
            print('⚠️ No plants were updated')

    except Exception as e:
        db.rollback()
        print(f'❌ Error updating images: {e}')
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_plants_with_local_images()