"""
Clean command implementation.
"""

import shutil
from cli.core import print_section_header, print_status_bar
from cli.utils import list_temp_profiles

def command_clean(args):
    """Clean up temporary files and profiles."""
    print_section_header("Cleanup Operations")
    
    if args.all:
        args.temp_profiles = True
        args.cache = True
        args.logs = True
    
    operations = []
    if args.temp_profiles:
        operations.append("temporary profiles")
    if args.cache:
        operations.append("browser cache")
    if args.logs:
        operations.append("log files")
    
    if not operations:
        print_status_bar("No cleanup operations specified", "WARNING")
        print("💡 Use --temp-profiles, --cache, --logs, or --all")
        return True
    
    print(f"🧹 Cleanup operations: {', '.join(operations)}")
    
    if args.dry_run:
        print_status_bar("DRY RUN - No files will be actually removed", "INFO")
    
    if not args.force and not args.dry_run:
        confirm = input("\nProceed with cleanup? (y/N): ")
        if confirm.lower() not in ['y', 'yes']:
            print_status_bar("Cleanup cancelled", "INFO")
            return True
    
    success = True
    
    if args.temp_profiles:
        success &= cleanup_temp_profiles(args.dry_run)
    
    if args.cache:
        success &= cleanup_cache(args.dry_run)
    
    if args.logs:
        success &= cleanup_logs(args.dry_run)
    
    if success:
        print_status_bar("Cleanup completed successfully", "SUCCESS")
    else:
        print_status_bar("Cleanup completed with some errors", "WARNING")
    
    return success

def cleanup_temp_profiles(dry_run: bool = False) -> bool:
    """Clean up temporary profiles."""
    print_status_bar("Cleaning temporary profiles...", "PROGRESS")
    
    temp_profiles = list_temp_profiles()
    if not temp_profiles:
        print_status_bar("No temporary profiles to clean", "INFO")
        return True
    
    success = True
    for profile in temp_profiles:
        try:
            if dry_run:
                print(f"  Would remove: {profile}")
            else:
                shutil.rmtree(profile)
                print(f"  Removed: {profile}")
        except Exception as e:
            print_status_bar(f"Failed to remove {profile}: {str(e)}", "ERROR")
            success = False
    
    return success

def cleanup_cache(dry_run: bool = False) -> bool:
    """Clean up browser cache."""
    print_status_bar("Cleaning browser cache...", "PROGRESS")
    
    if dry_run:
        print("  Would clear browser cache files")
    else:
        print_status_bar("Cache cleanup not yet implemented", "WARNING")
    
    return True

def cleanup_logs(dry_run: bool = False) -> bool:
    """Clean up log files."""
    print_status_bar("Cleaning log files...", "PROGRESS")
    
    if dry_run:
        print("  Would remove log files")
    else:
        print_status_bar("Log cleanup not yet implemented", "WARNING")
    
    return True
