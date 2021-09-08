#!/bin/bash


# 2021, Ludwig Kürzinger, Technische Universität München

# exit on error
set -e
BASEDIR=$(dirname "$0")
BASEDIR=$(realpath "$BASEDIR")
CONFIGPATH=${HOME}/.mothpi
SYSTEMD_ENV_PATH=$(realpath $HOME)"/.config/environment.d/mothpi.conf"


help() {
    PROGRAM=$(basename "$0")
    cat >&2 <<-_EOF
    DESCRIPTION
        Automated MothPi manager
    
    USAGE

    USAGE
        ${PROGRAM} <mode>
            mode      Select script functionality
        Modes
            serve       Run Mothpi as a service
            stop        Stop all services
            run         Run Mothpi standalone


            selfcheck   Perform an installation check
            update      Download mothpi updates
            sync        Upload all moth pictures
            tunnel      Open reverse SSH tunnel

            init        Install mothpi-programm
                        Only run this the first time
            uninstall   Remove all service links

	_EOF
    exit 0
}


init(){
    # copy systemd unit files
    echo "Copy systemd unit files"
    mkdir -p ~/.config/systemd/user/
    cp -uv ${BASEDIR}/systemd/mothpi.service ~/.config/systemd/user/

    echo "Save configuration."
    touch ~/.mothpi
    mkdir -p ~/.config/environment.d/
    cat <<EOF > ${SYSTEMD_ENV_PATH}
MOTHPI_BASEDIR=${BASEDIR}
MOTHPI_CONFIG=${CONFIGPATH}
EOF
    echo "Enable service"
    systemctl --user enable mothpi.service
}


selfcheck(){
    # list directories
    PROGRAM=$(basename "$0")
    echo "Starting self check of ${PROGRAM}"
    echo "Running from: ${BASEDIR}"
    # check systemd services and timers
    echo "Systemd config:"
    cat ${SYSTEMD_ENV_PATH}
    echo "Mothpi service status: "
    systemctl --user status mothpi.service
}


update(){
    cd ~/mothpi
    echo "-- Update repository (and overwrite all changes!)"
    git fetch origin master
    git reset --hard origin/master
    # soft: git pull origin master
    echo "-- Stop systemd services"
    systemctl --user stop mothpi.service
    echo "-- Update systemd files"
    cp -uv ${BASEDIR}/systemd/*.service ~/.config/systemd/user/
    echo "-- Restart systemd services, run:"
    echo "systemctl --user start mothpi.service"
}


sync(){
    echo "sync pictures"
    # get pictures directory

    # rsync pictures to the server
#    rsync mothpi@dl.visammod.vision.in.tum.de -p 58022
}


run(){
    # run mothpi
    python3 ${BASEDIR}/mothpi/mothpi.py
}


serve(){
    # run mothpi as service
    echo "run: "
    echo "systemctl --user start mothpi.service"
    echo "to stop: "
    echo "systemctl --user stop mothpi.service"
    echo "to obtain logs:"
    echo "journalctl --user -u mothpi.service"
}


tunnel(){
    echo "Creating a reverse ssh tunnel"
    # create a reverse ssh tunnel
    # ssh mothpi@dl.visammod.vision.in.tum.de -p 58022
}


## Application menu
if   [[ $1 == "init" ]]; then
    init
elif [[ $1 == "selfcheck" ]]; then
    selfcheck
elif [[ $1 == "update" ]]; then
    update
elif [[ $1 == "sync" ]]; then
    sync
elif [[ $1 == "run" ]]; then
    run
elif [[ $1 == "serve" ]]; then
    serve
elif [[ $1 == "tunnel" ]]; then
    tunnel
else
    help
fi

echo "$(basename "$0") done."