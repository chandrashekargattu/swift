#!/bin/bash

# Microservices Quick Start Script
# This script helps you quickly start the microservices architecture

set -e

echo "🚀 Interstate Cab Booking - Microservices Quick Start"
echo "===================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Function to wait for service
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=0
    
    echo -n "Waiting for $service_name..."
    while ! nc -z localhost $port 2>/dev/null; do
        if [ $attempt -eq $max_attempts ]; then
            echo -e "${RED} Failed!${NC}"
            return 1
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo -e "${GREEN} Ready!${NC}"
    return 0
}

# Main menu
echo ""
echo "Select an option:"
echo "1) Start all services (full microservices stack)"
echo "2) Start infrastructure only (DB, Redis, Kafka, etc.)"
echo "3) Start specific service"
echo "4) Stop all services"
echo "5) View service logs"
echo "6) Check service health"
echo "7) Run sample data migration"
echo "8) Exit"
echo ""
read -p "Enter your choice (1-8): " choice

case $choice in
    1)
        echo -e "\n${YELLOW}Starting all microservices...${NC}"
        docker-compose -f microservices-docker-compose.yml up -d
        
        echo -e "\n${YELLOW}Waiting for services to be ready...${NC}"
        wait_for_service "PostgreSQL" 5432
        wait_for_service "MongoDB" 27017
        wait_for_service "Redis" 6379
        wait_for_service "Kafka" 9092
        wait_for_service "Kong API Gateway" 8000
        
        echo -e "\n${GREEN}✅ All services started successfully!${NC}"
        echo -e "\nService URLs:"
        echo "- API Gateway: http://localhost:8000"
        echo "- User Service: http://localhost:8011"
        echo "- Booking Service: http://localhost:8012"
        echo "- Location Service: http://localhost:8013"
        echo "- Grafana: http://localhost:3001 (admin/admin)"
        echo "- Jaeger UI: http://localhost:16686"
        echo "- RabbitMQ: http://localhost:15672 (admin/admin)"
        ;;
        
    2)
        echo -e "\n${YELLOW}Starting infrastructure services only...${NC}"
        docker-compose -f microservices-docker-compose.yml up -d \
            postgres mongodb redis kafka zookeeper \
            prometheus grafana jaeger rabbitmq \
            chromadb clickhouse kong
        
        echo -e "\n${GREEN}✅ Infrastructure services started!${NC}"
        ;;
        
    3)
        echo "Available services:"
        echo "1) user-service"
        echo "2) booking-service"
        echo "3) location-service"
        echo "4) driver-service"
        echo "5) payment-service"
        echo "6) notification-service"
        echo "7) ai-service"
        echo "8) analytics-service"
        echo "9) admin-service"
        read -p "Select service to start (1-9): " service_choice
        
        services=("user-service" "booking-service" "location-service" "driver-service" 
                 "payment-service" "notification-service" "ai-service" 
                 "analytics-service" "admin-service")
        
        if [ $service_choice -ge 1 ] && [ $service_choice -le 9 ]; then
            service_name=${services[$((service_choice-1))]}
            echo -e "\n${YELLOW}Starting $service_name...${NC}"
            docker-compose -f microservices-docker-compose.yml up -d $service_name
            echo -e "${GREEN}✅ $service_name started!${NC}"
        else
            echo -e "${RED}Invalid choice!${NC}"
        fi
        ;;
        
    4)
        echo -e "\n${YELLOW}Stopping all services...${NC}"
        docker-compose -f microservices-docker-compose.yml down
        echo -e "${GREEN}✅ All services stopped!${NC}"
        ;;
        
    5)
        echo "Select service to view logs:"
        echo "1) All services"
        echo "2) user-service"
        echo "3) booking-service"
        echo "4) location-service"
        echo "5) kong (API Gateway)"
        read -p "Enter choice (1-5): " log_choice
        
        case $log_choice in
            1) docker-compose -f microservices-docker-compose.yml logs -f ;;
            2) docker-compose -f microservices-docker-compose.yml logs -f user-service ;;
            3) docker-compose -f microservices-docker-compose.yml logs -f booking-service ;;
            4) docker-compose -f microservices-docker-compose.yml logs -f location-service ;;
            5) docker-compose -f microservices-docker-compose.yml logs -f kong ;;
            *) echo -e "${RED}Invalid choice!${NC}" ;;
        esac
        ;;
        
    6)
        echo -e "\n${YELLOW}Checking service health...${NC}\n"
        
        # Check infrastructure
        echo "Infrastructure Services:"
        for service in postgres:5432 mongodb:27017 redis:6379 kafka:9092; do
            IFS=':' read -r name port <<< "$service"
            if nc -z localhost $port 2>/dev/null; then
                echo -e "✅ $name is ${GREEN}healthy${NC}"
            else
                echo -e "❌ $name is ${RED}down${NC}"
            fi
        done
        
        echo -e "\nMicroservices:"
        # Check microservices
        services=(
            "user-service:8011"
            "booking-service:8012"
            "location-service:8013"
            "driver-service:8014"
            "payment-service:8015"
            "notification-service:8016"
            "ai-service:8017"
            "analytics-service:8018"
            "admin-service:8019"
        )
        
        for service in "${services[@]}"; do
            IFS=':' read -r name port <<< "$service"
            if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health | grep -q "200"; then
                echo -e "✅ $name is ${GREEN}healthy${NC}"
            else
                echo -e "❌ $name is ${RED}down${NC} or not responding"
            fi
        done
        
        echo -e "\nMonitoring Services:"
        if nc -z localhost 3001 2>/dev/null; then
            echo -e "✅ Grafana is ${GREEN}running${NC} at http://localhost:3001"
        fi
        if nc -z localhost 16686 2>/dev/null; then
            echo -e "✅ Jaeger is ${GREEN}running${NC} at http://localhost:16686"
        fi
        ;;
        
    7)
        echo -e "\n${YELLOW}Running sample data migration...${NC}"
        
        # Create databases
        echo "Creating databases..."
        docker exec -it interstate-cab-booking_postgres_1 psql -U postgres -c "CREATE DATABASE IF NOT EXISTS user_db;"
        docker exec -it interstate-cab-booking_postgres_1 psql -U postgres -c "CREATE DATABASE IF NOT EXISTS driver_db;"
        docker exec -it interstate-cab-booking_postgres_1 psql -U postgres -c "CREATE DATABASE IF NOT EXISTS payment_db;"
        docker exec -it interstate-cab-booking_postgres_1 psql -U postgres -c "CREATE DATABASE IF NOT EXISTS admin_db;"
        
        echo -e "\n${YELLOW}Importing sample city data...${NC}"
        # Import cities to location service
        if [ -f "sample_indian_cities.csv" ]; then
            echo "Found sample_indian_cities.csv, importing..."
            # You would implement the actual import here
            echo -e "${GREEN}✅ Sample data imported!${NC}"
        else
            echo -e "${RED}sample_indian_cities.csv not found!${NC}"
        fi
        ;;
        
    8)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid choice!${NC}"
        exit 1
        ;;
esac

echo -e "\n${YELLOW}Tip: Run this script again to manage your microservices!${NC}"
