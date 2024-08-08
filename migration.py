import os
import subprocess
import sys

def run_command(command):
    print(f"Running command: {command}")  # Логируем команду
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Command failed: {command}")
        sys.exit(1)

def main():
    # Set the FLASK_APP environment variable
    os.environ['FLASK_APP'] = 'run.py'

    # Initialize the migration directory, if it does not already exist
    if not os.path.exists('migrations'):
        print("Initializing migrations...")
        run_command('flask --app run.py db init')
    else:
        print("Migrations directory already exists, skipping 'flask db init'...")

    # Create an initial migration
    print("Creating migration...")
    run_command('flask --app run.py db migrate -m "migration"')

    # Apply the migration to the database
    print("Applying migration...")
    run_command('flask --app run.py db upgrade')

    print("Migration complete.")

if __name__ == "__main__":
    main()
