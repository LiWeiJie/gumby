#!/bin/bash -xe

if [ ! -z $(pidof swift) ]; then
    echo "WARNING: Swift was running before starting the tests, killing it."
    echo "WARNING: Make sure that no other experiment/test that uses swift is running at the same time."
    killall swift
    sleep 1
    if [ ! -z $(pidof swift) ]; then
        echo "ERROR: Swift didn't die or was respawned."
        echo "ERROR: Exiting with failure"
        exit 1
    fi
fi

mkdir -p $HOME/R

export R_LIBS_USER=$R_LIBS_USER${R_LIBS_USER:+:}$HOME/R

export DISPLAY=:0

vnc4server -kill $DISPLAY ||:
vnc4server -name Tribler -geometry 1280x1024 $DISPLAY

sleep 2
openbox &
OBOX_PID=$!
sleep 1

pwd

cd tribler

rm -fR output

#Build swift
cd Tribler/SwiftEngine
make clean ||:
#Disable debug output
sed -i "s/DEBUG = True/DEBUG = False/" SConstruct
scons -j8
cp swift ../../
cd ../..
#EO Build swift

#This shouldn't be necessary anymore
#rm -fR  TriblerDownloads .Tribler

#Run the tests
if [ -z "$1" ]; then
    TESTDIR=Tribler/Test
    TESTS="$TESTDIR/test_remote_search.py $TESTDIR/test_libtorrent_download.py $TESTDIR/test_gui_general.py"
else
    TESTS="$*"
fi

echo "nosetests -v --with-xcoverage --xcoverage-file=$PWD/coverage.xml  --with-xunit --all-modules --traverse-namespace --cover-package=Tribler --cover-inclusive $TESTS" > process_list.txt


mkdir -p output
../experiments/scripts/process_guard.py process_list.txt output 60 1 ||:


ESCAPED_PATH=$(echo $PWD| sed 's~/~\\/~g')
sed -i 's/<!-- Generated by coverage.py: http:\/\/nedbatchelder.com\/code\/coverage -->/<sources><source>'$ESCAPED_PATH'<\/source><\/sources>/g' coverage.xml

#Kill everything
kill $OBOX_PID ||:
sleep 1
if [ -e /proc/$OBOX_PID ]; then
    sleep 5
    kill -9 $OBOX_PID ||:
fi

vnc4server -kill $DISPLAY ||:

#Create the graphs
$WORKSPACE/experiments/scripts/extract-resourceusage output output
$WORKSPACE/experiments/scripts/reduce-statistics output 300
cd output
R --no-save --quiet < $WORKSPACE/experiments/scripts/r/install.r
R --no-save --quiet < $WORKSPACE/experiments/scripts/r/cputimes.r


if [ ! -z $(pidof swift) ]; then
    echo "ERROR: swift was still running after finishing the tests."
    echo "ERROR: Exiting with failure."
    exit 1
fi
