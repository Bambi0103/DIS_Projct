#!/bin/bash

echo "Checking for PostgreSQL installation..."
psql --version
if [ $? -ne 0 ]; then
    echo "ERROR: PostgreSQL is not installed. Please install PostgreSQL and try again."
    exit 1
fi

curr_user=$(whoami)
echo "Identified current user: $curr_user"

role_exists=$(psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$curr_user';")
if [[ -z $role_exists ]]; then
    echo "Your current user '$curr_user' does not exist in PostgreSQL (your databases etc. are currently under the 'postgres' user)"
    echo "Do you wish to create a new role with the same name as your current user? (y/n)"
    read -r create_role
    if [[ $create_role == [Yy] ]]; then
        read -s -p "Enter password for new role: " new_role_password
        echo
        if [[ -z $new_role_password ]]; then
            echo "No password provided. Exiting."
            exit 1
        fi
        echo "Creating role '$curr_user' with superuser privileges..."
        psql -U postgres -c "CREATE ROLE $curr_user WITH LOGIN SUPERUSER PASSWORD '$new_role_password';"
        if [ $? -ne 0 ]; then
            echo "ERROR: Failed to create role '$curr_user'. Please check your PostgreSQL configuration."
            exit 1
        else
            echo "OK: Role '$curr_user' created successfully."
        fi
    elif [[ $create_role == [Nn] ]]; then
        echo "Using 'postgres' as the database user for subsequent operations."
        curr_user="postgres"
    else
        echo "Invalid choice. Exiting."
        exit 1
    fi
else
    echo "OK: User role '$curr_user' exists in PostgreSQL."
fi

psql_output=$(psql -U "$curr_user" -c "CREATE DATABASE guesstheplayerdb" 2>&1)
psql_exit=$?

if [ $psql_exit -ne 0 ]; then
    if echo "$psql_output" | grep -q "already exists"; then
        echo "Database 'guesstheplayerdb' already exists."
    else
        echo "ERROR: Failed to create the database. Error output:"
        echo "$psql_output"
        echo "Do you wish to continue [1] or exit [0]?"
        read -r continue_choice
        if [ "$continue_choice" -eq 0 ]; then
            echo "Exiting the script."
            exit 1
        elif [ "$continue_choice" -eq 1 ]; then
            echo "Continuing with the script..."
        else
            echo "Invalid choice. Exiting."
            exit 1
        fi
    fi
else
    echo "OK: Database 'guesstheplayerdb' created successfully."
fi

###############################################################################
# 1. Locate an executable that gives us Python 3.13.x
###############################################################################
PYTHON_CMD=""

try_cmd() {
    ver=$(eval "$1 --version 2>&1" || true)
    if [[ $ver =~ ^Python[[:space:]]+3\.13\.[0-9]+ ]]; then
        PYTHON_CMD="$1"
    fi
}

try_cmd python3
[[ -z $PYTHON_CMD ]] && try_cmd python
[[ -z $PYTHON_CMD ]] && try_cmd "py -3.13"
[[ -z $PYTHON_CMD ]] && try_cmd "py -3"

if [[ -z $PYTHON_CMD ]]; then
    echo "ERROR: No Python 3.13.x interpreter found in PATH." >&2
    exit 1
fi

python_version="$($PYTHON_CMD --version 2>&1)"
echo "OK: Found $python_version (via '$PYTHON_CMD')."

###############################################################################
# 2. Ensure a venv exists (named “venv”)
###############################################################################
if [[ ! -d venv ]]; then
    read -rp "No virtual env named 'venv'. Create it now? (y/n) " create_venv
    if [[ $create_venv == [Yy] ]]; then
        echo "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    else
        echo "Aborted by user." >&2
        exit 1
    fi
fi
echo "OK: Virtual environment ready."

###############################################################################
# 3. Activate the venv (handles Linux/macOS ↔ Windows paths)
###############################################################################
if [[ -f venv/bin/activate ]]; then
    source venv/bin/activate
elif [[ -f venv/Scripts/activate ]]; then
    source venv/Scripts/activate
else
    echo "ERROR: Could not find an 'activate' script inside venv." >&2
    exit 1
fi
echo "OK: Virtual environment activated."

###############################################################################
# 4. Install dependencies via the *same* interpreter
###############################################################################
echo "Installing required packages..."
$PYTHON_CMD -m pip install --upgrade pip wheel >/dev/null
$PYTHON_CMD -m pip install -r requirements.txt
echo "OK: Requirements installed."

echo "main.py is now ready to run - do you wish to run it now? (y/n)"
read -r run_choice
if [[ $run_choice == [nN] ]]; then
    echo "Exiting the script."
    exit 0
elif [[ $run_choice == [yY] ]]; then
    echo "Input your database password (will be used for calling the Python script):"
    read -r db_password
    if [[ -z $db_password ]]; then
        echo "No password provided. Exiting."
        exit 1
    fi
    echo "Running main.py with database password..."
    python src/main.py --user "$curr_user" --password "$db_password"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to run main.py. Please check your configuration."
        exit 1
    else
        echo "OK: main.py executed successfully."
    fi
else
    echo "Invalid choice. Exiting."
    exit 1
fi
