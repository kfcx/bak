nuitka --mingw64 --standalone --python-flag=no_site --include-module=app --include-data-dir=static=static --nofollow-import-to=opencv-python,zstandard,nuitka,ordered-set --no-pyi-file --remove-output -o aocr main.py

python -m nuitka \
        --standalone \
        --python-flag=nosite,-O \
        --plugin-enable=numpy \
        --clang \
        --warn-implicit-exceptions \
        --warn-unusual-code \
        --prefer-source-code \
        --show-progress \
        --show-memory \
        --windows-uac-admin=Windows \
        --include-module=app \
        --main=main.py


python -m nuitka --standalone --onefile --python-flag=no_site --include-module=app -o microservice.bin main.py


pipenv install
pipenv run python -m nuitka --include-module=app --follow-imports --standalone test1.py

python -m nuitka --mingw64 --standalone --windows-disable-console --plugin-enable=pyside6 --windows-icon-from-ico=static/img/logo.png --linux-onefile-icon=static/img/logo.png --onefile --python-flag=no_site --include-module=app -o ClipSync tray_main.py

python -m nuitka --mingw64 --standalone --plugin-enable=pyside6 --windows-icon-from-ico=static/img/logo.png --linux-onefile-icon=static/img/logo.png --onefile --python-flag=no_site --include-module=app -o ClipSync tray_main.py

python -m nuitka --mingw64 --standalone --python-flag=no_site --include-module=app -o pokemmo main.py
