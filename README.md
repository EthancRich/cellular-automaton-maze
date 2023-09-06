# Maze Generator via Cellular Automaton + Maze Game

## Description
This program is an *interactive maze game*, where each maze is randomly generated each run from a cellular automaton. It's built entirely in Python using pygame. This project is my first major attempt at writing Python code, and I learned a lot about the interesting, wild, and sometimes frustrating world of pythonisms. I really appreciate the value of worrying less about debugging code and mocking up a product that will run properly. It was a breath of fresh air sometimes, writing sections and the result working as intended.

The maze generation is built upon a [cellular automaton algorithm](https://justinparrtech.com/JustinParr-Tech/wp-content/uploads/Creating%20Mazes%20Using%20Cellular%20Automata_v2.pdf) by Justin A. Parr. The documentation for this automaton is quite extensive and uses some interesting properties like vectors and bitwise math to efficiently calculate the neighborhood of cells. While the implementation by Parr generates 2D maze images, I implemented the automaton in three dimensions. Parr’s documentation provides some pseudo code instructions for the integral functions and general instructions for variables and pieces to maintain for the maze to be generated. All code in the project was written by myself.

## Set Up
Ensure that you have a proper Python environment installed in your system with Pygame. Then, download both the cell.py and game.py files. Simply running the game.py script will start the program. Feel free to modify the dimensions of the maze in the game.py script.

Alternatively, you may download and run either of the executables in the repository as a self-contained experience of either a 5x5x5 or 10x10x10 maze.

## Instructions
**Escape** - *Quits the program*\
**Arrow Keys / Click + Drag** - *Camera Pan*\
**Space** - *Build Maze*

Upon running the program, the program will start in Cellular Automaton Mode, the first of two modes.

### Cellular Automaton Mode
A 3D array of values will appear. These represent the different states of the representative cell as the maze is generated. Hold **space** to begin generating the maze.

**Page Up** - *Maze Game Mode (When maze is completely built)*

### Maze Game Mode
The display will change to a skeleton mapping between each point in the maze. As the red dot, navigate the maze to the yellow dot opposite on the cube.

**QWEASD** - *Move Red Dot*\
**Page Down** - *Cellular Automaton Mode*
