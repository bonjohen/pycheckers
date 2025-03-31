@echo off
setlocal

:: Function to display usage
:usage
echo Usage: %0 [options]
echo Options:
echo   -a, --all       Run all tests
echo   -u, --unit      Run only unit tests
echo   -i, --ai        Run only AI tests
echo   -g, --ui        Run only UI tests
echo   -c, --coverage  Run tests with coverage report
echo   -h, --help      Display this help message
goto :eof

:: Parse command line arguments
if "%1"=="" (
    echo No option specified, running all tests...
    pytest
    goto :end
)

if "%1"=="-h" goto :usage
if "%1"=="--help" goto :usage

if "%1"=="-a" (
    pytest
    goto :end
)
if "%1"=="--all" (
    pytest
    goto :end
)

if "%1"=="-u" (
    pytest -m "not integration"
    goto :end
)
if "%1"=="--unit" (
    pytest -m "not integration"
    goto :end
)

if "%1"=="-i" (
    pytest tests/ai/
    goto :end
)
if "%1"=="--ai" (
    pytest tests/ai/
    goto :end
)

if "%1"=="-g" (
    pytest tests/ui/
    goto :end
)
if "%1"=="--ui" (
    pytest tests/ui/
    goto :end
)

if "%1"=="-c" (
    pytest --cov=src --cov-report=html
    goto :end
)
if "%1"=="--coverage" (
    pytest --cov=src --cov-report=html
    goto :end
)

:: If we get here, invalid option was provided
echo Invalid option: %1
call :usage

:end
endlocal