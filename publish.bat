@echo off

if "%1"=="" goto paramerror

if "%1" NEQ "patch" (
    if "%1" NEQ "minor" (
        goto paramerror
    )
)

bump2version --verbose %1
if errorlevel 1 goto error

rem git push --follow-tags origin master
rem if errorlevel 1 goto error

rmdir /s/q dist
if errorlevel 1 goto error

python setup.py sdist bdist_wheel
if errorlevel 1 goto error

twine upload dist/*
if errorlevel 1 goto error

echo Don't forget to push tags to git.
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
