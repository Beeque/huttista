#!/usr/bin/env python3
"""
Quick test runner for NHL HUT Builder Cards Monitor
Runs one monitoring cycle to test functionality
"""

import sys
import time
from cards_monitor_console import CardsMonitorConsole

def main():
    print("🧪 NHL HUT Builder Cards Monitor - Quick Test")
    print("=" * 60)
    print("Running one monitoring cycle to test functionality")
    print("This will check for new cards and show the process")
    print("=" * 60)
    
    try:
        # Create monitor instance
        monitor = CardsMonitorConsole()
        
        # Run one cycle
        monitor.run_monitoring_cycle()
        
        print("\n✅ Test completed successfully!")
        print("💡 If this worked, the full monitor should work too.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("💡 Check the error message and fix any issues.")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    if success:
        print("\n🚀 Ready to run the full monitor!")
        print("💡 Run 'python cards_monitor_console.py' for console version")
        print("💡 Or build executables with 'python build_executables.py'")
    else:
        print("\n⚠️ Please fix issues before running the full monitor")