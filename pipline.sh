#!/usr/bin/env bash
#
# script to run automated test framework on POSIX systems
#
# 1. setting up the environment
# 2. running actual test and deployment scripts
# 3. clean up afterwards
#
# All steps can be run in a single task or invokes individually providing command arguments
#

# import utility functions
. ./tools.sh

TEST_FILE="test.py"
# CC_TEST_REPORTER_ID="1234"

PYPI_USR="sonntagsgesicht"
PYPI_PWD="abc"

if [[ ! -e ${TEST_FILE} ]]; then
    echo '*** no test.py, please make sure to have a text file ***';
    exit
fi;



# ----------------------------------------------------------------------------
# run full test pine line
# ----------------------------------------------------------------------------

echo ''
pyenv global 2.7
ver=$(pyenv version)
echo "*** use new python environment ${ver} ***"
#run_setup
#run_test
#run_cleanup

echo ''
pyenv global 3.5
ver=$(pyenv version)
echo "*** use new python environment ${ver} ***"
#run_setup
#run_test
#run_cleanup

echo ''
pyenv global 3.6
ver=$(pyenv version)
echo "*** use new python environment ${ver} ***"
#run_setup
#run_test
#run_cleanup

echo ''
pyenv global 3.7
ver=$(pyenv version)
echo "*** use new python environment ${ver} ***"
run_setup
#run_setup_coverage
#run_test
run_coverage
#run_sphinx
#run_setuptools
#run_deploy
#run_cleanup_coverage
run_cleanup