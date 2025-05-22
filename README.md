# DIS_Project

## Initial Setup
### Automatic Setup
- In a terminal run the file `setup.sh` with bash (`bash setup.sh`)
- This should hopefully:
    - Create a database either under the default user 'postgres' or your own user (what your terminal is logged in as)
    - Create a python virtual environment if necessary
    - Install the required packages in the virtual environment
    - Run the `setup.py` file to initialise the database with required tables

### Manual Setup

## To-Dos
- Setup simple flask (or other Python front-end framework) as a basis and template for future development
- Set up users' table with appropriate fields in `setup.py`
- Initialise a report describing the idea (similar to [loldle](https://loldle.net/classic)) (begin typing a name and click a picture to understand)
- Perhaps begin implementing some python code with logic to handle the queries involved. 