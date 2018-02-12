# High Dimensional Algorithm Testing Tool (HDATT)

HDATT is a python library and command line tool that simplifies testing algorithms with high dimensional inputs and outputs, e.g. image processing algorithms.

TODO: add a motivation section

# Suites

An HDATT `Suite` is a python class that implements a few methods.  In particular, it implements methods that:

1. Collect test cases
2. Run a test case
3. Compare the result of running a test case against a previously verified
   result for the same test case
4. View a result

Each suite must also have a unique id that identifies it which is referred to as the `suite_id`.

We discuss each of these methods in detail below.

## Collecting Test Cases

A suite is responsible for collecting all of the test cases that it contains, and it must return a `dict` whose keys are ids that uniquely identify a test case over time, and whose values contain all of the inputs necessary to run the test.

## Running Test Cases

A suite is responsible for running test cases.  A test case must be run with the inputs provided from the collection stage.

The output of the algorithm we are testing will usually be a large array of some sort, which is difficult to stably compare over time as the algorithm evolves.

In order to avoid having to manually and qualitatively compare these large outputs, instead we reduce them into one or more "metrics" that can be compared automatically.  These metrics are then compared with previous results from the same test case that have been manually verified by a human.

If the automated comparison fails, it may not mean that the algorithm has actually errored.  It may simply mean that a change in the algorithm has resulted in the metrics sufficiently changing so as to require the full-output to be re-verified by a human.

The metrics alone are insufficient to make a manual verification, thus the run method should also record the full dimensional output (and possibly intermediate output) that can help a human manually verify that the result is in fact correct.

Thus, the run method of the suite must return two items

1. Metrics - Reduced, low-dimensional numbers that can be used to automatically verify if the algorithm is still running as expected, but are sensitive enough to change if the algorithm has changed substantially
2. Context - High dimensional output of the algorithm, as well as any other intermediate output that can be used by a human to verify a result.

## Comparing the result

A suite is also responsible for comparing two result of running the algorithm.  Typically this method will be used to compare the result of running a new version of the algorithm against the last human-verified result of running the algorithm for a given test case.

This method will be given the metrics from a previous, verified run (the golden metrics), as well as the metrics from a new run.  It must return a boolean indicating whether it must be re-verified by a human, and a string with any comments about the failure.


## Visualizing the result

A suite must also make it easy for humans to verify the results of running its test cases.  The `show` method is given a full result (including the metrics and the context), and it must display these results in an easy to view manner.

# Stores

Unlike many test runners that treat previous results as being transient items that loose their interest quickly, the nature of hdatt requires that historical test results be given a little more respect!  After all, the historical results are being depended on to avoid requiring all of the high-dimensional algorithm outputs from being inspected manually after each test run.

Test results are stored in a `Store`.  A store is a class that implements a few methods.

When running the hdatt CLI, there are always two stores involved:

1. The golden store - the current "gold standard" metrics for each test case
2. The save store - where all historical runs are stored for easy comparison

The requirements of each of these stores are different.

The golden store should be saved inside the git repository, so that if two developers are working on an algorithm at once, they will know if there is a merge conflict.  Because the golden store must be stored in the repository, it must also be small; we do not want it to save the result context, but just the result metrics.  Finally, we want the golden store to only retain a single result per test case.

The save store, on the other hand, should keep all historical results, and should keep the full context of the results so that they can be visually compared.  It should also not be kept inside the git repository.

# Abstractions

HDATT has the following abstractions:

- A test *suite* runs tests against a particular algorithm
- A test *case* is a particular "scenario" that a test suite runs
- A test *result* is the result of running a test case

Test results contain three pieces of information:

- *metrics*
- *context*
- meta data

Metrics are low-dimensional and easily comparable pieces of data that have been derived from the algorithm's raw high dimensional output.  The metrics are used by the test suite to automatically verify new test results against older human-verified test results.

The context includes the high-dimensional output of the algorithm, along with any relevant intermediate data.  The context is used when a human verifies a test run.

Meta data about the test result includes the current git commit, the date and time of the run, etc.

Test results are kept in *stores*.  There are two stores that the command line tool interacts with--the *golden store* and the .  There is the *golden store*, which contains all of the most up-to-date, human-verified test results.  Then there is the *save store

# Design Goals

- A conceptually simple API
- Be picky and abort easily at the start of a run, but after the run begins,
  try to catch any errors and continue.

# Casespecs

A casespec is a string that selects test cases.  A casespec may specify a single test case, or it may specify many test cases.

Here are several casespecs along with the test cases they would select:

"" - Selects all test cases in all suites.
"a" - Selects all cases in the test suite with id "a".
"a/b" - Selects test case with id "b" in the suite with id "b".

# Resultspecs

A resultspec is a string that selects test results.  A result spec may specify a single result, or many results.  Resultspecs are more varied than casespecs, because there are typically many more results that need to be selected among.

Here are several casespecs along with the test cases they would select:

"" - Selects the most recent result for every test case in every test suite.
"a" - Selects the most recent results for every test case in the test suite with id "a".
"a/b" - Selects the most recent result for the test case with id "b" in the test suite with id "a".
"a/b/c" - Selects the test result with id "c" for the test case with id "b" in the test suite with id "a".
