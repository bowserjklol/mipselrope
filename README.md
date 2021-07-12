# ROPEmporium MIPS

Repository containing solution files for each of the 8 ROPE MIPS challenges.

I use the `start.sh` to setup and manage a few components of the environment.


### Setting up a mipsel qemu guest

Download precompiled components (kernel, disk) with `start.sh install`

Start the qemu quest with `start.sh qemu`


### Getting ROPE mipsel challenges

Grab the ROPE mipsel challenges with `start.sh challenges`


## Tests

Test with `./start.sh tests` for a simple sanity check to ensure each solution produces a flag.

```sh
root@debian-stretch-mipsel:/mipselrope# ./start.sh tests
checking fluff_mipsel solution
+++++++++++++++++
ROPE{a_placeholder_32byte_flag!}

checking pivot_mipsel solution
+++++++++++++++++
ROPE{a_placeholder_32byte_flag!}

[...]

checking write4_mipsel solution
+++++++++++++++++
ROPE{a_placeholder_32byte_flag!}

checking callme_mipsel solution
+++++++++++++++++
ROPE{a_placeholder_32byte_flag!}

```

### Removal

Delete the qemu guest with `start.sh uninstall`
