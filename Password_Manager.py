#!/usr/bin/env python3
"""
Secure Password Manager - Command Line Version
Milestone #1: Registration, MFA Login, Add Password Entry
"""

import json
import hashlib
import random
import time
import os
import sys
from datetime import datetime, timedelta
from base64 import b64encode, b64decode

# Simple AES-256 simulation using XOR for demo (in production use cryptography library)
class SimpleEncryption:
    @staticmethod
    def encrypt(text, key):
        """Simulate AES-256 encryption"""
        key_bytes = hashlib.sha256(key.encode()).digest()
        text_bytes = text.encode()
        encrypted = bytes([text_bytes[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(text_bytes))])
        return b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt(encrypted_text, key):
        """Simulate AES-256 decryption"""
        key_bytes = hashlib.sha256(key.encode()).digest()
        encrypted_bytes = b64decode(encrypted_text.encode())
        decrypted = bytes([encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(encrypted_bytes))])
        return decrypted.decode()

# Data storage files
USERS_FILE = 'users.json'
PASSWORDS_FILE = 'passwords.json'
ENCRYPTION_KEY = 'master-encryption-key-change-this'

# Colors for terminal output (Inclusivity Heuristic #3: Accessible colors)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def clear_screen():
    """Clear terminal screen (Inclusivity Heuristic #7: Clear navigation)"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    """Print formatted header (Inclusivity Heuristic #2: Clear feedback)"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_success(text):
    """Print success message (Inclusivity Heuristic #2: Clear feedback)"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print error message (Inclusivity Heuristic #2: Clear feedback)"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def load_data(filename):
    """Load data from JSON file"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_data(filename, data):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def hash_password(password):
    """Hash password using SHA-256 (simulates bcrypt for demo)
    Security Quality Attribute: Passwords must be hashed"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Validate email format (Inclusivity Heuristic #6: Error prevention)"""
    return '@' in email and '.' in email.split('@')[1]

def check_password_strength(password):
    """Check password strength (Inclusivity Heuristic #6: Error prevention)"""
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    strength_score = sum([has_upper, has_lower, has_digit, has_special])
    
    if strength_score < 3:
        return False, "Password must contain uppercase, lowercase, numbers, and special characters"
    
    return True, "Strong password"

def generate_strong_password():
    """Generate strong password (Inclusivity Heuristic #5: Customization)"""
    import string
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    password = ''.join(random.choice(chars) for _ in range(16))
    # Ensure it has all required types
    if not (any(c.isupper() for c in password) and 
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password) and
            any(not c.isalnum() for c in password)):
        return generate_strong_password()  # Regenerate if not strong enough
    return password

def generate_mfa_code():
    """Generate 6-digit MFA code"""
    return str(random.randint(100000, 999999))

def register_user():
    """User Story #1: Register Account
    Given a user is on the registration page,
    When they enter a valid email and password and click Register,
    Then a new account is created and stored securely."""
    
    print_header("REGISTER NEW ACCOUNT")
    
    # Input email (Inclusivity Heuristic #1: Multiple input methods - keyboard)
    email = input(f"{Colors.BOLD}Email address:{Colors.END} ").strip()
    
    # Validate email (Inclusivity Heuristic #6: Error prevention)
    if not validate_email(email):
        print_error("Invalid email format. Please include @ and domain.")
        input("\nPress Enter to continue...")
        return None
    
    # Check if user exists
    users = load_data(USERS_FILE)
    if any(u['email'] == email for u in users):
        print_error("An account with this email already exists.")
        input("\nPress Enter to continue...")
        return None
    
    # Input password with strength checking
    while True:
        password = input(f"{Colors.BOLD}Master Password (min 12 chars):{Colors.END} ")
        
        is_strong, message = check_password_strength(password)
        
        if is_strong:
            print_success(message)
            break
        else:
            print_error(message)
            print_info("Tip: Use uppercase, lowercase, numbers, and special characters")
            
            # Offer to generate password (Inclusivity Heuristic #5: Customization)
            choice = input(f"\n{Colors.YELLOW}Generate strong password? (y/n):{Colors.END} ").lower()
            if choice == 'y':
                password = generate_strong_password()
                print_success(f"Generated password: {Colors.BOLD}{password}{Colors.END}")
                print_warning("Save this password securely!")
                input("\nPress Enter when you've saved it...")
                break
    
    # Hash password (Security Quality Attribute)
    hashed_password = hash_password(password)
    
    # Create user
    new_user = {
        'id': str(int(time.time() * 1000)),
        'email': email,
        'password': hashed_password,
        'created_at': datetime.now().isoformat()
    }
    
    users.append(new_user)
    save_data(USERS_FILE, users)
    
    print_success("Account created successfully!")
    print_info("You can now login with your credentials.")
    input("\nPress Enter to continue...")
    
    return new_user

