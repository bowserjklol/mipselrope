#!/usr/bin/env bash

if [ "$1" = "uninstall" ]; then
    rm -f \
    debian-stretch-mipsel.qcow2 \
    initrd.img-4.9.0-4-5kc-malta.mipsel.stretch \
    vmlinux-4.9.0-4-5kc-malta.mipsel.stretch

elif [ "$1" = "install" ]; then
    # https://people.debian.org/~jcowgill/qemu-mips/
    wget https://people.debian.org/~jcowgill/qemu-mips/debian-stretch-mipsel.qcow2
    wget https://people.debian.org/~jcowgill/qemu-mips/initrd.img-4.9.0-4-5kc-malta.mipsel.stretch
    wget https://people.debian.org/~jcowgill/qemu-mips/vmlinux-4.9.0-4-5kc-malta.mipsel.stretch

elif [ "$1" = "qemu" ]; then
    qemu-system-mips64el \
        -M malta \
        -cpu MIPS64R2-generic \
        -m 2G \
        -append 'root=/dev/vda console=ttyS0 mem=2048m net.ifnames=0 nokaslr' \
        -netdev user,id=user.0 \
        -device virtio-net,netdev=user.0 \
        -device usb-kbd \
        -device usb-tablet \
        -device e1000 \
        -net user,hostfwd=tcp::2222-:22 \
        -net nic \
        -nographic \
        -kernel vmlinux-* \
        -initrd initrd.img-* \
        -drive file=$(echo debian-*.qcow2),if=virtio

elif [ "$1" = "challenges" ]; then
    for chal in ret2win split callme write4 badchars fluff pivot ret2csu
        do
            wget https://ropemporium.com/binary/"$chal"_mipsel.zip 2>/dev/null
            unzip "$chal"_mipsel.zip -d "$chal"
            rm "$chal"_mipsel.zip
        done

elif [ "$1" = "tests" ]; then
    find . -type f -executable | grep -v '\.py\|\.s\|release' | while read line
        do
            directory=$(echo $line | cut -d\/ -f2)
            binary=$(echo $line | cut -d\/ -f3)
            chall=$(echo $binary | cut -d _ -f1)

            echo "checking $binary solution"
            echo '+++++++++++++++++'
            cd $directory
            if [ "$binary" != "pivot_mipsel" ]; then
                python3 $chall-exploit.py
                if [ "$binary" == "ret2win_mipsel" ]; then
                    # workaround for infinite return to flag func
                    ./$binary < payload.bin | grep ROPE\{ &
                    sleep 1
                    killall $binary
                else
                    cat payload.bin | ./$binary | grep ROPE\{
                fi
            else
                ./$chall-exploit.py | grep ROPE\{
            fi
            cd ..
            echo
        done

else
    echo "Usage: ./$@ challenges | install | uninstall | qemu | tests"
    echo "    challenges: wget all the mipsel challenges"
    echo "    install: wget kernel and disk image files"
    echo "    uninstall: remove kernel and disk image files"
    echo "    qemu: start qemu mipsel emulated machine"
    echo "    tests: start tests for each solution"

fi

