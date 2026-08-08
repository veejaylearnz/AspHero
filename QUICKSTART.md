# Leave Management System - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Run the Main Program
```bash
python leave_management_system.py
```

### Step 2: Add Your First Employee
1. Select option **1** from the menu
2. Enter Employee ID: `EMP001`
3. Enter Name: `John Doe`
4. Enter Designation: `Developer`
5. Enter Department: `IT`

### Step 3: Check Leave Balance
1. Select option **5** from the menu
2. Enter Employee ID: `EMP001`
3. View shows: Sick Leave (10), Casual Leave (12), Paid Leave (20), etc.

### Step 4: Apply for Leave
1. Select option **4** from the menu
2. Employee ID: `EMP001`
3. Leave Type: `SL` (Sick Leave)
4. Start Date: `2024-06-15` (format: YYYY-MM-DD)
5. End Date: `2024-06-17`
6. Reason: `Medical checkup`

### Step 5: View & Approve Requests
1. Select option **6** to see all pending requests
2. Note the Request ID (e.g., `LR00001`)
3. Select option **7** to approve
4. Enter Request ID: `LR00001`
5. Approved By: `Manager Name`
6. Comments: `Approved`

### Step 6: Check Updated Balance
1. Select option **5** again
2. Enter Employee ID: `EMP001`
3. Note: Sick Leave is now **7** days (10 - 3)

---

## 📊 Using the Demo Script

Run the complete demo with sample data:

```bash
python demo_leave_system.py
```

This will:
- Create 4 sample employees
- Apply 3 leave requests
- Approve and reject requests
- Show all features in action

---

## 📈 Generating Reports

### Method 1: Using Interactive Menu
```bash
python leave_reporting.py
```

Reports Available:
1. **Leave Usage Summary** - All employees' current balances
2. **Department-wise Summary** - Grouped by department
3. **Leave Type Statistics** - Usage for each leave type
4. **Employee Annual Report** - Detailed report for one employee
5. **High Leave Users** - Top users by days used
6. **Full Report** - Complete comprehensive report

### Method 2: Using Python Code
```python
from leave_management_system import LeaveManagementSystem
from leave_reporting import LeaveReporting

system = LeaveManagementSystem()
reporting = LeaveReporting(system)

# Generate different reports
reporting.print_leave_usage_summary()
reporting.print_department_summary()
reporting.print_leave_type_statistics()
reporting.print_employee_annual_report("EMP001")
reporting.print_high_leave_users(5)
```

---

## 📁 File Overview

| File | Purpose |
|------|---------|
| `leave_management_system.py` | Main system with all classes and logic |
| `demo_leave_system.py` | Demo script with sample data |
| `leave_reporting.py` | Reporting and analytics module |
| `leave_system_data.json` | Auto-generated data storage (created after first run) |
| `README_LEAVE_SYSTEM.md` | Comprehensive documentation |

---

## 🎯 Common Tasks

### Add Multiple Employees
```python
from leave_management_system import LeaveManagementSystem

system = LeaveManagementSystem()

employees = [
    ("EMP001", "John Doe", "Senior Dev", "IT"),
    ("EMP002", "Jane Smith", "Manager", "HR"),
    ("EMP003", "Alice Johnson", "QA", "QA"),
]

for emp_id, name, des, dept in employees:
    system.add_employee(emp_id, name, des, dept)
```

### Bulk Process Leave Requests
```python
# Apply leaves
system.apply_leave("EMP001", "SL", "2024-06-15", "2024-06-17", "Sick")
system.apply_leave("EMP002", "CL", "2024-06-20", "2024-06-22", "Personal")

# Approve all pending
for request_id, request in system.leave_requests.items():
    if request.status == "PENDING":
        system.approve_leave_request(request_id, "Manager", "Approved")
```

### Export Data
```python
import json

system = LeaveManagementSystem()
with open("backup.json", "r") as f:
    data = json.load(f)
    print(data)
```

---

## ✅ Leave Types Reference

| Code | Leave Type | Days/Year |
|------|-----------|-----------|
| SL | Sick Leave | 10 |
| CL | Casual Leave | 12 |
| PL | Paid Leave | 20 |
| UL | Unpaid Leave | 5 |
| ML | Maternity Leave | 90 |

---

## 🔍 Troubleshooting

**Q: How do I start fresh with no data?**
```bash
# Simply delete the JSON file
rm leave_system_data.json
# Or rename it
ren leave_system_data.json leave_system_data_backup.json
```

**Q: Date format error?**
```
Always use: YYYY-MM-DD
Examples: 2024-06-15, 2024-12-25
```

**Q: Request approval shows "Insufficient balance"?**
```
Check current balance before approving:
Option 5 → Enter Employee ID → View available days
```

**Q: How do I find a Request ID?**
```
Option 6 → View Pending Requests → Note the REQ ID
Or Option 10 → View Employee Requests → See all their request IDs
```

---

## 🎓 Learning Path

1. **Beginner**: Run demo script → Explore main menu
2. **Intermediate**: Create employees → Apply & approve leaves
3. **Advanced**: Use reporting module → Generate reports
4. **Expert**: Modify code → Integrate with other systems

---

## 💡 Pro Tips

1. **Batch Operations**: Use Python script for bulk employee/request management
2. **Data Backup**: Copy the JSON file before major operations
3. **Reports**: Generate weekly/monthly reports using the reporting module
4. **Automation**: Schedule scripts to auto-approve leaves based on criteria
5. **Integration**: Use programmatic API to integrate with other systems

---

## 📞 Example Scenarios

### Scenario 1: Employee Calls Sick
```
Option 4 (Apply Leave) → SL → Today to today → "High fever"
Option 6 (Pending Requests) → Note request ID
Option 7 (Approve) → Approve with HR manager name
```

### Scenario 2: Plan Summer Vacation
```
Option 4 (Apply Leave) → PL → 2024-07-01 to 2024-07-10 → "Summer vacation"
# Deducts 10 days from 20 available paid leave
# Remaining: 10 days
```

### Scenario 3: Monthly Report
```
Option from reporting menu: 6 (Full Report)
# Shows all employees, departments, leave types, and top users
# Can be saved/exported for management review
```

---

## 🔐 Important Notes

- ✅ All data is automatically saved after each operation
- ✅ Multiple approvals for same request are prevented
- ✅ Insufficient balance is checked before approval
- ✅ System validates all dates and formats
- ✅ No external dependencies required (pure Python)

---

**Ready to manage leaves? Start with the demo!**
```bash
python demo_leave_system.py
```

**Questions? Check the full documentation in README_LEAVE_SYSTEM.md**

