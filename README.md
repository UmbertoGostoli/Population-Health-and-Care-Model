# Population Health and Care Model
_Basic framework for generating simulated agent populations with realistic socio-demographic characteristics_


To run the model, simply run _main_o.py_.  To generate and view the resulting graphs once the simulation runs are completed, run _graphs.py_.  Additional documentation will be added to demonstrate how the scenario generation features work.

This version is set to run a single simulation, rather than use the scenario generation.  In order to change this, open _main_o.py_ and change line 475 to read _parametersFromFiles = True_.

This simulation can run on multiple processor cores simultaneously when exploring a set of scenarios.  To use the multiprocessing features, change _m['multiprocessing']_ to _True_ on line 93 in _main_o.py_, then enter the number of cores you wish to use in the following line as the value for _m['numberProcessors']_.

[![DOI](https://zenodo.org/badge/170349145.svg)](https://zenodo.org/badge/latestdoi/170349145)

