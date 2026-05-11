@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
if errorlevel 1 exit /b %errorlevel%
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
set "CARGO_TARGET_DIR=C:\Windows\Temp\openjarvis-cargo-target"
cd /d "C:\Users\jkoma\OneDrive\Documents\pro\jarvis\OpenJarvis"
C:\Users\jkoma\.local\bin\uv.exe run maturin develop -m rust/crates/openjarvis-python/Cargo.toml
exit /b %errorlevel%
