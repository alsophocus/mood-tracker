#!/bin/bash

echo "🧪 Running Mood Tracker Test Suite"
echo "=================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r requirements.txt

# Run tests with coverage
echo "🚀 Running tests..."
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo "📊 Coverage report generated in htmlcov/index.html"
else
    echo ""
    echo "❌ Some tests failed!"
    exit 1
fi

echo ""
echo "🔍 Test Categories Covered:"
echo "  • Authentication & OAuth"
echo "  • Database Operations"
echo "  • Mood Tracking Logic"
echo "  • Analytics Calculations"
echo "  • API Endpoints"
echo "  • Security Validations"
echo ""
echo "📈 View detailed coverage: open htmlcov/index.html"
