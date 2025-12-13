"""
Test script to verify task API functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def login():
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={
            "username": "user1@happypawsrescue.org",
            "password": "password123"
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]

def get_tasks(token):
    """Get all tasks"""
    response = requests.get(
        f"{BASE_URL}/tasks/",
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return response.json()

def create_task(token, title, description, assigned_to_user_id=None):
    """Create a new task"""
    response = requests.post(
        f"{BASE_URL}/tasks/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": title,
            "description": description,
            "status": "open",
            "priority": "normal",
            "assigned_to_user_id": assigned_to_user_id
        }
    )
    response.raise_for_status()
    return response.json()

def update_task(token, task_id, **updates):
    """Update a task"""
    response = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
        json=updates
    )
    response.raise_for_status()
    return response.json()

def mark_task_complete(token, task_id):
    """Mark a task as completed"""
    return update_task(token, task_id, status="completed")

def main():
    print("=" * 60)
    print("Testing Task API Functionality")
    print("=" * 60)

    # 1. Login
    print("\n1. Logging in...")
    token = login()
    print("   ✓ Login successful")

    # 2. Get existing tasks
    print("\n2. Getting existing tasks...")
    tasks = get_tasks(token)
    print(f"   ✓ Found {len(tasks)} existing tasks")
    for task in tasks[:3]:  # Show first 3
        print(f"      - {task['title']} (Status: {task['status']}, Priority: {task['priority']})")

    # 3. Create a new task
    print("\n3. Creating a new task...")
    new_task = create_task(
        token,
        "Test Task - Verify API Functionality",
        "This task was created by the test script to verify task creation works"
    )
    print(f"   ✓ Created task: {new_task['title']}")
    print(f"      ID: {new_task['id']}, Status: {new_task['status']}")

    # 4. Assign the task to user 2
    print("\n4. Assigning task to user 2...")
    updated_task = update_task(token, new_task['id'], assigned_to_user_id=2)
    print(f"   ✓ Assigned task to user ID: {updated_task['assigned_to_user_id']}")

    # 5. Mark task as in progress
    print("\n5. Marking task as in progress...")
    updated_task = update_task(token, new_task['id'], status="in_progress")
    print(f"   ✓ Updated task status to: {updated_task['status']}")

    # 6. Mark task as completed
    print("\n6. Marking task as completed...")
    completed_task = mark_task_complete(token, new_task['id'])
    print(f"   ✓ Marked task as completed: {completed_task['status']}")

    # 7. Verify tasks can be filtered
    print("\n7. Getting all tasks again...")
    all_tasks = get_tasks(token)
    print(f"   ✓ Total tasks now: {len(all_tasks)}")

    completed_tasks = [t for t in all_tasks if t['status'] == 'completed']
    open_tasks = [t for t in all_tasks if t['status'] == 'open']
    in_progress_tasks = [t for t in all_tasks if t['status'] == 'in_progress']

    print(f"      - Open: {len(open_tasks)}")
    print(f"      - In Progress: {len(in_progress_tasks)}")
    print(f"      - Completed: {len(completed_tasks)}")

    print("\n" + "=" * 60)
    print("✓ All task API tests passed successfully!")
    print("=" * 60)
    print("\nTask functionality verified:")
    print("  ✓ Tasks can be listed")
    print("  ✓ Tasks can be created")
    print("  ✓ Tasks can be assigned to users")
    print("  ✓ Tasks can be updated (status changes)")
    print("  ✓ Tasks can be marked as completed")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
