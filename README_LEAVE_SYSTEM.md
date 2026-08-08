# Leave Management System

A comprehensive Python-based Leave Management System to manage employee leaves, track leave balances, process leave requests, and generate reports.

## Features

### 1. **Employee Management**
- Add new employees with details (ID, name, designation, department)
- View individual employee information
- List all employees in the organization

### 2. **Leave Types**
- **Sick Leave (SL)**: 10 days per year
- **Casual Leave (CL)**: 12 days per year
- **Paid Leave (PL)**: 20 days per year
- **Unpaid Leave (UL)**: 5 days per year
- **Maternity Leave (ML)**: 90 days per year

### 3. **Leave Request Management**
- Apply for leave with reason and date range
- View pending leave requests
- Approve/reject leave requests by managers
- Add comments during approval/rejection
- View detailed leave request information

### 4. **Leave Balance Tracking**
- Automatic leave balance initialization for each employee
- Real-time balance updates after approval
- View leave balance by leave type
- Track used and remaining leaves

### 5. **Data Persistence**
- All data saved to JSON files
- Automatic save after each operation
- Easy data import/export

---

## System Architecture

### Core Classes

#### 1. **Employee**
Represents an employee in the system.
- Attributes: emp_id, name, designation, department, join_date
- Methods: to_dict(), from_dict()

#### 2. **LeaveType**
Manages different types of leaves available.
- Contains leave codes and their configurations
- Methods: get_all_types(), get_leave_type_name()

#### 3. **LeaveBalance**
Tracks leave balance for each employee.
- Attributes: emp_id, balance (dictionary)
- Methods: get_balance(), deduct_leave(), add_leave()

#### 4. **LeaveRequest**
Represents a leave request from an employee.
- Attributes: request_id, emp_id, leave_type, dates, status, reason
- Status: PENDING, APPROVED, REJECTED
- Methods: approve(), reject(), get_days()

#### 5. **LeaveManagementSystem**
Main system class that manages all operations.
- Methods for CRUD operations on employees and leave requests
- Data persistence using JSON
- Request approval/rejection workflow

---

## Installation

1. **Download the files**:
   - `leave_management_system.py` - Main system
   - `demo_leave_system.py` - Demo script (optional)

2. **No external dependencies required** - Uses only Python standard library

3. **Run the system**:
   ```bash
   python leave_management_system.py
   ```

---

## Usage

### Interactive Menu
Run the main script to access the interactive CLI menu:

```bash
python leave_management_system.py
```

Menu Options:
1. **Add Employee** - Register a new employee
2. **View Employee Details** - Get employee information
3. **List All Employees** - Display all registered employees
4. **Apply for Leave** - Submit a leave request
5. **View Leave Balance** - Check available leaves
6. **View Pending Requests** - See all pending approvals
7. **Approve Leave Request** - Approve a pending request
8. **Reject Leave Request** - Reject a pending request
9. **View Leave Request Details** - Get detailed info on a request
10. **View Employee Requests** - See all requests of an employee
11. **View All Leave Types** - Display available leave types
12. **Exit** - Exit the system

### Programmatic Usage

```python
from leave_management_system import LeaveManagementSystem

# Initialize system
system = LeaveManagementSystem()

# Add an employee
system.add_employee("EMP001", "John Doe", "Developer", "IT")

# Apply for leave
system.apply_leave("EMP001", "SL", "2024-06-15", "2024-06-17", "Medical appointment")

# View leave balance
system.view_leave_balance("EMP001")

# Approve leave request
system.approve_leave_request("LR00001", "Manager Name", "Approved")

# Reject leave request
system.reject_leave_request("LR00002", "Manager Name", "Insufficient staff coverage")
```

---

## Data Storage Format

### JSON Structure

