In this folder, you can find the files used to generate the experiments for our DATE'24 paper.

Note, however, that the source code has changes over time and that not all commands are up-to-date.
To find the up-to-date commands for the UpTime to conduct similar experiments, please refer to the [examples](../examples) folder.

For example, the flags `-all` and `-m` for the `robdd` or `sbdd` commands are deprecated.
Now, the zero terminal is not automatically removed from the BDD. To remove the zero terminal, use the `prune` command.\
Merging ROBDDs is no longer possible. To obtain a single BDD, use SBDDs instead (`sbdd`).