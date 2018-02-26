
# HDAT example

This directory shows how to use HDAT to test a very simple image processing algorithm. The algorithm being tested, found in `image_example.py`, simply flips an image upside down, then uses the `ndimage` library to apply a Gaussian blur. The test suite in `image_example_hdat.py` identifies test cases, displays images for review, and compares image metrics to test the algorithm.

Dependencies are required to run the example. All can be installed with `pip`:
 * numpy
 * scipy
 * imageio
 * matplotlib

The example also assumes that the `hdat` module has been installed with `pip`.

## Listing the test cases
List available test cases in the `hdat` directory:
```
hdat list
```
Two test cases with the `example-suite` suite id should appear with the casespecs `example-suite/chicken` and `example-suite/wheat`. Test suites from the `hdat` unit tests will also appear, but will throw a `NotImplementedError` if run.

## Running and displaying test cases
Run the algorithm and display the resulting images:
```
hdat runshow example-suite
```
A window with a processed image should appear. When closed, the next test case will run and another window should appear.

## Verifying the initial run
When running test cases for the first time, there will be no golden result to compare the test results with. Add the resulting images to the golden result store with:
```
hdat verify example-suite
```

## Modifying the algorithm and re-running
The comments in `image_example.py` contain suggestions for changes to the image processing algorithm. Try making a change and re-running the test suite with:
```
hdat runshow example-suite
```
Depending on the change made, the image metrics comparison (minimum value, average value, etc.) may pass or fail. If they fail, the algorithm change can be reverted, or the change can be verified, updating the golden results store:
```
hdat verify example-suite
```
