#!/bin/bash

# Comprehensive test runner script for Andamios ORM
# This script runs all tests with 100% coverage requirements

set -e  # Exit on any error

echo "🧪 Andamios ORM Test Suite"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COVERAGE_THRESHOLD=100
PYTEST_ARGS=""
RUN_INTEGRATION=false
VERBOSE=false
PARALLEL=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            PYTEST_ARGS="$PYTEST_ARGS -v"
            shift
            ;;
        -i|--integration)
            RUN_INTEGRATION=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -f|--fast)
            PYTEST_ARGS="$PYTEST_ARGS -x"
            shift
            ;;
        --no-cov)
            PYTEST_ARGS="$PYTEST_ARGS --no-cov"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose     Verbose output"
            echo "  -i, --integration Run integration tests"
            echo "  -p, --parallel    Run tests in parallel"
            echo "  -f, --fast        Fail fast on first error"
            echo "  --no-cov          Skip coverage reporting"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Change to project root
cd "$PROJECT_ROOT"

echo -e "${BLUE}Project root: $PROJECT_ROOT${NC}"

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found. Please install it with: pip install pytest${NC}"
    exit 1
fi

# Check if coverage is available
if ! command -v coverage &> /dev/null && [[ "$PYTEST_ARGS" != *"--no-cov"* ]]; then
    echo -e "${RED}❌ coverage not found. Please install it with: pip install coverage${NC}"
    exit 1
fi

# Clean previous coverage data
if [[ "$PYTEST_ARGS" != *"--no-cov"* ]]; then
    echo -e "${YELLOW}🧹 Cleaning previous coverage data...${NC}"
    coverage erase || true
    rm -rf htmlcov/ || true
    rm -f coverage.xml coverage.json || true
fi

# Determine test markers
TEST_MARKERS=""
if [[ "$RUN_INTEGRATION" == true ]]; then
    TEST_MARKERS="-m 'unit or integration'"
else
    TEST_MARKERS="-m 'unit'"
fi

# Add parallel execution if requested
if [[ "$PARALLEL" == true ]]; then
    PYTEST_ARGS="$PYTEST_ARGS -n auto"
fi

# Run tests
echo -e "${BLUE}🚀 Running tests...${NC}"
echo "Command: pytest $PYTEST_ARGS $TEST_MARKERS"
echo ""

# Build the full pytest command
FULL_COMMAND="pytest $PYTEST_ARGS $TEST_MARKERS"

# Run the tests
if eval $FULL_COMMAND; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    TEST_SUCCESS=true
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    TEST_SUCCESS=false
fi

# Generate coverage reports if coverage was run
if [[ "$PYTEST_ARGS" != *"--no-cov"* ]] && [[ "$TEST_SUCCESS" == true ]]; then
    echo ""
    echo -e "${BLUE}📊 Generating coverage reports...${NC}"
    
    # Generate HTML report
    if coverage html; then
        echo -e "${GREEN}✅ HTML coverage report generated: htmlcov/index.html${NC}"
    else
        echo -e "${YELLOW}⚠️  Failed to generate HTML coverage report${NC}"
    fi
    
    # Generate XML report (for CI/CD)
    if coverage xml; then
        echo -e "${GREEN}✅ XML coverage report generated: coverage.xml${NC}"
    else
        echo -e "${YELLOW}⚠️  Failed to generate XML coverage report${NC}"
    fi
    
    # Generate JSON report
    if coverage json; then
        echo -e "${GREEN}✅ JSON coverage report generated: coverage.json${NC}"
    else
        echo -e "${YELLOW}⚠️  Failed to generate JSON coverage report${NC}"
    fi
    
    # Show coverage summary
    echo ""
    echo -e "${BLUE}📈 Coverage Summary:${NC}"
    coverage report
    
    # Check coverage threshold
    COVERAGE_PERCENTAGE=$(coverage report --format=total)
    if (( $(echo "$COVERAGE_PERCENTAGE >= $COVERAGE_THRESHOLD" | bc -l) )); then
        echo -e "${GREEN}✅ Coverage threshold met: ${COVERAGE_PERCENTAGE}% >= ${COVERAGE_THRESHOLD}%${NC}"
    else
        echo -e "${RED}❌ Coverage threshold not met: ${COVERAGE_PERCENTAGE}% < ${COVERAGE_THRESHOLD}%${NC}"
        TEST_SUCCESS=false
    fi
fi

# Summary
echo ""
echo "=========================="
if [[ "$TEST_SUCCESS" == true ]]; then
    echo -e "${GREEN}🎉 Test suite completed successfully!${NC}"
    
    if [[ "$PYTEST_ARGS" != *"--no-cov"* ]]; then
        echo -e "${GREEN}📊 Coverage reports available in htmlcov/ directory${NC}"
    fi
    
    exit 0
else
    echo -e "${RED}💥 Test suite failed!${NC}"
    echo -e "${YELLOW}Please fix the failing tests and ensure 100% coverage.${NC}"
    exit 1
fi