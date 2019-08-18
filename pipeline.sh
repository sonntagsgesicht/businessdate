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

set -e
# import utility functions
. pipeline_tools.sh;
if [[ -e pipeline_info.sh ]]; then . pipeline_info.sh; fi;

# ----------------------------------------------------------------------------
# run full test pine line
# ----------------------------------------------------------------------------

echo ''
switch_pyenv 2.7
run_setup
run_test
run_cleanup

echo ''
switch_pyenv 3.5
run_setup
run_test
run_cleanup

echo ''
switch_pyenv 3.6
run_setup
run_test
run_cleanup

echo ''
switch_pyenv 3.7
run_setup
run_setup_coverage
run_test
run_coverage
run_sphinx
run_setuptools
#run_deploy
run_cleanup_coverage
run_cleanup