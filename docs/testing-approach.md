## Testing approach used in Whatsapp Archive Browse

### Motivation

I've seen large projects become very expensive to refactor due to countless
fragile low value unit tests... this is what I would like to avoid in any
project.

Ability to effortlessly break down functionality or move functions to other
modules, classes or files is the most basic form (perhaps after renaming) of
refactoring. However unit tests often end up focusing on individual functions
and small groupings of them in a way that moving code around (refactoring)
breaks the tests. Moving often also would require refactoring of the tests as
well because if is no longer a unit test by definition if for example some of
the functions that the test is built upon are no longer in the "unit".

### Inspiration

Roughly inspired by [the testing
trophy](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications),
but focusing even more on end to end tests.

### Testing approach

- Heavy use of type hints (static, base of the testing trophy)
- Small number of basic simple unit tests (skimping here in this project)
  - No unit tests if coverage by the end to end tests is sufficient
  - Avoid large amounts of complex and fragile unit tests
    - At extereme unit tests make refactoring so hard that refactoring is
      avoided
      - This ends up harming the velocity and quality of the project
- Integration and end to end testing are the same thing in this project due to
  simplicity
  - So few components that testing subassemblies of them would not add value
    compared to just testing all of them together in the end to end tests.
- End to end tests in [test_integration.py](../tests/test_integration.py). (The top part of the trophy)
  - End to end tests are based on stored refernce files
  - Easy to compare using git diffs
  - Easy to update automatically when changes are made
  - Input files constructed by test using resources stored in the project
  - Top level function of the program called
  - Outputs compared to reference files stored in git, mismatches fail tests
  - Facility within the test to regenerate reference outputs if they are missing
    (typically deleted by programmer `rm -rf
    tests/resources/reference_output/*`)
  - In this relatively straightforward stateless project end to end tests are
    easy to debug and understand

