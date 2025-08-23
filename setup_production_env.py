#!/usr/bin/env python3
"""
Production Environment Setup Script
This script helps you set up production environment files for Railway and Vercel
"""

import os
import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure random secret key"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def setup_backend_production():
    """Set up backend production environment file"""
    print("🔧 Setting up Backend Production Environment...")
    
    # Read the template
    template_file = "Backend/env.production.ready"
    if not os.path.exists(template_file):
        print(f"❌ Template file {template_file} not found!")
        return
    
    with open(template_file, 'r') as f:
        content = f.read()
    
    # Generate a secure secret key
    secret_key = generate_secret_key(50)
    content = content.replace("your-super-secret-key-here-change-this-to-a-strong-random-string", secret_key)
    
    # Write the production file
    output_file = "Backend/.env.production"
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Backend production environment file created: {output_file}")
    print(f"🔑 Generated secure SECRET_KEY: {secret_key[:20]}...")
    print("📝 Edit this file with your actual production values!")

def setup_frontend_production():
    """Set up frontend production environment file"""
    print("🔧 Setting up Frontend Production Environment...")
    
    # Read the template
    template_file = "frontend/env.production.ready"
    if not os.path.exists(template_file):
        print(f"❌ Template file {template_file} not found!")
        return
    
    with open(template_file, 'r') as f:
        content = f.read()
    
    # Write the production file
    output_file = "frontend/.env.production"
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Frontend production environment file created: {output_file}")
    print("📝 Edit this file with your actual production values!")

def main():
    """Main setup function"""
    print("🚀 Production Environment Setup Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("Backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the root of your mail_merge_kit project!")
        return
    
    print("📁 Setting up production environment files...")
    print()
    
    # Set up backend
    setup_backend_production()
    print()
    
    # Set up frontend
    setup_frontend_production()
    print()
    
    print("🎉 Production environment setup complete!")
    print()
    print("📋 Next steps:")
    print("1. Edit Backend/.env.production with your Railway credentials")
    print("2. Edit frontend/.env.production with your Vercel credentials")
    print("3. Deploy to Railway and Vercel")
    print("4. Set environment variables in your hosting platforms")
    print()
    print("📚 See ENVIRONMENT_SETUP.md for detailed instructions")

if __name__ == "__main__":
    main()
