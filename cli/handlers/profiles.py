"""
Profiles command implementation.
"""

import shutil
from cli.core import print_section_header, print_status_bar
from cli.utils import list_debug_profiles, list_temp_profiles

def command_profiles(args):
    """Manage browser profiles."""
    print_section_header("Profile Management")
    
    if args.list:
        print("🔍 Available Profiles:")
        debug_profiles = list_debug_profiles()
        temp_profiles = list_temp_profiles()
        
        print(f"\n📁 Debug Profiles ({len(debug_profiles)}):")
        for i, profile in enumerate(debug_profiles, 1):
            print(f"  {i}. {profile}")
        
        print(f"\n🗂️  Temporary Profiles ({len(temp_profiles)}):")
        for i, profile in enumerate(temp_profiles, 1):
            print(f"  {i}. {profile}")
        
        if not debug_profiles and not temp_profiles:
            print("  No profiles found")
    
    elif args.clean:
        print("🧹 Cleaning up old profiles...")
        temp_profiles = list_temp_profiles()
        
        if not temp_profiles:
            print_status_bar("No temporary profiles to clean", "INFO")
            return True
        
        print(f"Found {len(temp_profiles)} temporary profiles to clean:")
        for profile in temp_profiles:
            print(f"  • {profile}")
        
        if not args.force:
            confirm = input("\nProceed with cleanup? (y/N): ")
            if confirm.lower() not in ['y', 'yes']:
                print_status_bar("Cleanup cancelled", "INFO")
                return True
        
        cleaned = 0
        for profile in temp_profiles:
            try:
                shutil.rmtree(profile)
                cleaned += 1
                print_status_bar(f"Removed: {profile}", "SUCCESS")
            except Exception as e:
                print_status_bar(f"Failed to remove {profile}: {str(e)}", "ERROR")
        
        print_status_bar(f"Cleaned up {cleaned}/{len(temp_profiles)} profiles", "SUCCESS")
    
    elif args.create:
        print(f"📝 Creating new profile: {args.create}")
        # Profile creation logic would go here
        print_status_bar("Profile creation not yet implemented", "WARNING")
    
    elif args.remove:
        print(f"🗑️  Removing profile: {args.remove}")
        # Profile removal logic would go here
        print_status_bar("Profile removal not yet implemented", "WARNING")
    
    elif args.info:
        print(f"ℹ️  Profile information: {args.info}")
        # Profile info logic would go here
        print_status_bar("Profile info not yet implemented", "WARNING")
    
    else:
        print("💡 Use --list to see available profiles")
        print("   Use --clean to remove temporary profiles")
    
    return True
