#!/usr/bin/env bash
#
# functions to run automated test framework on POSIX systems
#
# 1. setting up the environment
# 2. running actual test scripts
# 3. clean up afterwards
#
# All steps can be run in a single task or be invoked individually
#
# required variables are TEST_FILE, PYPI_USR, PYPI_PWD and CC_TEST_REPORTER_ID


BIN="$(pwd)/.bin"

if [[ ! -e ${TEST_FILE} ]]; then
    echo '*** no test.py, please make sure to have a text file ***';
    exit
fi;

# ----------------------------------------------------------------------------
# define environment maintenance functions
# ----------------------------------------------------------------------------

run_setup()
{
    # 1. setup the environment
    echo '*** setup environment requirements ***';
    python -m pip freeze > freeze_requirements.txt;
    if [[ -s requirements.txt ]]; then
        python -m pip install -r requirements.txt;
    fi;
    if [[ -s upgrade_requirements.txt ]]; then
        python -m pip install --upgrade -r upgrade_requirements.txt;
    fi;
}   # end of run_setup

run_cleanup()
{
    echo '*** clean environment ***';
    # 3. clean up afterwards
    if [[ -s requirements.txt ]]; then
        python -m pip uninstall -q -q -y -r requirements.txt;
    fi;
    if [[ -s upgrade_requirements.txt ]]; then
        python -m pip uninstall -q -q -y -r upgrade_requirements.txt;
    fi;
    # sed -i 's/==/>=/g' freeze_requirements.txt
    python -m pip install --upgrade -r freeze_requirements.txt;
    rm freeze_requirements.txt
}   # end of run_cleanup


# ----------------------------------------------------------------------------
# define test functions
# ----------------------------------------------------------------------------

run_test()
{
    # 2. running actual test scripts
    echo '*** run test scripts ***';
    python ${TEST_FILE}
}   # end of run_test

run_setup_coverage()
{
    echo '*** install coverage scripts ***';
    pip install coverage
    mkdir ${BIN};
    if !([[ -e "${BIN}/cc-test-reporter" ]]); then
        case $(uname) in
            "Darwin" )
                echo '*** download coverage reporter for macOS ***';
                curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-darwin-amd64 > "${BIN}/cc-test-reporter";
                ;;
            "Linux" )
                echo '*** download coverage reporter for Linux ***';
                curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-darwin-amd64 > "${BIN}/cc-test-reporter";
                ;;
        esac;
        chmod +x "${BIN}/cc-test-reporter";
    fi;
    # echo "working in $(pwd)"
}   # run_setup_coverage

run_cleanup_coverage()
{
    echo '*** cleanup coverage scripts ***';
    #rm "${BIN}/cc-test-reporter";
    #rm -f -r ${BIN};
    coverage erase;
    rm coverage.xml
    rm -f -r htmlcov;
    pip uninstall -y coverage
}   # end run_cleanup_coverage

run_coverage()
{
    # 2. running coverage scripts
    echo '*** run coverage scripts ***';
    "${BIN}/cc-test-reporter" before-build;
    coverage run ${TEST_FILE};
    coverage report -m;
    coverage html;
    coverage xml;
    echo '*** upload coverage report ***';
    "${BIN}/cc-test-reporter" after-build -r ${CC_TEST_REPORTER_ID} -t coverage.py --exit-code $? --prefix $(pwd)
}   # end of run_coverage

run_sphinx()
{
    # todo add sphinx build and doctest
    echo '*** run sphinx scripts ***';
    cd ./doc/sphinx/;
    make clean;
    make html;
    make doctest;
    cd ../..;
}   # end of run_sphinx

run_setuptools()
{
    echo '*** run setuptools scripts ***';
    python setup.py build
    python setup.py sdist bdist_wheel
}   # end of run_setuptools


run_deploy()
{
    echo '*** run deployment scripts ***';
    python -m pip install --upgrade twine;
    python -m twine upload -u ${PYPI_USR} -p ${PYPI_PWD} --repository-url https://test.pypi.org/legacy/ dist/*;
    python -m pip uninstall twine
}