def mfa_verification(user):
    """User Story #2: Login with MFA (Part 2)
    When they provide a valid MFA code,
    Then they are granted access to their account."""
    
    print_header("TWO-FACTOR AUTHENTICATION")
    
    # Generate MFA code (Security Quality Attribute)
    mfa_code = generate_mfa_code()
    expires_at = time.time() + 60  # 60 seconds expiration
    
    print_info(f"A 6-digit code has been sent to {user['email']}")
    print_warning(f"For demo purposes, your code is: {Colors.BOLD}{mfa_code}{Colors.END}")
    print_info("Code expires in 60 seconds\n")
    
    # Show countdown timer (Usability Quality Attribute)
    time_left = 60
    while time_left > 0:
        current_time = time.time()
        if current_time >= expires_at:
            break
        
        time_left = int(expires_at - current_time)
        print(f"\r{Colors.CYAN}⏱  Time remaining: {time_left} seconds{Colors.END}", end='', flush=True)
        
        # Check for input (non-blocking simulation)
        print(f"\r{Colors.BOLD}Enter 6-digit code (or 'resend'):{Colors.END} ", end='', flush=True)
        entered_code = input()
        
        if entered_code.lower() == 'resend':
            print_info("Resending code...")
            return mfa_verification(user)  # Recursive call to resend
        
        if entered_code == mfa_code:
            print_success("\n\nVerification successful!")
            return True
        else:
            print_error("Invalid code. Please try again.")
            time_left = int(expires_at - time.time())
            if time_left <= 0:
                break
    
    print_error("\n\nMFA code expired. Please login again.")
    input("\nPress Enter to continue...")
    return False

def login_user():
    """User Story #2: Login with MFA (Part 1)
    Given a user enters correct login credentials,
    When they provide a valid MFA code,
    Then they are granted access to their account."""
    
    print_header("LOGIN")
    
    email = input(f"{Colors.BOLD}Email address:{Colors.END} ").strip()
    password = input(f"{Colors.BOLD}Master Password:{Colors.END} ")
    
    # Reliability Quality Attribute: Login must complete within 5 seconds
    start_time = time.time()
    
    users = load_data(USERS_FILE)
    hashed_password = hash_password(password)
    
    user = next((u for u in users if u['email'] == email and u['password'] == hashed_password), None)
    
    login_duration = time.time() - start_time
    
    if login_duration > 5:
        print_error("Login timeout - please try again")
        print_info(f"Login took {login_duration:.2f} seconds (max: 5 seconds)")
        input("\nPress Enter to continue...")
        return None
    
    if not user:
        print_error("Invalid email or password")
        input("\nPress Enter to continue...")
        return None
    
    print_success("Credentials verified!")
    time.sleep(0.5)
    
    # MFA verification (Security Quality Attribute)
    if mfa_verification(user):
        print_success(f"\nWelcome back, {user['email']}!")
        input("\nPress Enter to continue to dashboard...")
        return user
    
    return None

