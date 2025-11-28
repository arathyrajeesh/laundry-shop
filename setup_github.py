#!/usr/bin/env python3
"""
GitHub Setup Script for Laundry Shop Project
This script helps you safely initialize Git and prepare your project for GitHub.
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 Laundry Shop - GitHub Setup Script")
    print("=" * 50)

    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  WARNING: .env file not found!")
        print("Please copy .env.example to .env and fill in your actual credentials before proceeding.")
        print("Run: cp .env.example .env")
        response = input("Do you want to continue anyway? (y/N): ").lower().strip()
        if response not in ['y', 'yes']:
            print("Setup cancelled. Please create your .env file first.")
            sys.exit(1)

    # Check if already a git repository
    if os.path.exists('.git'):
        print("📁 Git repository already exists.")
    else:
        # Initialize Git repository
        if not run_command("git init", "Initializing Git repository"):
            sys.exit(1)

    # Add all files
    if not run_command("git add .", "Adding files to Git"):
        sys.exit(1)

    # Initial commit
    commit_message = "Initial commit: Laundry Shop Management System"
    if not run_command(f'git commit -m "{commit_message}"', "Creating initial commit"):
        sys.exit(1)

    print("\n🎉 Git setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Create a new repository on GitHub (https://github.com/new)")
    print("2. Copy the repository URL")
    print("3. Run the following commands:")
    print("   git remote add origin <your-repo-url>")
    print("   git branch -M main")
    print("   git push -u origin main")
    print("\n🔒 Security Reminder:")
    print("- Your .env file is automatically ignored by .gitignore")
    print("- Never commit sensitive information to Git")
    print("- Keep your .env file private and secure")

if __name__ == "__main__":
    main()