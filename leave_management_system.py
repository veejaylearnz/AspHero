"""
Leave Management System
A comprehensive system to manage employee leaves, requests, and tracking.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class Employee:
    """Represents an employee in the system."""
    
    def __init__(self, emp_id: str, name: str, designation: str, department: str):
        self.emp_id = emp_id
        self.name = name
        self.designation = designation
        self.department = department
        self.join_date = datetime.now().strftime("%Y-%m-%d")
    
    def to_dict(self) -> Dict:
        return {
            'emp_id': self.emp_id,
            'name': self.name,
            'designation': self.designation,
            'department': self.department,
            'join_date': self.join_date
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Employee':
        emp = Employee(data['emp_id'], data['name'], data['designation'], data['department'])
        emp.join_date = data.get('join_date', emp.join_date)
        return emp


class LeaveType:
    """Represents different types of leaves available."""
    
    LEAVE_TYPES = {
        'SL': {'name': 'Sick Leave', 'days_per_year': 10},
        'CL': {'name': 'Casual Leave', 'days_per_year': 12},
        'PL': {'name': 'Paid Leave', 'days_per_year': 20},
        'UL': {'name': 'Unpaid Leave', 'days_per_year': 5},
        'ML': {'name': 'Maternity Leave', 'days_per_year': 90}
    }
    
    @classmethod
    def get_all_types(cls) -> Dict:
        return cls.LEAVE_TYPES
    
    @classmethod
    def get_leave_type_name(cls, leave_code: str) -> str:
        return cls.LEAVE_TYPES.get(leave_code, {}).get('name', 'Unknown')


class LeaveBalance:
    """Tracks leave balance for each employee and leave type."""
    
    def __init__(self, emp_id: str):
        self.emp_id = emp_id
        self.balance = {}
        # Initialize balance for all leave types
        for code, details in LeaveType.LEAVE_TYPES.items():
            self.balance[code] = details['days_per_year']
    
    def get_balance(self, leave_type: str) -> int:
        return self.balance.get(leave_type, 0)
    
    def deduct_leave(self, leave_type: str, days: int) -> bool:
        if self.get_balance(leave_type) >= days:
            self.balance[leave_type] -= days
            return True
        return False
    
    def add_leave(self, leave_type: str, days: int):
        """Add leaves back (in case of cancellation)."""
        if leave_type in self.balance:
            self.balance[leave_type] += days
    
    def to_dict(self) -> Dict:
        return {
            'emp_id': self.emp_id,
            'balance': self.balance
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'LeaveBalance':
        lb = LeaveBalance(data['emp_id'])
        lb.balance = data.get('balance', lb.balance)
        return lb


class LeaveRequest:
    """Represents a leave request from an employee."""
    
    REQUEST_COUNTER = 0
    
    def __init__(self, emp_id: str, leave_type: str, start_date: str, end_date: str, reason: str):
        LeaveRequest.REQUEST_COUNTER += 1
        self.request_id = f"LR{LeaveRequest.REQUEST_COUNTER:05d}"
        self.emp_id = emp_id
        self.leave_type = leave_type
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason
        self.status = 'PENDING'  # PENDING, APPROVED, REJECTED
        self.request_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.approval_date = None
        self.approved_by = None
        self.comments = ""
    
    def get_days(self) -> int:
        """Calculate number of days requested."""
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.strptime(self.end_date, "%Y-%m-%d")
        return (end - start).days + 1
    
    def approve(self, approved_by: str, comments: str = ""):
        self.status = 'APPROVED'
        self.approval_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.approved_by = approved_by
        self.comments = comments
    
    def reject(self, approved_by: str, comments: str = ""):
        self.status = 'REJECTED'
        self.approval_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.approved_by = approved_by
        self.comments = comments
    
    def to_dict(self) -> Dict:
        return {
            'request_id': self.request_id,
            'emp_id': self.emp_id,
            'leave_type': self.leave_type,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'reason': self.reason,
            'status': self.status,
            'request_date': self.request_date,
            'approval_date': self.approval_date,
            'approved_by': self.approved_by,
            'comments': self.comments,
            'days': self.get_days()
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'LeaveRequest':
        lr = LeaveRequest(data['emp_id'], data['leave_type'], 
                         data['start_date'], data['end_date'], data['reason'])
        lr.request_id = data['request_id']
        lr.status = data['status']
        lr.request_date = data['request_date']
        lr.approval_date = data.get('approval_date')
        lr.approved_by = data.get('approved_by')
        lr.comments = data.get('comments', '')
        return lr


class LeaveManagementSystem:
    """Main system for managing leaves."""
    
    def __init__(self, data_file: str = "leave_system_data.json"):
        self.data_file = data_file
        self.employees: Dict[str, Employee] = {}
        self.leave_balances: Dict[str, LeaveBalance] = {}
        self.leave_requests: Dict[str, LeaveRequest] = {}
        self.load_data()
    
    def load_data(self):
        """Load data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Load employees
                for emp_data in data.get('employees', []):
                    emp = Employee.from_dict(emp_data)
                    self.employees[emp.emp_id] = emp
                
                # Load leave balances
                for balance_data in data.get('leave_balances', []):
                    lb = LeaveBalance.from_dict(balance_data)
                    self.leave_balances[lb.emp_id] = lb
                
                # Load leave requests
                for request_data in data.get('leave_requests', []):
                    lr = LeaveRequest.from_dict(request_data)
                    self.leave_requests[lr.request_id] = lr
                
                print("✓ Data loaded successfully!")
            except Exception as e:
                print(f"Error loading data: {e}")
    
    def save_data(self):
        """Save data to JSON file."""
        try:
            data = {
                'employees': [emp.to_dict() for emp in self.employees.values()],
                'leave_balances': [lb.to_dict() for lb in self.leave_balances.values()],
                'leave_requests': [lr.to_dict() for lr in self.leave_requests.values()]
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=4)
            print("✓ Data saved successfully!")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_employee(self, emp_id: str, name: str, designation: str, department: str) -> bool:
        """Add a new employee."""
        if emp_id in self.employees:
            print(f"✗ Employee {emp_id} already exists!")
            return False
        
        emp = Employee(emp_id, name, designation, department)
        self.employees[emp_id] = emp
        self.leave_balances[emp_id] = LeaveBalance(emp_id)
        print(f"✓ Employee {name} added successfully!")
        self.save_data()
        return True
    
    def view_employee(self, emp_id: str) -> Optional[Employee]:
        """View employee details."""
        if emp_id not in self.employees:
            print(f"✗ Employee {emp_id} not found!")
            return None
        return self.employees[emp_id]
    
    def list_all_employees(self):
        """List all employees."""
        if not self.employees:
            print("No employees found!")
            return
        
        print("\n" + "="*80)
        print(f"{'EMP ID':<10} {'NAME':<20} {'DESIGNATION':<15} {'DEPARTMENT':<20}")
        print("="*80)
        for emp in self.employees.values():
            print(f"{emp.emp_id:<10} {emp.name:<20} {emp.designation:<15} {emp.department:<20}")
        print("="*80)
    
    def apply_leave(self, emp_id: str, leave_type: str, start_date: str, 
                   end_date: str, reason: str) -> bool:
        """Apply for leave."""
        if emp_id not in self.employees:
            print(f"✗ Employee {emp_id} not found!")
            return False
        
        if leave_type not in LeaveType.LEAVE_TYPES:
            print(f"✗ Invalid leave type: {leave_type}")
            return False
        
        # Validate dates
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if start > end:
                print("✗ Start date cannot be after end date!")
                return False
        except ValueError:
            print("✗ Invalid date format! Use YYYY-MM-DD")
            return False
        
        lr = LeaveRequest(emp_id, leave_type, start_date, end_date, reason)
        self.leave_requests[lr.request_id] = lr
        print(f"✓ Leave request {lr.request_id} submitted successfully!")
        print(f"  Days requested: {lr.get_days()}")
        self.save_data()
        return True
    
    def view_leave_balance(self, emp_id: str):
        """View leave balance for an employee."""
        if emp_id not in self.leave_balances:
            print(f"✗ Employee {emp_id} not found!")
            return
        
        emp = self.employees.get(emp_id)
        if emp:
            print(f"\n{'Leave Balance for'} {emp.name} ({emp_id})")
        print("="*50)
        print(f"{'Leave Type':<20} {'Balance':<10}")
        print("="*50)
        
        balance = self.leave_balances[emp_id]
        for leave_code, balance_days in balance.balance.items():
            leave_name = LeaveType.get_leave_type_name(leave_code)
            print(f"{leave_name:<20} {balance_days:<10}")
        print("="*50)
    
    def view_pending_requests(self):
        """View all pending leave requests."""
        pending = [lr for lr in self.leave_requests.values() if lr.status == 'PENDING']
        
        if not pending:
            print("No pending leave requests!")
            return
        
        print("\n" + "="*100)
        print(f"{'REQ ID':<10} {'EMP ID':<10} {'LEAVE TYPE':<12} {'FROM':<12} {'TO':<12} {'DAYS':<5} {'STATUS':<10}")
        print("="*100)
        for lr in pending:
            leave_name = LeaveType.get_leave_type_name(lr.leave_type)
            print(f"{lr.request_id:<10} {lr.emp_id:<10} {leave_name:<12} {lr.start_date:<12} {lr.end_date:<12} {lr.get_days():<5} {lr.status:<10}")
        print("="*100)
    
    def approve_leave_request(self, request_id: str, approved_by: str, comments: str = "") -> bool:
        """Approve a leave request."""
        if request_id not in self.leave_requests:
            print(f"✗ Request {request_id} not found!")
            return False
        
        lr = self.leave_requests[request_id]
        
        if lr.status != 'PENDING':
            print(f"✗ Request is already {lr.status}!")
            return False
        
        # Check balance
        balance = self.leave_balances.get(lr.emp_id)
        if not balance or balance.get_balance(lr.leave_type) < lr.get_days():
            print(f"✗ Insufficient leave balance! Available: {balance.get_balance(lr.leave_type)} days")
            return False
        
        # Deduct from balance
        balance.deduct_leave(lr.leave_type, lr.get_days())
        lr.approve(approved_by, comments)
        
        print(f"✓ Leave request {request_id} approved!")
        print(f"  Remaining balance: {balance.get_balance(lr.leave_type)} days")
        self.save_data()
        return True
    
    def reject_leave_request(self, request_id: str, approved_by: str, comments: str = "") -> bool:
        """Reject a leave request."""
        if request_id not in self.leave_requests:
            print(f"✗ Request {request_id} not found!")
            return False
        
        lr = self.leave_requests[request_id]
        
        if lr.status != 'PENDING':
            print(f"✗ Request is already {lr.status}!")
            return False
        
        lr.reject(approved_by, comments)
        print(f"✓ Leave request {request_id} rejected!")
        self.save_data()
        return True
    
    def view_leave_request(self, request_id: str):
        """View details of a specific leave request."""
        if request_id not in self.leave_requests:
            print(f"✗ Request {request_id} not found!")
            return
        
        lr = self.leave_requests[request_id]
        emp = self.employees.get(lr.emp_id)
        
        print("\n" + "="*50)
        print("Leave Request Details")
        print("="*50)
        print(f"Request ID: {lr.request_id}")
        print(f"Employee: {emp.name if emp else 'Unknown'} ({lr.emp_id})")
        print(f"Leave Type: {LeaveType.get_leave_type_name(lr.leave_type)}")
        print(f"From: {lr.start_date}")
        print(f"To: {lr.end_date}")
        print(f"Days: {lr.get_days()}")
        print(f"Reason: {lr.reason}")
        print(f"Status: {lr.status}")
        print(f"Request Date: {lr.request_date}")
        if lr.approval_date:
            print(f"Approval Date: {lr.approval_date}")
            print(f"Approved By: {lr.approved_by}")
            print(f"Comments: {lr.comments}")
        print("="*50)
    
    def view_employee_requests(self, emp_id: str):
        """View all leave requests of an employee."""
        if emp_id not in self.employees:
            print(f"✗ Employee {emp_id} not found!")
            return
        
        emp = self.employees[emp_id]
        requests = [lr for lr in self.leave_requests.values() if lr.emp_id == emp_id]
        
        if not requests:
            print(f"No leave requests found for {emp.name}!")
            return
        
        print(f"\nLeave Requests for {emp.name} ({emp_id})")
        print("="*90)
        print(f"{'REQ ID':<10} {'TYPE':<12} {'FROM':<12} {'TO':<12} {'DAYS':<5} {'STATUS':<12}")
        print("="*90)
        for lr in requests:
            leave_name = LeaveType.get_leave_type_name(lr.leave_type)
            print(f"{lr.request_id:<10} {leave_name:<12} {lr.start_date:<12} {lr.end_date:<12} {lr.get_days():<5} {lr.status:<12}")
        print("="*90)


