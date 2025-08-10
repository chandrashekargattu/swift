const { MongoClient } = require('mongodb');

// Replace this with your actual connection string
const uri = "YOUR_MONGODB_CONNECTION_STRING_HERE";

async function testConnection() {
    const client = new MongoClient(uri);
    
    try {
        // Connect to MongoDB
        await client.connect();
        console.log("✅ Successfully connected to MongoDB!");
        
        // Test database access
        const db = client.db("rideswift_db");
        const collections = await db.listCollections().toArray();
        console.log("📊 Database 'rideswift_db' is accessible");
        console.log(`📁 Collections found: ${collections.length}`);
        
        // Test write operation
        const testCollection = db.collection('test');
        const result = await testCollection.insertOne({ 
            test: true, 
            timestamp: new Date() 
        });
        console.log("✍️  Write test successful!");
        
        // Clean up test data
        await testCollection.deleteOne({ _id: result.insertedId });
        console.log("🧹 Test data cleaned up");
        
    } catch (error) {
        console.error("❌ Connection failed:", error.message);
        console.error("Please check your connection string and network settings");
    } finally {
        // Close connection
        await client.close();
        console.log("👋 Connection closed");
    }
}

console.log("🔍 Testing MongoDB connection...");
console.log("================================");
testConnection();
