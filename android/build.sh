cd android

skip() {
    $* 2> /dev/null
}

skip mkdir build/server
skip mkdir build/client
skip mkdir build/zlib
skip mkdir build/private
skip mkdir build/private/lib
skip mkdir build/public

skip ln -sf $PWD/../server build/server/jni
skip ln -sf $PWD/../src build/client/jni
skip ln -sf $PWD/../zlib-1.2.5 build/zlib/jni
skip ln -sf $PWD/pyjni build/pyjni

. info.sh
export PATH="$PATH:$ANDROID_PATH"

cd build/server
ndk-build
cd ../..

cd build/client
ndk-build
cd ../..

cd build/pyjni
ndk-build
cd ../..

cp -p build/client/libs/armeabi/* .
cp -p build/server/libs/armeabi/* .
cp -p build/pyjni/libs/armeabi/* .
