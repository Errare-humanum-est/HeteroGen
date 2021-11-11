# HeteroGen

## Software Dependencies

- Linux distribution (e.g. Ubuntu 20.04)
- Python 3.8 or higher
  - antlr3 3.4
  - colorama 0.4.3
  - graphviz 0.16
  - networkx 2.5.1
  - tabulate 0.8.9
- CMurphi 5.4.9.1

## Run HeteroGen:
  *python3 TestScripts/HeteroGen.py* 

This will generate the heterogeneous coherence protocol statemachines and litmus tests of protocols presented in the paper, which will be verified using the Murphi model checker.
The output directory for the generated Murphi model checker files is *Protocols/MOESI_Directory/RF_Dir/ord_net/HeteroGen*

## Model Checker Setup
To compile the generated murphi litmus test files **update variable ’murphi_compiler_path’**  in  TestScripts/ParallelCompiler.py  to  your  localMurphi path.
Now compile the model checker files:
  *python3 TestScripts/ParallelCompiler.py*
  
## Evaluation and Expected Results
To verify the correctness of the generated heterogeneous cache co-herence protocols, the Murphi model checker is used.
Run the generated model checking executables:
  *python3 TestScripts/ParallelChecker.py*

The runtime of all litmus tests depends on the amount of RAM and number of CPUs available. The ParallelChecker.py will automatically run all litmus tests and generate a report file 'Test_Result.txt' in the TestScripts directory.

## Understanding the Test Report
In the report file 'Test_Result.txt' the litmus tests failing are listed. None of the litmus tests should fail under normal operation. 
The types of failure that are listed can be as follows:
  - *Not served yet*: Due to some error the litmus test was not served 
  - *Out of memory*: The verification test ran out of available RAM.
  - *File not found*: No executable was found.
  
  - *Fail*: The litmus test failed because of an unknown error (e.g. executable could not be run)
  - *Litmus test fail*: A litmus test has failed
  - *Deadlock*: A deadlock in the protocol was found
  - *Invariant*: An invariant specified was violated






