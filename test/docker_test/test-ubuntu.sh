#!/bin/bash

set -e
set -x

ENV_FILE=/tmp/env.sh

. ${ENV_FILE}

# setup MODULE_SRC_DIR env var
cwd=`pwd`
if [ -z "${MODULE_SRC_DIR}" ]; then
    if [ -e "$cwd/src/proj-module.cpp" ]; then
        MODULE_SRC_DIR=$cwd
    else
        MODULE_SRC_DIR=$WORKDIR/module-proj
    fi
fi
echo "export MODULE_SRC_DIR=${MODULE_SRC_DIR}" >> ${ENV_FILE}

echo "export QORE_UID=999" >> ${ENV_FILE}
echo "export QORE_GID=999" >> ${ENV_FILE}

. ${ENV_FILE}

export MAKE_JOBS=4

# install PROJ development library
apt-get update
apt-get install -y libproj-dev valgrind

# build module and install
echo && echo "-- building module --"
mkdir -p ${MODULE_SRC_DIR}/build
cd ${MODULE_SRC_DIR}/build
cmake .. -DCMAKE_BUILD_TYPE=debug -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX}
make -j${MAKE_JOBS}
make install

# add Qore user and group
groupadd -o -g ${QORE_GID} qore
useradd -o -m -d /home/qore -u ${QORE_UID} -g ${QORE_GID} qore

# own everything by the qore user
chown -R qore:qore ${MODULE_SRC_DIR}

# run the tests
cd ${MODULE_SRC_DIR}
for test in test/*.qtest; do
    gosu qore:qore qore --enable-debug $test -vv
done
# The reverse order needs a fresh interpreter before either module is loaded.
gosu qore:qore qore --enable-debug -DPythonFirst test/proj-python.qtest -vv

# Memory-check the PROJ and GEOS suites. Python coexistence runs above in both
# orders; CPython/JIT allocator and shutdown reports require Python's own
# memory-check environment and must not be suppressed by PROJ's rules.
# Use PCRE2's interpreter for memory checks; its JIT reports uninitialized
# reads under Valgrind. Normal tests above retain the default regex engine.
for test in test/proj.qtest test/projgeos.qtest; do
    QORE_PCRE2_NO_JIT=1 gosu qore:qore valgrind --error-exitcode=1 --leak-check=full --suppressions=${MODULE_SRC_DIR}/test/proj.supp qore -b --enable-debug $test -vv
done
