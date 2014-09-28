#!/bin/sh

#nosetests --nocapture $1
nosetests --nocapture $1 --with-coverage

#nosetests --ipdb $1
#nosetests --ipdb-failure $1
