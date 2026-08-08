"""
Advanced Reporting Module for Leave Management System
Provides analytics and reporting features
"""

from leave_management_system import LeaveManagementSystem, LeaveType
from datetime import datetime
from collections import defaultdict
from typing import Dict, List


class LeaveReporting:
    """Provides reporting and analytics for the leave management system."""
    
    def __init__(self, system: LeaveManagementSystem):
        self.system = system
    
    def get_leave_usage_summary(self) -> Dict:
        """Get leave usage summary for all employees."""
        summary = {}
        
        for emp_id, balance in self.system.leave_balances.items():
            emp = self.system.employees.get(emp_id)
            if not emp:
                continue
            
            summary[emp_id] = {
                'name': emp.name,
                'department': emp.department,
                'balance': balance.balance.copy()
            }
        
        return summary
    
    def print_leave_usage_summary(self):
        """Print a formatted leave usage summary."""
        summary = self.get_leave_usage_summary()
        
        if not summary:
            print("No data available!")
            return
        
        print("\n" + "="*120)
        print("LEAVE USAGE SUMMARY REPORT")
        print("="*120)
        print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*120)
        
        # Print header
        print(f"{'EMP ID':<10} {'NAME':<20} {'DEPT':<15}", end="")
        for code, details in LeaveType.LEAVE_TYPES.items():
            leave_name = details['name'].replace(' Leave', '')
            print(f"{code:<8}", end="")
        print()
        print("="*120)
        
        # Print data
        for emp_id, data in summary.items():
            print(f"{emp_id:<10} {data['name']:<20} {data['department']:<15}", end="")
            for code in LeaveType.LEAVE_TYPES.keys():
                balance = data['balance'].get(code, 0)
                print(f"{balance:<8}", end="")
            print()
        
        print("="*120)
    
    def get_department_summary(self) -> Dict:
        """Get leave summary grouped by department."""
        dept_summary = defaultdict(lambda: {
            'employees': 0,
            'total_pending': 0,
            'total_approved': 0,
            'total_rejected': 0
        })
        
        # Group employees by department
        for emp_id, emp in self.system.employees.items():
            dept = emp.department
            dept_summary[dept]['employees'] += 1
        
        # Count requests by department
        for request in self.system.leave_requests.values():
            emp = self.system.employees.get(request.emp_id)
            if not emp:
                continue
            
            dept = emp.department
            if request.status == 'PENDING':
                dept_summary[dept]['total_pending'] += 1
            elif request.status == 'APPROVED':
                dept_summary[dept]['total_approved'] += 1
            elif request.status == 'REJECTED':
                dept_summary[dept]['total_rejected'] += 1
        
        return dict(dept_summary)
    
    def print_department_summary(self):
        """Print department-wise summary."""
        summary = self.get_department_summary()
        
        if not summary:
            print("No data available!")
            return
        
        print("\n" + "="*80)
        print("DEPARTMENT-WISE LEAVE SUMMARY")
        print("="*80)
        print(f"{'DEPARTMENT':<20} {'EMPLOYEES':<12} {'PENDING':<12} {'APPROVED':<12} {'REJECTED':<12}")
        print("="*80)
        
        for dept, data in summary.items():
            print(f"{dept:<20} {data['employees']:<12} {data['total_pending']:<12} {data['total_approved']:<12} {data['total_rejected']:<12}")
        
        print("="*80)
    
    def get_leave_type_statistics(self) -> Dict:
        """Get statistics for each leave type."""
        stats = {}
        
        for leave_code, leave_details in LeaveType.LEAVE_TYPES.items():
            requests = [lr for lr in self.system.leave_requests.values() 
                       if lr.leave_type == leave_code]
            
            approved = [lr for lr in requests if lr.status == 'APPROVED']
            pending = [lr for lr in requests if lr.status == 'PENDING']
            rejected = [lr for lr in requests if lr.status == 'REJECTED']
            
            total_days = sum(lr.get_days() for lr in approved)
            
            stats[leave_code] = {
                'name': leave_details['name'],
                'total_requests': len(requests),
                'approved_requests': len(approved),
                'pending_requests': len(pending),
                'rejected_requests': len(rejected),
                'total_days_used': total_days,
                'max_days_per_year': leave_details['days_per_year']
            }
        
        return stats
    
    def print_leave_type_statistics(self):
        """Print leave type statistics."""
        stats = self.get_leave_type_statistics()
        
        if not stats:
            print("No data available!")
            return
        
        print("\n" + "="*100)
        print("LEAVE TYPE STATISTICS")
        print("="*100)
        print(f"{'LEAVE TYPE':<20} {'REQUESTS':<12} {'APPROVED':<12} {'PENDING':<12} {'REJECTED':<12} {'DAYS USED':<12}")
        print("="*100)
        
        for leave_code, data in stats.items():
            print(f"{data['name']:<20} {data['total_requests']:<12} {data['approved_requests']:<12} {data['pending_requests']:<12} {data['rejected_requests']:<12} {data['total_days_used']:<12}")
        
        print("="*100)
    
    def get_employee_annual_report(self, emp_id: str) -> Dict:
        """Get annual leave report for an employee."""
        emp = self.system.employees.get(emp_id)
        if not emp:
            return None
        
        balance = self.system.leave_balances.get(emp_id)
        requests = [lr for lr in self.system.leave_requests.values() if lr.emp_id == emp_id]
        
        report = {
            'employee': emp,
            'current_balance': balance.balance if balance else {},
            'total_requests': len(requests),
            'approved_requests': len([lr for lr in requests if lr.status == 'APPROVED']),
            'pending_requests': len([lr for lr in requests if lr.status == 'PENDING']),
            'rejected_requests': len([lr for lr in requests if lr.status == 'REJECTED']),
            'requests_by_type': self._get_requests_by_type(requests)
        }
        
        return report
    
    def _get_requests_by_type(self, requests):
        """Helper to group requests by type."""
        by_type = defaultdict(list)
        for lr in requests:
            by_type[lr.leave_type].append(lr)
        return dict(by_type)
    
    def print_employee_annual_report(self, emp_id: str):
        """Print annual report for an employee."""
        report = self.get_employee_annual_report(emp_id)
        
        if not report:
            print(f"Employee {emp_id} not found!")
            return
        
        emp = report['employee']
        
        print("\n" + "="*70)
        print("EMPLOYEE ANNUAL LEAVE REPORT")
        print("="*70)
        print(f"Employee ID: {emp.emp_id}")
        print(f"Name: {emp.name}")
        print(f"Designation: {emp.designation}")
        print(f"Department: {emp.department}")
        print(f"Join Date: {emp.join_date}")
        print("="*70)
        
        print("\nLEAVE BALANCE:")
        print("-" * 70)
        for leave_code, balance in report['current_balance'].items():
            leave_name = LeaveType.get_leave_type_name(leave_code)
            print(f"  {leave_name:<20} : {balance} days")
        
        print("\nREQUEST STATISTICS:")
        print("-" * 70)
        print(f"  Total Requests      : {report['total_requests']}")
        print(f"  Approved            : {report['approved_requests']}")
        print(f"  Pending             : {report['pending_requests']}")
        print(f"  Rejected            : {report['rejected_requests']}")
        
        print("\nREQUESTS BY TYPE:")
        print("-" * 70)
        for leave_code, requests in report['requests_by_type'].items():
            leave_name = LeaveType.get_leave_type_name(leave_code)
            total_days = sum(lr.get_days() for lr in requests if lr.status == 'APPROVED')
            print(f"  {leave_name:<20} : {len(requests)} requests ({total_days} days used)")
        
        print("="*70)
    
    def get_high_leave_users(self, limit: int = 5) -> List[tuple]:
        """Get employees with highest leave usage."""
        emp_usage = defaultdict(int)
        
        for request in self.system.leave_requests.values():
            if request.status == 'APPROVED':
                emp_usage[request.emp_id] += request.get_days()
        
        # Sort by usage
        sorted_usage = sorted(emp_usage.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for emp_id, days in sorted_usage[:limit]:
            emp = self.system.employees.get(emp_id)
            if emp:
                result.append((emp.name, emp_id, days))
        
        return result
    
    def print_high_leave_users(self, limit: int = 5):
        """Print employees with highest leave usage."""
        users = self.get_high_leave_users(limit)
        
        if not users:
            print("No data available!")
            return
        
        print("\n" + "="*70)
        print(f"TOP {limit} EMPLOYEES WITH HIGHEST LEAVE USAGE")
        print("="*70)
        print(f"{'RANK':<6} {'NAME':<25} {'EMP ID':<12} {'TOTAL DAYS':<15}")
        print("="*70)
        
        for rank, (name, emp_id, days) in enumerate(users, 1):
            print(f"{rank:<6} {name:<25} {emp_id:<12} {days:<15}")
        
        print("="*70)
    
    def generate_full_report(self):
        """Generate and print a comprehensive report."""
        print("\n\n" + "#"*120)
        print("# COMPREHENSIVE LEAVE MANAGEMENT REPORT")
        print("#"*120)
        print(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("#"*120 + "\n")
        
        self.print_leave_usage_summary()
        self.print_department_summary()
        self.print_leave_type_statistics()
        self.print_high_leave_users(5)
        
        print("\n" + "#"*120)
        print("# END OF REPORT")
        print("#"*120 + "\n")


def reporting_menu(system: LeaveManagementSystem):
    """Interactive reporting menu."""
    reporting = LeaveReporting(system)
    
    while True:
        print("\n" + "="*60)
        print("LEAVE MANAGEMENT REPORTING")
        print("="*60)
        print("\n1. Leave Usage Summary")
        print("2. Department-wise Summary")
        print("3. Leave Type Statistics")
        print("4. Employee Annual Report")
        print("5. High Leave Users")
        print("6. Full Report")
        print("7. Back to Main Menu")
        print("="*60)
        
        choice = input("\nSelect an option (1-7): ").strip()
        
        if choice == '1':
            reporting.print_leave_usage_summary()
        
        elif choice == '2':
            reporting.print_department_summary()
        
        elif choice == '3':
            reporting.print_leave_type_statistics()
        
        elif choice == '4':
            emp_id = input("Enter Employee ID: ").strip()
            reporting.print_employee_annual_report(emp_id)
        
        elif choice == '5':
            limit = input("Enter number of employees (default 5): ").strip()
            limit = int(limit) if limit.isdigit() else 5
            reporting.print_high_leave_users(limit)
        
        elif choice == '6':
            reporting.generate_full_report()
        
        elif choice == '7':
            break
        
        else:
            print("✗ Invalid option! Please select 1-7.")


if __name__ == "__main__":
    system = LeaveManagementSystem()
    reporting_menu(system)
