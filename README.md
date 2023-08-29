# YAML-heritage

This library enables easy loading of parameters from a YAML file into Python class structures.

## Usage

This `example.ipynb` can be found in the examples folder.

- Create the expected structure with Python classes

  ```python
  from yaml_heritage import Heritage

  class Subclass(Heritage):
      subparam: str
      param1: int

  class Example(Heritage):
      param1: int
      param2: float
      param3: Subclass
  ```

- Replicate the same structure in the YAML file

  ```yaml
  param1: 1.1
  param2: 2.5
  param3:
    subparam: abc
    param1: 2.3
  ```

- Load the parameters from the YAML file into the classes

  ```python
  example = Example.load('example.yaml')
  ```

- Then `example` would be :

  ```yaml
  param1: 1,
  param2: 2.500e+00,
  param3:
    subparam: abc,
    param1: 2
  ```

Note that the values are converted to the expected type. For example, param1 is expected to be an integer, so 1.1 is converted to 1.

## Yaml syntax

- Float
  Floats should have the decimal point at the end. For example, '35e6' should be written as '35.e6'.

- Link other file
  You can easily link other files as a parameter and they will be loaded.

  ```yaml
  etching_param: &etching_param 'const_params/etching_params.yaml'
  ```

- Link to a value:

  ```yaml
  etching_param: &etching_param 'const_params/etching_params.yaml'
  ...
  somewhere:
      etching_param: *etching_param
  ```

- Link by relative link
  You can link to a value by relative link, example: `$.param_a`

  - `$` sign denotes that it is a link.
  - `.` denotes to move up one level to find the parameter.
  - `param_a` is the name of the parameter

  ```
  param_a: 1
  ...
  somewhere:
      param_b: $.param_a
  ```