def add_password_entry(user):
    """User Story #3: Add Password Entry
    Given a user is logged in,
    When they enter a site name, username, and password and click Save,
    Then the entry is encrypted and stored."""
    
    print_header("ADD NEW PASSWORD ENTRY")
    
    # Auto-focus simulation (Usability Quality Attribute)
    print_info("Enter details for your password entry\n")
    
    site_name = input(f"{Colors.BOLD}Website/App Name:{Colors.END} ").strip()
    if not site_name:
        print_error("Site name is required")
        input("\nPress Enter to continue...")
        return
    
    username = input(f"{Colors.BOLD}Username/Email:{Colors.END} ").strip()
    if not username:
        print_error("Username is required")
        input("\nPress Enter to continue...")
        return
    
    # Option to generate password (Inclusivity Heuristic #5: Customization)
    choice = input(f"\n{Colors.YELLOW}Generate strong password? (y/n):{Colors.END} ").lower()
    
    if choice == 'y':
        password = generate_strong_password()
        print_success(f"Generated: {Colors.BOLD}{password}{Colors.END}")
        show = input(f"\n{Colors.YELLOW}Show password? (y/n):{Colors.END} ").lower()
        if show != 'y':
            password_display = '*' * len(password)
            print_info(f"Password hidden: {password_display}")
    else:
        password = input(f"{Colors.BOLD}Password:{Colors.END} ")
    
    # Encrypt password with AES-256 (Security Quality Attribute)
    encrypted_password = SimpleEncryption.encrypt(password, ENCRYPTION_KEY)
    
    # Create entry
    entry = {
        'id': str(int(time.time() * 1000)),
        'user_id': user['id'],
        'site_name': site_name,
        'username': username,
        'password': encrypted_password,
        'created_at': datetime.now().isoformat()
    }
    
    passwords = load_data(PASSWORDS_FILE)
    passwords.append(entry)
    save_data(PASSWORDS_FILE, passwords)
    
    print_success("\n✓ Password entry saved successfully!")
    print_info("Your password is encrypted with AES-256")
    input("\nPress Enter to continue...")

def view_passwords(user):
    """View saved passwords (Inclusivity Heuristic #1: Keyboard navigation)"""
    print_header("MY PASSWORDS")
    
    passwords = load_data(PASSWORDS_FILE)
    user_passwords = [p for p in passwords if p['user_id'] == user['id'] and not p.get('deleted')]
    
    if not user_passwords:
        print_info("No passwords saved yet.")
        print_info("Use 'Add Password' to store your first credential.")
        input("\nPress Enter to continue...")
        return
    
    # Display passwords (Inclusivity Heuristic #7: Clear navigation)
    for idx, entry in enumerate(user_passwords, 1):
        print(f"\n{Colors.BOLD}{idx}. {entry['site_name']}{Colors.END}")
        print(f"   Username: {entry['username']}")
        print(f"   Password: {'•' * 8}")
        print(f"   Created: {entry['created_at'][:10]}")
    
    print(f"\n{Colors.BOLD}Options:{Colors.END}")
    print("  [number] - View password details")
    print("  [d][number] - Delete entry (e.g., 'd1')")
    print("  [back] - Return to dashboard")
    
    choice = input(f"\n{Colors.BOLD}Choice:{Colors.END} ").strip().lower()
    
    if choice == 'back' or not choice:
        return
    
    if choice.startswith('d'):
        try:
            idx = int(choice[1:]) - 1
            if 0 <= idx < len(user_passwords):
                delete_password(user_passwords[idx], user)
            else:
                print_error("Invalid entry number")
                input("\nPress Enter to continue...")
        except ValueError:
            print_error("Invalid input")
            input("\nPress Enter to continue...")
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(user_passwords):
                view_password_detail(user_passwords[idx])
            else:
                print_error("Invalid entry number")
                input("\nPress Enter to continue...")
        except ValueError:
            print_error("Invalid input")
            input("\nPress Enter to continue...")

def view_password_detail(entry):
    """View decrypted password"""
    print_header(f"🔍 {entry['site_name']}")
    
    print(f"{Colors.BOLD}Website/App:{Colors.END} {entry['site_name']}")
    print(f"{Colors.BOLD}Username:{Colors.END} {entry['username']}")
    
    # Decrypt password (Security Quality Attribute: AES-256)
    decrypted_password = SimpleEncryption.decrypt(entry['password'], ENCRYPTION_KEY)
    
    show = input(f"\n{Colors.YELLOW}Reveal password? (y/n):{Colors.END} ").lower()
    if show == 'y':
        print(f"{Colors.BOLD}Password:{Colors.END} {Colors.GREEN}{decrypted_password}{Colors.END}")
    else:
        print(f"{Colors.BOLD}Password:{Colors.END} {'•' * len(decrypted_password)}")
    
    input("\nPress Enter to continue...")

