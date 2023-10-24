The folder [code](code) contains an example of how to write Python code to tie together the flow of UpTime.

The folder [commands](commands) contains a step-wise example on how to use the command interface to tie together UpTime:
- Step 1: Generates a crossbar design using COMPACT
- Step 2: Generates a crossbar with stuck-at-faults. Then adds stuck-at-faults to simulate the behaviour over time.
- Step 3: Applies data layout reorganization using either:
  1. naive mapping (baseline)
  2. row permutations
  3. sequential row and column permutations 
  4. simultaneous row and column permutations (UpTime, this work)