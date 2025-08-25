"""Quick script to seed cities in the database."""
import asyncio
from app.services.geo import geo_service
from app.core.database import connect_to_mongo, close_mongo_connection


async def main():
    """Seed cities."""
    try:
        # Connect to database
        await connect_to_mongo()
        print("Connected to MongoDB")
        
        # Check current cities
        count = await geo_service.cities_collection.count_documents({})
        print(f"Current cities in database: {count}")
        
        # Seed cities
        if count == 0:
            result = await geo_service.seed_initial_cities()
            print(result)
        else:
            print("Cities already seeded")
            
        # Verify
        new_count = await geo_service.cities_collection.count_documents({})
        print(f"Total cities after seeding: {new_count}")
        
        # List first 5 cities
        cities = []
        async for city in geo_service.cities_collection.find().limit(5):
            cities.append(city["name"])
        print(f"Sample cities: {', '.join(cities)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
