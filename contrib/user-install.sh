#!/bin/sh

set -e

topdir=$(readlink -f $(dirname "$(readlink -f "$0")")/..)
contribdir=$topdir/contrib
sddir=~/.config/systemd/user

install_ghmoon()
{
    local location=$(which ghmoon 2>&1)

    case "$location" in
	"")
	    echo "Installing symlink to ghmoon in ~/.local/bin"
	    mkdir -p ~/.local/bin
	    ln -s $topdir/ghmoon ~/.local/bin/ghmoon
	    ;;
	~/.local/bin/ghmoon)
	    ;;
	*)
	    cat <<EOF | fmt
WARNING: Found ghmoon in $location, please install it in ~/.local/bin
or modify the systemd unit file accordingly

EOF
	    ;;
    esac
}

install_unit()
{
    local unit=$1
    [ -f $sddir/$unit ] && return

    echo "Installing $unit to $sddir"
    install -D $contribdir/$unit $sddir/$unit
}

install_ghmoon
install_unit ghmoon.service

cat <<EOF
Done.

Setup your configuration in ~/.ghmoon/config.yaml, then enable and
start ghmoon.service.
EOF