```json
{
  "employees": [
    {
      "emp_id": "EMP001",
      "name": "John Doe",
      "designation": "Developer",
      "department": "IT",
      "join_date": "2024-01-15"
    }
  ],
  "leave_balances": [
    {
      "emp_id": "EMP001",
      "balance": {
        "SL": 10,
        "CL": 12,
        "PL": 20,
        "UL": 5,
        "ML": 90
      }
    }
  ],
  "leave_requests": [
    {
      "request_id": "LR00001",
      "emp_id": "EMP001",
      "leave_type": "SL",
      "start_date": "2024-06-15",
      "end_date": "2024-06-17",
      "reason": "Medical appointment",
      "status": "PENDING",
      "request_date": "2024-01-10 14:30:45",
      "approval_date": null,
      "approved_by": null,
      "comments": "",
      "days": 3
    }
  ]
}
```

---

## Example Workflow

### Step-by-Step Guide

**1. Add Employees**
```
Select: 1
Employee ID: EMP001
Name: John Doe
Designation: Senior Developer
Department: IT
```

**2. View Leave Balance**
```
Select: 5
Enter Employee ID: EMP001
```

**3. Apply for Leave**
```
Select: 4
Employee ID: EMP001
Leave Type: SL
Start Date (YYYY-MM-DD): 2024-06-15
End Date (YYYY-MM-DD): 2024-06-17
Reason: Medical checkup
```

**4. View Pending Requests**
```
Select: 6
(Shows all pending requests)
```

**5. Approve Leave Request**
```
Select: 7
Request ID: LR00001
Approved By: Jane Smith
Comments: Approved
```

**6. View Updated Balance**
```
Select: 5
Enter Employee ID: EMP001
(Balance shows 7 days remaining for SL)
```

---

## Demo Script

Run the demo to see all features in action:

```bash
python demo_leave_system.py
```

This will:
- Create sample employees
- Apply multiple leave requests
- Show pending requests
- Approve/reject requests
- Display updated balances

---

## Key Features Explained

### Leave Request Workflow
1. Employee applies for leave
2. System validates:
   - Employee exists
   - Leave type is valid
   - Date format is correct
3. Request is created with PENDING status
4. Manager reviews request
5. Manager can APPROVE or REJECT
6. If approved, leaves are deducted from balance
7. Data is persisted to JSON

### Leave Balance Management
- Each employee starts with full balance for all leave types
- Balance is deducted only when request is APPROVED
- Rejected requests don't affect balance
- System prevents approval if insufficient balance

### Data Persistence
- All operations automatically save to JSON
- Data survives application restart
- Easy to backup and migrate data

---

## Error Handling

The system handles various error scenarios:

- ✗ Employee not found
- ✗ Invalid leave type
- ✗ Invalid date format
- ✗ Start date after end date
- ✗ Insufficient leave balance
- ✗ Request already processed
- ✗ Duplicate employee ID

---

## Future Enhancements

1. **Database Integration** - Replace JSON with SQL database
2. **Email Notifications** - Notify employees of approval/rejection
3. **Holiday Calendar** - Exclude holidays from leave calculation
4. **Reports** - Generate leave usage reports
5. **User Authentication** - Add login system
6. **REST API** - Create web API for integration
7. **Audit Trail** - Track all system changes
8. **Leave Encashment** - Handle unused leave payments

---

## Troubleshooting

**Q: Data not saving?**
- Ensure the script has write permissions in the directory
- Check disk space availability

**Q: Invalid date format error?**
- Use YYYY-MM-DD format (e.g., 2024-06-15)

**Q: Leave approval failed - Insufficient balance?**
- View leave balance before applying
- Only approved requests deduct from balance

**Q: Can't find employee?**
- Add employee first (Option 1)
- Use correct Employee ID

---

## File Structure

```
├── leave_management_system.py    # Main system (core classes and logic)
├── demo_leave_system.py           # Demo script with sample data
├── leave_system_data.json         # Data storage (auto-generated)
└── README.md                      # Documentation
```

---

## License

This project is free to use and modify.

---

## Support

For issues or questions, review the code comments in `leave_management_system.py` or run the demo to understand the workflow.

---

**Happy Leave Management! 🎉**
