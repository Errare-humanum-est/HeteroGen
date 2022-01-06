# Compile gem5 protocol
scons build/RISCV_Big_Tiny_DeNovo/gem5.opt --default=RISCV PROTOCOL=HETERO_RCCO_GEN_NO_HS -j8

/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_cilksort_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/cilk5-cilksort -o "-n 3000000 -g 8192 -v --stats" &


/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_lu_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/cilk5-lu -o "-n 512 -v --stats" &


/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_matmul_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/cilk5-matmul -o "-n 256 -g 32 -v --stats" &


/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_mattranspose_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/cilk5-mattranspose -o "-n 8000 -b 256 -v --stats" &


/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_nqueens_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/cilk5-nqueens -o "-n 10 -g 3 -v --stats" &


/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_BC_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/BC -o "-i /artifact_top/alloy-apps/ligra/inputs/rMatGraph_J_100000 -g 32" &


/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_BellmanFord_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/BellmanFord -o "-i /artifact_top/alloy-apps/ligra/inputs/rMatGraph_WJ_200000 -g 32" &


/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_BFS_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/BFS -o "-i /artifact_top/alloy-apps/ligra/inputs/rMatGraph_J_800000 -g 32" &


/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_BFS-Bitvector_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/BFS-Bitvector -o "-i /artifact_top/alloy-apps/ligra/inputs/rMatGraph_J_500000 -g 32" &


/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_Components_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/Components -o "-i /artifact_top/alloy-apps/ligra/inputs/rMatGraph_J_500000 -g 32" &


/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_MIS_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/MIS -o "-i /artifact_top/alloy-apps/ligra/inputs/rMatGraph_J_100000 -g 32" &


/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_Radii_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/Radii -o "-i /artifact_top/alloy-apps/ligra/inputs/rMatGraph_J_200000 -g 32" &


/artifact_top/alloy-gem5/build/RISCV_Big_Tiny_DeNovo/gem5.opt --listener-mode=off --outdir=/artifact_top/alloy-gem5/sim_res/RCCO_GEN_NO_HS_Triangle_mod /artifact_top/alloy-gem5/configs/brg/sc3.py --tiny_l1d_size 4kB --num-tiny-cpus 60 --cpu-type DerivO3CPU --link-latency 1 --tiny-cpu-type TimingSimpleCPU --tiny_l1i_size 4kB --l2_size 512kB --num-dirs 8 --brg-fast-forward --num-cpus 64 --network garnet2.0 --buffer-size 0 --mem-size 4GB --ruby --l1d_size 64kB --mem-type SimpleMemory --num-l1-cache-ports 8 --num-l2caches 8 --ports 16 --big-tiny --l1i_size 64kB --topology MeshDirL2Bottom_XY --mesh-rows 8  -c /artifact_top/alloy-apps/build-applrts_sc3/Triangle -o "-i /artifact_top/alloy-apps/ligra/inputs/rMatGraph_J_200000 -g 32" &

sleep 60

# Wait for the benchmarks to finish, this can take several hours
echo "All benchmarks started for HETERO_RCCO_GEN_NO_HS, completion will take several hours"
wait
echo "All benchmarks have completed"

