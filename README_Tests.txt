Tests are located in Dtk_Tests.

When writing the tests, the idea was to keep them independent of the version of eradication.exe and of the used campaign file. For example some tests add an infection to a filtered subset of individuals. 
The number of individuals and the attributes of the individuals can change but the tests still should be applicable.

The unittests can be run with:
python -m unittest change_serialized_population_test.py

setUpClass() tries to run eradication.exe and generate a state-00015.dtk file in Dtk_Tests\0_setUp\output. This file is then used for testing.
To set the path to eradication.exe the variable path_eradication has be be changed.