#!/usr/bin/env python3
"""
Test script to verify the fruit fly database functionality.
This tests the simplified fruit fly assessment system.
"""

from tas_data import fruit_fly_db

def test_fruit_fly_database():
    """Test the fruit fly database functionality."""
    print("🧪 Testing Fruit Fly Database...")
    print("=" * 50)
    
    # Test 1: Check if fruit flies are loaded
    print("1. Testing fruit fly data loading:")
    qff = fruit_fly_db.get_fruit_fly_info("QFF")
    mff = fruit_fly_db.get_fruit_fly_info("MFF")
    
    if qff:
        print(f"✅ QFF loaded: {qff.common_name} ({len(qff.hosts)} hosts)")
    else:
        print("❌ QFF not loaded")
    
    if mff:
        print(f"✅ MFF loaded: {mff.common_name} ({len(mff.hosts)} hosts)")
    else:
        print("❌ MFF not loaded")
    
    print()

def test_commodity_lookup():
    """Test commodity lookup functionality."""
    print("2. Testing commodity lookup:")
    
    test_commodities = [
        "grape",  # Changed from "table grapes"
        "apple",
        "sweet orange",  # Changed from "citrus"
        "banana",
        "tomato"
    ]
    
    for commodity in test_commodities:
        info = fruit_fly_db.get_commodity_info(commodity)
        if info:
            print(f"✅ {commodity}: QFF={info.qff_host}, MFF={info.mff_host}")
        else:
            print(f"❌ {commodity}: Not found")
    
    print()

def test_state_presence():
    """Test state presence checking."""
    print("3. Testing state presence:")
    
    test_states = ["NSW", "VIC", "WA", "SA", "TAS"]
    
    for state in test_states:
        qff_present = fruit_fly_db.is_pest_present_in_state("QFF", state)
        mff_present = fruit_fly_db.is_pest_present_in_state("MFF", state)
        print(f"✅ {state}: QFF={qff_present}, MFF={mff_present}")
    
    print()

def test_risk_assessment():
    """Test risk assessment functionality."""
    print("4. Testing risk assessment:")
    
    test_cases = [
        ("grape", "NSW"),  # Changed from "table grapes"
        ("grape", "WA"),   # Changed from "table grapes"
        ("grape", "TAS"),  # Changed from "table grapes"
        ("apple", "NSW"),         # Should have QFF risk
        ("apple", "WA"),          # Should have MFF risk
        ("banana", "VIC"),        # Should have QFF risk
    ]
    
    for commodity, state in test_cases:
        assessment = fruit_fly_db.assess_fruit_fly_risk(commodity, state)
        if "error" not in assessment:
            risk_level = "HIGH" if assessment["qff_risk"] or assessment["mff_risk"] else "LOW"
            print(f"✅ {commodity} from {state}: {risk_level} risk")
            if assessment["risk_details"]:
                for detail in assessment["risk_details"]:
                    print(f"   - {detail}")
        else:
            print(f"❌ {commodity} from {state}: {assessment['error']}")
    
    print()

def test_host_lists():
    """Test host list generation."""
    print("5. Testing host lists by state:")
    
    test_states = ["NSW", "WA", "TAS"]
    
    for state in test_states:
        hosts = fruit_fly_db.get_fruit_fly_hosts_for_state(state)
        print(f"✅ {state}:")
        if hosts["QFF"]:
            print(f"   QFF hosts: {len(hosts['QFF'])} (e.g., {hosts['QFF'][:3]})")
        if hosts["MFF"]:
            print(f"   MFF hosts: {len(hosts['MFF'])} (e.g., {hosts['MFF'][:3]})")
        if not hosts["QFF"] and not hosts["MFF"]:
            print("   No fruit fly hosts")
    
    print()

def main():
    """Run all tests."""
    print("🧪 Testing Fruit Fly Assessment System...")
    print("=" * 50)
    
    test_fruit_fly_database()
    test_commodity_lookup()
    test_state_presence()
    test_risk_assessment()
    test_host_lists()
    
    print("=" * 50)
    print("✅ Fruit fly database tests completed!")
    print("\nNext steps:")
    print("1. Test with the agent: python agent_setup_tas.py")
    print("2. Try different commodities and states to see risk assessment in action")

if __name__ == "__main__":
    main() 