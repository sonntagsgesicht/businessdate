#
# script to run automated test framework on POSIX systems
#
# 1. setting up the environment
# 2. running actual test scripts
# 3. clean up afterwards
#
# All steps can be run in a single task or invokes individually providing command arguments
#

# 1. setup the environment

if [ $1 -eq 1 ]; then
  echo '*** setup test environment ***';
  python -m pip freeze > freeze_requirements.txt;
  python3 -m pip freeze > freeze3_requirements.txt;
    if [ -e requirements.txt ]; then
        python -m pip install --upgrade -r requirements.txt;
        python3 -m pip install --upgrade -r requirements.txt;
    else
        echo "no requirements.txt to install";
    fi;
    if [ -e upgrade_requirements.txt ]; then
        python -m pip install --upgrade -r upgrade_requirements.txt;
        python3 -m pip install --upgrade -r upgrade_requirements.txt;
    else
        echo "no upgrade_requirements.txt to install";
    fi;
    curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64 > "${HOME}/bin/cc-test-reporter" && chmod +x "${HOME}/bin/cc-test-reporter";
fi;

# 2. running actual test scripts

if [ $1 -eq 2 ]; then
    # todo: add time and location
    echo '*** run test scripts ***';
    if [ -e test.py ];
        then
            # todo send coverage report only once
            cc-test-reporter before-build
            coverage run test.py;
            coverage report -m;
            coverage html -d ./doc/coverage;
            coverage xml;
            cc-test-reporter after-build -t coverage.py --exit-code $? --prefix /home/rof/src/github.com/sonntagsgesicht/businessdate
            python3 test.py;
    else
        echo "no test.py";
    fi;
fi;

# 3. clean up afterwards

if [ $1 == 3 ]; then
    rm .coverage
    rm coverage.xml
    echo '*** clean up test environment ***';
    if [ -e requirements.txt ]; then
        python -m pip uninstall -r requirements.txt;
        python3 -m pip uninstall -r requirements.txt;
    else
        echo "no requirements.txt to remove";
    fi;
    if [ -e upgrade_requirements.txt ]; then
        python -m pip uninstall -r upgrade_requirements.txt;
        python3 -m pip uninstall -r upgrade_requirements.txt;
    else
        echo "no upgrade_requirements.txt to remove";
    fi;
    if [ -e freeze_requirements.txt ]; then
        # todo replace ">=" by "=="; see txt=">=, >=";echo ${txt//>=/==}
        python -m pip install --upgrade -r freeze_requirements.txt;
    fi;
    if [ -e freeze3_requirements.txt ]; then
        # todo replace ">=" by "=="; see txt=">=, >=";echo ${txt//>=/==}
        python3 -m pip install --upgrade -r freeze3_requirements.txt;
    fi;
fi;