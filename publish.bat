@echo off

if "%1"=="" goto paramerror

if "%1" NEQ "patch" (
    if "%1" NEQ "minor" (
        goto paramerror
    )
)

bump2version --verbose %1
if errorlevel 1 goto error

git push --follow-tags origin
if errorlevel 1 goto error

rmdir /s/q dist
if errorlevel 1 goto error

python -m unittest
if errorlevel 1 goto error

python setup.py sdist bdist_wheel
if errorlevel 1 goto error

twine upload dist/*
if errorlevel 1 goto error

goto end

:PARAMERROR
echo.
echo Error in input parameters.
goto end

:ERROR
echo.
echo There was an error publishing the package.
goto end

:END
echo Finished
