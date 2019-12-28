function Prepre-env {
    pip install requests

    mkdir "$(pwd)\dist"
    mkdir "$(pwd)\$env:KIVY_BUILD_DIR"
    if (!(Test-Path "$(pwd)\$env:KIVY_BUILD_CACHE")) {
      mkdir "$(pwd)\$env:KIVY_BUILD_CACHE"
    }
}


function Download-Packages() {
    python -m pip install pip wheel setuptools --upgrade
    python -m "win.$env:PACKAGE_TARGET" build_path "$(pwd)\$env:KIVY_BUILD_DIR" arch $env:PACKAGE_ARCH package $env:PACKAGE_TARGET output "$(pwd)\dist" cache "$(pwd)\$env:KIVY_BUILD_CACHE" download_only "1"
}


function Create-Packages() {
    python -m pip install pip wheel setuptools --upgrade
    python -m "win.$env:PACKAGE_TARGET" build_path "$(pwd)\$env:KIVY_BUILD_DIR" arch $env:PACKAGE_ARCH package $env:PACKAGE_TARGET output "$(pwd)\dist" cache "$(pwd)\$env:KIVY_BUILD_CACHE"
    dir "$(pwd)\dist"
    rm "$(pwd)\dist\*tar.gz"
}


function Upload-windows-wheels-to-server($ip) {
    echo "Uploading wheels*:"
    C:\tools\msys64\usr\bin\bash --login -c ".ci/windows-server-upload.sh $ip '$(pwd)\dist' 'kivy_deps.$env:PACKAGE_TARGET`_dev-*.whl' ci/win/deps/$env:PACKAGE_TARGET`_dev/"
    C:\tools\msys64\usr\bin\bash --login -c ".ci/windows-server-upload.sh $ip '$(pwd)\dist' 'kivy_deps.$env:PACKAGE_TARGET-*.whl' ci/win/deps/$env:PACKAGE_TARGET/"
}

function Test-kivy() {
    python -m pip config set install.find-links "$(pwd)\dist"
    python -m pip install "https://github.com/kivy/kivy/archive/master.zip[full,dev]"

    python -c 'import kivy'
    $test_path=python -c 'import kivy.tests as tests; print(tests.__path__[0])'  --config "kivy:log_level:error"
    cd "$test_path"

    echo "[run]`nplugins = kivy.tools.coverage`n" > .coveragerc
    python -m pytest .
}
