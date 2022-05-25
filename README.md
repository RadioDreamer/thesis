# Simulation and Visualization of P-systems

This repository contains my Computer Science BSc thesis. The goal of the software is to construct a membrane system and simulate it's computation. After construction, the membrane system is visualized on a graphical surface. A general definition of membrane systems can be found at [Wikipedia](https://en.wikipedia.org/wiki/P_system).

### Prerequisites

This project is written in *Python* using the *PySide6* module.
The later can be installed using the command:

```
pip install pyside6
```
The testing is implemented by *PyTest*, which can be downloaded using the

```
pip install -U pytest
```
command. 

## Unit Tests

The unit tests can be found under the **test** folder. To run the tests, simply run the
```
pytest UnitTests.py
```

command in the above mentioned directory.

### Coding Style

Since the project is following the OOP paradigm, the classes are in *CamelCase* notation. All methods and member variables however follow the *snake_case* notation, resulting in a more pythonic experience.
