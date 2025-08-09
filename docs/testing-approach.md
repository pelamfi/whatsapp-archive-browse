## Testing approach used in Whatsapp Archive Browse

### Motivation for the testing approach

I've seen large projects become very expensive to refactor due to countless
fragile low value unit tests — this is what I would like to avoid in any
project.

Ability to effortlessly break down functionality or move functions to other
modules, classes or files is the most basic form (perhaps after renaming) of
refactoring. However, unit tests often end up focusing on individual functions
and small groupings of them in a way that moving code around (refactoring)
breaks the tests. Moving often also would require refactoring of the tests as
well because it is no longer a unit test by definition if, for example, some of
the functions that the test is built upon are no longer in the "unit".

### Inspiration for the testing approach

Roughly inspired by [the testing
trophy](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications),
but focusing even more on end to end tests.

### Testing Approach in WhatsApp Archive Browse

- Heavy use of type hints (static, base of the testing trophy)
- Small number of basic simple unit tests (skimping here in this project)
  - No unit tests if coverage by the end-to-end tests is sufficient
  - Avoid large amounts of complex and fragile unit tests
    - At extreme, unit tests make refactoring so hard that refactoring is
      avoided
      - This ends up harming the velocity and quality of the project
- Integration and end to end testing are the same thing in this project due to
  simplicity
  - So few components that testing subassemblies of them would not add value
    compared to just testing all of them together in the end-to-end tests.
- End-to-end tests in [test_integration.py](../tests/test_integration.py). (The
  top part of the trophy)
  - End-to-end tests are based on stored reference files
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

### When Unit Tests Make Sense

While this project heavily favors end-to-end tests, there are scenarios where unit
tests provide significant value:

- Complex algorithms with many edge cases
  - When individual functions have complex logic that needs to be verified
    exhaustively
  - Where setting up all edge cases in E2E tests would be impractical
- Core business logic requiring verifiable correctness
  - Critical calculations or data transformations
  - Security-sensitive code paths
- Highly dependent components
  - Code that relies on many external services
  - Where E2E test setup would be prohibitively expensive or complex

### Trade-offs and Considerations

The choice between unit tests and E2E tests involves several trade-offs:

Test Execution Speed:
- E2E tests are typically slower to execute
- Unit tests provide faster feedback loops during development
- Consider the impact on developer workflow and CI/CD pipelines

Maintenance Costs:
- Unit tests often require more updates during refactoring
- E2E tests are more resilient to internal restructuring
- Reference file systems (like in this project) can make E2E test maintenance
  easier

Debug Complexity:
- Unit test failures usually point to specific functions
- E2E test failures might require more investigation
- However, with good tooling (like our diff system), E2E test fixes can be
  straightforward

### Example: Our Reference File System in Practice

1. During development:
   - Make changes to the code
   - Run E2E tests, which generate new output
   - Git diff shows exactly what changed in the output
   - If changes are expected, update reference files (`rm -rf
     tests/resources/reference_output/*` and rerun tests)

2. Debugging workflow:
   - When an E2E test fails, examine the diff between expected and actual output
   - Use standard debugging tools to trace through the full program flow
   - The stateless nature of our system makes this process straightforward
   - Update reference files once the issue is fixed and verified

3. Refactoring example:
   - Moving functions between modules
   - Unit tests would need updates to import paths and mock setups
   - Our E2E tests continue passing as they only care about final output

### Choosing Between Unit and E2E Tests

Consider these factors when deciding on test approach:

1. System Characteristics:
   - Stateful vs stateless nature
   - Complexity of component interactions
   - External dependencies

2. Development Context:
   - Available tooling for test maintenance
   - Team size and experience
   - Project phase (prototype vs maintenance)

3. Risk Profile:
   - Cost of failures
   - Speed of feedback needed
   - Deployment frequency

4. Practical Constraints:
   - CI/CD pipeline requirements
   - Development workflow needs
   - Resource limitations

The approach in this project works well because:
- The system is primarily stateless
- We have good tooling for reference comparisons
- The component interactions are straightforward
- The end-to-end workflow is our primary concern

Different contexts might require different balances of testing approaches, but
the key is choosing the method that provides the most value for your specific
situation while minimizing maintenance overhead.

