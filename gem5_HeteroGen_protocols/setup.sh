# Remove old scons files
rm ../alloy-gem5/src/mem/protocol/SConsopts
rm ../alloy-gem5/src/mem/SConscript
rm ../alloy-gem5/src/cpu/SConscript

# Copy new source files into alloy-gem5
cp -r . ../alloy-gem5/