def main():
    """Main function with CLI interface."""
    system = LeaveManagementSystem()
    
    while True:
        print("\n" + "="*60)
        print("LEAVE MANAGEMENT SYSTEM")
        print("="*60)
        print("\n1. Add Employee")
        print("2. View Employee Details")
        print("3. List All Employees")
        print("4. Apply for Leave")
        print("5. View Leave Balance")
        print("6. View Pending Requests")
        print("7. Approve Leave Request")
        print("8. Reject Leave Request")
        print("9. View Leave Request Details")
        print("10. View Employee Requests")
        print("11. View All Leave Types")
        print("12. Exit")
        print("="*60)
        
        choice = input("\nSelect an option (1-12): ").strip()
        
        if choice == '1':
            print("\n--- Add New Employee ---")
            emp_id = input("Employee ID: ").strip()
            name = input("Name: ").strip()
            designation = input("Designation: ").strip()
            department = input("Department: ").strip()
            system.add_employee(emp_id, name, designation, department)
        
        elif choice == '2':
            emp_id = input("Enter Employee ID: ").strip()
            emp = system.view_employee(emp_id)
            if emp:
                print(f"\nEmployee Details:")
                print(f"ID: {emp.emp_id}")
                print(f"Name: {emp.name}")
                print(f"Designation: {emp.designation}")
                print(f"Department: {emp.department}")
                print(f"Join Date: {emp.join_date}")
        
        elif choice == '3':
            system.list_all_employees()
        
        elif choice == '4':
            print("\n--- Apply for Leave ---")
            emp_id = input("Employee ID: ").strip()
            print("Leave Types: SL (Sick Leave), CL (Casual Leave), PL (Paid Leave), UL (Unpaid Leave), ML (Maternity Leave)")
            leave_type = input("Leave Type: ").strip().upper()
            start_date = input("Start Date (YYYY-MM-DD): ").strip()
            end_date = input("End Date (YYYY-MM-DD): ").strip()
            reason = input("Reason: ").strip()
            system.apply_leave(emp_id, leave_type, start_date, end_date, reason)
        
        elif choice == '5':
            emp_id = input("Enter Employee ID: ").strip()
            system.view_leave_balance(emp_id)
        
        elif choice == '6':
            system.view_pending_requests()
        
        elif choice == '7':
            print("\n--- Approve Leave Request ---")
            request_id = input("Request ID: ").strip().upper()
            approved_by = input("Approved By (Manager Name): ").strip()
            comments = input("Comments (optional): ").strip()
            system.approve_leave_request(request_id, approved_by, comments)
        
        elif choice == '8':
            print("\n--- Reject Leave Request ---")
            request_id = input("Request ID: ").strip().upper()
            approved_by = input("Rejected By (Manager Name): ").strip()
            comments = input("Reason for rejection: ").strip()
            system.reject_leave_request(request_id, approved_by, comments)
        
        elif choice == '9':
            request_id = input("Enter Request ID: ").strip().upper()
            system.view_leave_request(request_id)
        
        elif choice == '10':
            emp_id = input("Enter Employee ID: ").strip()
            system.view_employee_requests(emp_id)
        
        elif choice == '11':
            print("\n" + "="*50)
            print("Available Leave Types")
            print("="*50)
            for code, details in LeaveType.get_all_types().items():
                print(f"{code}: {details['name']} - {details['days_per_year']} days/year")
            print("="*50)
        
        elif choice == '12':
            print("\nThank you for using Leave Management System. Goodbye!")
            break
        
        else:
            print("✗ Invalid option! Please select 1-12.")


if __name__ == "__main__":
    main()
