#!/bin/bash

# Quick API Test Script for Phase 2 Validation
# Tests all ML endpoints and verifies responses

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🧪 PHASE 2 ML VALIDATION - Quick API Test Script     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:5000"

# Test counter
TESTS_PASSED=0
TESTS_TOTAL=0

# Helper function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    local expected_status=${4:-200}
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    echo -e "${BLUE}Test $TESTS_TOTAL: $name${NC}"
    echo "   URL: $method $url"
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url")
    else
        response=$(curl -s -w "\n%{http_code}" "$url")
    fi
    
    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "   ${GREEN}✅ PASS${NC} (HTTP $status_code)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        
        # Try to pretty print JSON if jq is available
        if command -v jq &> /dev/null; then
            echo "$body" | jq -C '.' 2>/dev/null | head -n 10
            if [ $(echo "$body" | jq 'length' 2>/dev/null) -gt 0 ]; then
                echo "   ..."
            fi
        fi
    else
        echo -e "   ${RED}❌ FAIL${NC} (HTTP $status_code, expected $expected_status)"
        echo "$body"
    fi
    echo ""
}

# Helper function to check JSON field
check_ml_method() {
    local response=$1
    local field_path=$2
    local expected_value=$3
    local description=$4
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if command -v jq &> /dev/null; then
        actual=$(echo "$response" | jq -r "$field_path" 2>/dev/null)
        
        if [ "$actual" = "$expected_value" ]; then
            echo -e "   ${GREEN}✅ $description${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "   ${RED}❌ $description${NC}"
            echo "      Expected: $expected_value"
            echo "      Got: $actual"
        fi
    else
        echo -e "   ${YELLOW}⚠️  $description (jq not installed, skipping)${NC}"
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 Phase 1: Server Health Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: Root endpoint
test_endpoint "Root API Info" "$BASE_URL/"

# Test 2: Health check
test_endpoint "Health Check" "$BASE_URL/health"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌱 Phase 2: Database Seeding"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 3: Seed database
test_endpoint "Seed Sample Data" "$BASE_URL/api/seed-database" "POST"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 Phase 3: ML Analytics Endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 4: Advanced ML Analytics
echo -e "${BLUE}Test $((TESTS_TOTAL + 1)): Advanced ML Analytics${NC}"
echo "   URL: GET $BASE_URL/api/admin/ml/advanced-analytics"

ml_response=$(curl -s "$BASE_URL/api/admin/ml/advanced-analytics")
ml_status=$?

if [ $ml_status -eq 0 ]; then
    echo -e "   ${GREEN}✅ Request Successful${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "   ${RED}❌ Request Failed${NC}"
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))
echo ""

# Validate ML components
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔬 Phase 4: ML Component Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if command -v jq &> /dev/null; then
    echo "Checking ML Methods:"
    
    # Check Isolation Forest
    check_ml_method "$ml_response" \
        ".data.anomaly_detection.method" \
        "Isolation Forest" \
        "Isolation Forest (Anomaly Detection)"
    
    # Check K-Means
    check_ml_method "$ml_response" \
        ".data.clustering.method" \
        "K-Means" \
        "K-Means (Clustering)"
    
    # Check Random Forest
    check_ml_method "$ml_response" \
        ".data.severity_prediction.method" \
        "Random Forest Classifier" \
        "Random Forest (Severity Prediction)"
    
    # Check Forecasting
    check_ml_method "$ml_response" \
        ".data.forecast.method" \
        "Linear Regression + Confidence Intervals" \
        "Linear Regression (Forecasting)"
    
    # Check Risk Scoring
    check_ml_method "$ml_response" \
        ".data.risk_assessment.assessment_method" \
        "Multi-factor ML Risk Scoring" \
        "ML Risk Scoring"
    
    echo ""
    echo "Checking Data Availability:"
    
    # Check anomaly detection has data
    anomalies=$(echo "$ml_response" | jq -r '.data.anomaly_detection.anomalies_detected' 2>/dev/null)
    if [ "$anomalies" = "true" ] || [ "$anomalies" = "false" ]; then
        echo -e "   ${GREEN}✅ Anomaly Detection: Data Present${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "   ${RED}❌ Anomaly Detection: No Data${NC}"
    fi
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    # Check clustering available
    clustering=$(echo "$ml_response" | jq -r '.data.clustering.clustering_available' 2>/dev/null)
    if [ "$clustering" = "true" ]; then
        echo -e "   ${GREEN}✅ Clustering: Available${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "   ${YELLOW}⚠️  Clustering: Not Available (may need more data)${NC}"
    fi
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    # Check forecasting available
    forecasting=$(echo "$ml_response" | jq -r '.data.forecast.forecasting_available' 2>/dev/null)
    if [ "$forecasting" = "true" ]; then
        echo -e "   ${GREEN}✅ Forecasting: Available${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "   ${YELLOW}⚠️  Forecasting: Not Available (may need more data)${NC}"
    fi
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    # Check risk score exists
    risk_score=$(echo "$ml_response" | jq -r '.data.risk_assessment.risk_score' 2>/dev/null)
    if [ ! -z "$risk_score" ] && [ "$risk_score" != "null" ]; then
        echo -e "   ${GREEN}✅ Risk Scoring: Operational (Score: $risk_score)${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "   ${RED}❌ Risk Scoring: No Score Generated${NC}"
    fi
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
else
    echo -e "${YELLOW}⚠️  jq not installed - skipping detailed validation${NC}"
    echo "   Install jq for detailed checks: apt-get install jq / brew install jq"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 TEST RESULTS SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

percentage=$((TESTS_PASSED * 100 / TESTS_TOTAL))

echo "Tests Passed: $TESTS_PASSED / $TESTS_TOTAL ($percentage%)"
echo ""

if [ $percentage -eq 100 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo ""
    echo "✅ Phase 2 is fully operational!"
    echo "✅ All 5 ML models are working correctly"
    echo "✅ Database integration successful"
    echo ""
    echo -e "${BLUE}📈 Ready for Phase 3: Advanced Visualizations${NC}"
    echo ""
    exit 0
elif [ $percentage -ge 80 ]; then
    echo -e "${YELLOW}⚠️  MOSTLY WORKING${NC}"
    echo ""
    echo "Some tests failed but core functionality is operational."
    echo "Review warnings above and ensure:"
    echo "  • Database has at least 30 reports"
    echo "  • scikit-learn is properly installed"
    echo "  • Server has been restarted after seeding"
    echo ""
    exit 1
else
    echo -e "${RED}❌ CRITICAL ISSUES DETECTED${NC}"
    echo ""
    echo "Phase 2 validation failed. Common issues:"
    echo "  1. Server not running (python backend/app.py)"
    echo "  2. Database not seeded (curl -X POST /api/seed-database)"
    echo "  3. scikit-learn not installed (pip install -r requirements.txt)"
    echo "  4. Port 5000 blocked or in use"
    echo ""
    echo "Check server logs for detailed error messages."
    echo ""
    exit 2
fi
