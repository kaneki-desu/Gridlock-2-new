#!/bin/bash
# TrafficTwin AI - Complete Setup Script
# Automates backend and frontend setup

set -e

echo "================================================"
echo "TrafficTwin AI - Complete Setup"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm found${NC}"

if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠ PostgreSQL client not found. Please install PostgreSQL first.${NC}"
fi

# Setup Backend
echo -e "\n${YELLOW}Setting up Backend...${NC}"

cd backend

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit backend/.env with your PostgreSQL credentials${NC}"
fi

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Setup Frontend
echo -e "\n${YELLOW}Setting up Frontend...${NC}"

cd ../frontend

# Install Node dependencies
echo "Installing Node dependencies..."
npm install

# Create .env.local file if it doesn't exist
if [ ! -f .env.local ]; then
    echo "Creating .env.local file from template..."
    cp .env.example .env.local
fi

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Summary
echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}================================================${NC}"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Set up PostgreSQL database:"
echo "   createdb traffic_twin_ai"
echo "   psql traffic_twin_ai < ../backend/schema.sql"
echo ""
echo "2. Edit backend/.env with your database URL"
echo ""
echo "3. Train ML models (from backend directory):"
echo "   python train_model.py --data-path /path/to/data.csv"
echo ""
echo "4. Build FAISS index (from backend directory):"
echo "   python build_rag_index.py --data-path /path/to/data.csv"
echo ""
echo "5. Start backend (from backend directory):"
echo "   python app.py"
echo ""
echo "6. Start frontend (from frontend directory):"
echo "   npm run dev"
echo ""
echo "7. Access the application:"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Frontend: http://localhost:3000"
