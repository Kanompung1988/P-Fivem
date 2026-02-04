#!/bin/bash

# Test Runner - รันทดสอบทุก test
# Usage: ./run_tests.sh [--with-api]

echo " Running Test Suite for Seoulholic AI Bot"
echo "============================================="
echo ""

# Check if --with-api flag is present
WITH_API=false
if [[ "$1" == "--with-api" ]]; then
    WITH_API=true
fi

# Counter
TOTAL_TESTS=0
PASSED_TESTS=0

# Test 1: Input Guard (no API needed)
echo "📋 Test 1: Input Guard System"
echo "------------------------------"
python tests/test_input_guard.py
if [ $? -eq 0 ]; then
    echo " Input Guard test passed"
    ((PASSED_TESTS++))
else
    echo " Input Guard test failed"
fi
((TOTAL_TESTS++))
echo ""

# Test 2: Integration (needs API key)
if [ "$WITH_API" = true ]; then
    echo "📋 Test 2: Integration Test (AI + Guard)"
    echo "-----------------------------------------"
    
    # Check for API key
    if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null && ! grep -q "sk-your" .env; then
        python tests/test_integration.py
        if [ $? -eq 0 ]; then
            echo " Integration test passed"
            ((PASSED_TESTS++))
        else
            echo " Integration test failed"
        fi
        ((TOTAL_TESTS++))
    else
        echo "  Skipping - OPENAI_API_KEY not configured in .env"
        echo "   To run: Add your API key to .env and use --with-api flag"
    fi
    echo ""
    
    # Test 3: Quick Test (needs API)
    echo "📋 Test 3: Quick Test (9 questions)"
    echo "------------------------------------"
    if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null && ! grep -q "sk-your" .env; then
        python tests/quick_test.py
        if [ $? -eq 0 ]; then
            echo " Quick test passed"
            ((PASSED_TESTS++))
        else
            echo " Quick test failed"
        fi
        ((TOTAL_TESTS++))
    else
        echo "  Skipping - OPENAI_API_KEY not configured"
    fi
    echo ""
else
    echo "  Skipping API tests (use --with-api to run)"
    echo ""
fi

# Summary
echo "============================================="
echo " Test Summary"
echo "============================================="
echo "Total Tests Run: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $((TOTAL_TESTS - PASSED_TESTS))"

if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "Pass Rate: ${PASS_RATE}%"
    
    if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
        echo ""
        echo " All tests passed! "
        exit 0
    else
        echo ""
        echo " Some tests failed"
        exit 1
    fi
else
    echo ""
    echo "  No tests were run"
    echo "Use --with-api flag to run API-dependent tests"
    exit 0
fi
