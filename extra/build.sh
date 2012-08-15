#!/bin/bash

KRTOOLKIT_LOC=~/Projects/krtoolkit
DOWNWARD_LOC=~/Projects/FD

PDDL_FILES=( greedy_join.py instantiate.py build_model.py pddl_to_prolog.py split_rules.py normalize.py )

# Copy the PDDL libs
cp -rf $DOWNWARD_LOC/src/translate/pddl/*.py $KRTOOLKIT_LOC/krrt/planning/pddl/
cp $DOWNWARD_LOC/src/translate/graph.py $KRTOOLKIT_LOC/krrt/planning/pddl/
cp $DOWNWARD_LOC/src/translate/tools.py $KRTOOLKIT_LOC/krrt/planning/pddl/
cp $DOWNWARD_LOC/src/translate/timers.py $KRTOOLKIT_LOC/krrt/planning/pddl/

for f in "${PDDL_FILES[@]}"
do
    cp $DOWNWARD_LOC/src/translate/$f $KRTOOLKIT_LOC/krrt/planning/pddl/
    sed -i 's/import pddl$/from krrt.planning import pddl/' $KRTOOLKIT_LOC/krrt/planning/pddl/$f
done


# Copy the SAS libs
cp -rf $DOWNWARD_LOC/scripts/stuff/sas_tasks/*.py $KRTOOLKIT_LOC/krrt/planning/sas/
