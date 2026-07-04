"""
Demo script for Leave Management System
Shows how to use the system programmatically
"""

from leave_management_system import LeaveManagementSystem
from datetime import datetime, timedelta


def demo():
    """Run a demonstration of the leave management system."""
    
    print("\n" + "="*70)
    print("LEAVE MANAGEMENT SYSTEM - DEMO")
    print("="*70)
    
    # Initialize system
    system = LeaveManagementSystem("demo_leave_system.json")
    
    # Demo 1: Add Employees
    print("\n[DEMO 1] Adding Employees to the System...")
    print("-" * 70)
    
    employees = [
        ("EMP001", "John Doe", "Senior Developer", "IT"),
        ("EMP002", "Jane Smith", "Project Manager", "Project Management"),
        ("EMP003", "Alice Johnson", "HR Manager", "Human Resources"),
        ("EMP004", "Bob Wilson", "QA Engineer", "Quality Assurance"),
    ]
    
    for emp_id, name, designation, department in employees:
        system.add_employee(emp_id, name, designation, department)
    
    # Demo 2: List all employees
    print("\n[DEMO 2] Listing All Employees...")
    print("-" * 70)
    system.list_all_employees()
    
    # Demo 3: View leave balance
    print("\n[DEMO 3] Viewing Leave Balance for EMP001...")
    print("-" * 70)
    system.view_leave_balance("EMP001")
    
    # Demo 4: Apply for leave
    print("\n[DEMO 4] Applying for Leave...")
    print("-" * 70)
    
    today = datetime.now()
    
    # Leave request 1: Sick leave
    start1 = (today + timedelta(days=5)).strftime("%Y-%m-%d")
    end1 = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    system.apply_leave("EMP001", "SL", start1, end1, "Medical checkup")
    
    # Leave request 2: Casual leave
    start2 = (today + timedelta(days=15)).strftime("%Y-%m-%d")
    end2 = (today + timedelta(days=17)).strftime("%Y-%m-%d")
    system.apply_leave("EMP002", "CL", start2, end2, "Family trip")
    
    # Leave request 3: Paid leave
    start3 = (today + timedelta(days=25)).strftime("%Y-%m-%d")
    end3 = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    system.apply_leave("EMP003", "PL", start3, end3, "Vacation")
    
    # Demo 5: View pending requests
    print("\n[DEMO 5] Viewing Pending Leave Requests...")
    print("-" * 70)
    system.view_pending_requests()
    
    # Demo 6: View employee-specific requests
    print("\n[DEMO 6] Viewing All Requests for Employee EMP001...")
    print("-" * 70)
    system.view_employee_requests("EMP001")
    
    # Demo 7: Approve a leave request
    print("\n[DEMO 7] Approving Leave Request...")
    print("-" * 70)
    system.approve_leave_request("LR00001", "Alice Johnson", "Approved - Medical certificate verified")
    
    # Demo 8: View leave balance after approval
    print("\n[DEMO 8] Viewing Updated Leave Balance for EMP001...")
    print("-" * 70)
    system.view_leave_balance("EMP001")
    
    # Demo 9: View leave request details
    print("\n[DEMO 9] Viewing Leave Request Details...")
    print("-" * 70)
    system.view_leave_request("LR00001")
    
    # Demo 10: Reject a leave request
    print("\n[DEMO 10] Rejecting a Leave Request...")
    print("-" * 70)
    system.reject_leave_request("LR00002", "Alice Johnson", "Not approved - Insufficient staffing")
    
    # Demo 11: View pending requests after approval/rejection
    print("\n[DEMO 11] Updated Pending Requests...")
    print("-" * 70)
    system.view_pending_requests()
    
    # Demo 12: View all leave types
    print("\n[DEMO 12] Available Leave Types...")
    print("-" * 70)
    print("Leave Types: SL (Sick Leave), CL (Casual Leave), PL (Paid Leave), UL (Unpaid Leave), ML (Maternity Leave)")
    
    print("\n" + "="*70)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nData has been saved to 'demo_leave_system.json'")


if __name__ == "__main__":
    demo()
