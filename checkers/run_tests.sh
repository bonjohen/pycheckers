#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -a, --all       Run all tests"
    echo "  -u, --unit      Run only unit tests"
    echo "  -i, --ai        Run only AI tests"
    echo "  -g, --ui        Run only UI tests"
    echo "  -c, --coverage  Run tests with coverage report"
    echo "  -h, --help      Display this help message"
}

# Parse command line arguments
case "$1" in
    -a|--all)
        pytest
        ;;
    -u|--unit)
        pytest -m "not integration"
        ;;
    -i|--ai)
        pytest tests/ai/
        ;;
    -g|--ui)
        pytest tests/ui/
        ;;
    -c|--coverage)
        pytest --cov=src --cov-report=html
        ;;
    -h|--help)
        usage
        ;;
    *)
        echo "No option specified, running all tests..."
        pytest
        ;;
esac