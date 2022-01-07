# HeteroGen
[HeteroGen Paper](https://github.com/Errare-humanum-est/HeteroGen/blob/4b461e10eb93145de129d942ca78a2b551eea3f7/HeteroGen%20HPCA22.pdf)

## Hardware dependencies

Any PC with at least 16GB of RAM suffices to run most tests and these will complete in a matter of minutes on an Intel Skylake or comparable CPU.
However, a few deadlocks tests can require up to 1TB of RAM and hours of computation time.

## Software Dependencies

- Linux distribution (e.g. Ubuntu 20.04)
- Graphviz 2.43.0
- Python 3.8 or higher
  - antlr3 3.4
  - colorama 0.4.3
  - graphviz 0.16
  - networkx 2.5.1
  - psutil 5.8.0
  - tabulate 0.8.9
- CMurphi 5.4.9.1
- Efficiently Supporting Dynamic Task-Parallelism on Heterogeneous Cache-Coherent Systems by Wang et al.: https://zenodo.org/record/3910803

## Antlr3 setup

To install antlr3 first open to the antrl3 python3 directory. 

  *cd antlr3-master/runtime/Python3*

Then run the install script provided in the directory.

  *sudo python3 setup.py install*

## CMurphi setup
To install CMuprhi run from the parent directory:

  *cd src && make*

## Datasets

Stable state protocols, used as inputs by HeteroGen to generate the heterogeneous cache coherence protocol, are provided in the *Protocols/MOESI Directory/ord* net directory. A set of litmus tests to verify the correctness of the protocols is provided in the MurphiLitmusTests directory.

## Experiment workflow
In the top level directory run:

*python3 HeteroGen.py*


This will generate the heterogeneous coherence protocol state machines and litmus tests of protocols presented in the paper, which
will be verified using the Murphi model checker. When HeteroGen is running warnings are displayed. These warnings can be ignored when using the provided protocols, but can help to debug problems when using new atomic protocols as inputs to HeteroGen.
The generated files can be found in the directory: *Protocols/MOESI Directory/ord net/HeteroGen*
 

## Model Checker Setup

To compile the generated litmus tests **update the variable 'murphi_compiler_path'** in the file ParallelCompiler.py to your local Murphi path. Now compile the model checker files:

*python3 ParallelCompiler.py*

## Evaluation and Expected Results

To verify the correctness of the generated heterogeneous cache coherence protocols, the Murphi model checker is used. Run the generated model checking executables:

*python3 ParallelChecker.py*

The runtime of all litmus tests depends on the amount of RAM and number of CPUs available. The ParallelChecker.py will automatically run all litmus tests and generate a report file **'Test_Result.txt'** in the TestScripts directory.

If the ParallelChecker reports that no Murphi test files were found, change the access permission of the executables to ’+x’.

## Understanding the Test Report

In the report file *'Test_Result.txt'* the litmus tests failing are listed. None of the litmus tests should fail under normal operation. The types of failure that are listed can be as follows:

- Not served yet: Due to some error the litmus test was not served

- Out of memory: The verification test ran out of available RAM.

- File not found: No executable was found.

- Fail: The litmus test failed because of an unknown error (e.g. executable could not be run)

- Litmus test fail: A litmus test has failed

- Deadlock: A deadlock in the protocol was found

- Invariant: An invariant specified was violated


## Generated protocols performance evaluation

To evaluate the performance of the automatically generated MESI-RCCO HeteroGen protocol it is compared against the HCC-Denovo protocol. 

To compare the performance of the protocols, please follow the instructions provided by the authors of the Efficiently Supporting Dynamic Task-Parallelism on Heterogeneous Cache-Coherent Systems publication to setup the reference system.

Once the reference system has been setup, copy the provided **gem5_HeteroGen_protocols** directory into the docker container and run:

*setup.sh*

The setup script copies and modifies all the required files into the alloy-gem5 directory.
Change directory to:

*cd alloy-gem5*


After running the setup script, run the benchmark execution scripts in the alloy-gem5 directory to produce the simulation results.

- HCC-DeNovo protocol: *run_DeNovo.sh*

- HeteroGen MESI-RCCO protocol without any handshakes: *run_RCCO_GEN_NO_HS.sh*

- HeteroGen MESI-RCCO protocol with write handshakes: *run_RCCO_GEN_WR_HS.sh*


The simulation results are provided in the sim_res directory:

*alloy-gem5/sim_res*

Each result folder is labeled by the type of protocol (e.g. RCCO_GEN_NO_HS) that has been run followed by the name of the executed benchmark (e.g. BC).