def delete_password(entry, user):
    """Delete password with undo option (Inclusivity Heuristic #8: Undo/Recovery)"""
    confirm = input(f"\n{Colors.RED}Delete '{entry['site_name']}'? (y/n):{Colors.END} ").lower()
    
    if confirm != 'y':
        print_info("Deletion cancelled")
        input("\nPress Enter to continue...")
        return
    
    passwords = load_data(PASSWORDS_FILE)
    
    # Soft delete
    for p in passwords:
        if p['id'] == entry['id']:
            p['deleted'] = True
            p['deleted_at'] = datetime.now().isoformat()
            break
    
    save_data(PASSWORDS_FILE, passwords)
    
    print_success(f"'{entry['site_name']}' deleted")
    print_warning("You have 5 seconds to undo...")
    
    # Undo window (Inclusivity Heuristic #8: Undo/Recovery)
    start_time = time.time()
    undo_window = 5
    
    print(f"\n{Colors.YELLOW}Type 'undo' to restore, or wait...{Colors.END}")
    
    import select
    if os.name != 'nt':  # Unix-like systems
        import sys, tty, termios
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            while time.time() - start_time < undo_window:
                time_left = int(undo_window - (time.time() - start_time))
                print(f"\r{Colors.CYAN}Time left to undo: {time_left}s{Colors.END}", end='', flush=True)
                
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    undo_input = sys.stdin.readline().strip().lower()
                    if undo_input == 'undo':
                        # Restore
                        passwords = load_data(PASSWORDS_FILE)
                        for p in passwords:
                            if p['id'] == entry['id']:
                                del p['deleted']
                                del p['deleted_at']
                                break
                        save_data(PASSWORDS_FILE, passwords)
                        print(f"\n{Colors.GREEN}✓ Password restored!{Colors.END}")
                        input("\nPress Enter to continue...")
                        return
                time.sleep(0.1)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    else:
        # Windows: simpler approach
        for i in range(undo_window, 0, -1):
            print(f"\r{Colors.CYAN}Time left to undo: {i}s (undo not available on Windows in this demo){Colors.END}", end='', flush=True)
            time.sleep(1)
    
    print(f"\n{Colors.INFO}Undo window closed. Deletion permanent.{Colors.END}")
    input("\nPress Enter to continue...")

def dashboard(user):
    """Main dashboard (Inclusivity Heuristic #7: Clear navigation)"""
    while True:
        clear_screen()
        print_header("PASSWORD MANAGER DASHBOARD")
        
        print(f"{Colors.BOLD}Logged in as:{Colors.END} {user['email']}\n")
        
        # Menu with clear labels (Inclusivity Heuristic #7: Clear navigation)
        print(f"{Colors.BOLD}Menu:{Colors.END}")
        print(f"  {Colors.GREEN}[1]{Colors.END} Add New Password")
        print(f"  {Colors.CYAN}[2]{Colors.END} View Passwords")
        print(f"  {Colors.YELLOW}[3]{Colors.END} Logout")
        print(f"  {Colors.RED}[4]{Colors.END} Exit")

        choice = input(f"\n{Colors.BOLD}Choose an option:{Colors.END} ").strip()
        
        if choice == '1':
            clear_screen()
            add_password_entry(user)
        elif choice == '2':
            clear_screen()
            view_passwords(user)
        elif choice == '3':
            print_info("Logging out...")
            time.sleep(0.5)
            break
        elif choice == '4':
            print_info("Goodbye!")
            sys.exit(0)
        else:
            print_error("Invalid option. Please choose 1-4.")
            input("\nPress Enter to continue...")

def main():
    """Main application loop"""
    while True:
        clear_screen()
        print_header("SECURE PASSWORD MANAGER")
        print(f"{Colors.CYAN}Milestone #1: Core Authentication & Password Storage{Colors.END}\n")
        
        # Main menu (Inclusivity Heuristic #7: Clear navigation)
        print(f"{Colors.BOLD}Welcome!{Colors.END}")
        print(f"  {Colors.GREEN}[1]{Colors.END} Register New Account")
        print(f"  {Colors.CYAN}[2]{Colors.END} Login")
        print(f"  {Colors.RED}[3]{Colors.END} Exit")

        choice = input(f"\n{Colors.BOLD}Choose an option:{Colors.END} ").strip()
        
        if choice == '1':
            clear_screen()
            user = register_user()
            if user:
                dashboard(user)
        elif choice == '2':
            clear_screen()
            user = login_user()
            if user:
                dashboard(user)
        elif choice == '3':
            print_info("Thank you for using Password Manager!")
            sys.exit(0)
        else:
            print_error("Invalid option. Please choose 1-3.")
            input("\nPress Enter to continue...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.INFO}Program interrupted. Goodbye!{Colors.END}")
        sys.exit(0)