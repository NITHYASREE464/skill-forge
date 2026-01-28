from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import re
import tempfile

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'default-secret-key')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 72

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Educational domain patterns
ALLOWED_EMAIL_DOMAINS = [
    r'\.edu$', r'\.edu\.\w+$', r'\.ac\.\w+$', r'@iit\w*\.', r'@nit\w*\.',
    r'@bits-pilani\.', r'@vit\.', r'@manipal\.', r'@amity\.', r'@srm\.',
    r'@iisc\.', r'@iiit\w*\.', r'\.college$', r'\.university$'
]

def is_valid_edu_email(email: str) -> bool:
    email_lower = email.lower()
    demo_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
    domain = email_lower.split('@')[-1]
    if domain in demo_domains:
        return True
    for pattern in ALLOWED_EMAIL_DOMAINS:
        if re.search(pattern, email_lower):
            return True
    return False

# ============ MODELS ============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RoleUpdate(BaseModel):
    role: str

class TaskSubmission(BaseModel):
    task_id: str
    code: str
    explanation: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None

class CodeRunRequest(BaseModel):
    code: str
    task_id: Optional[str] = None

class ResumeCreate(BaseModel):
    company: str
    content: Dict[str, Any]
    template: str = "modern"

class ResumeUpdate(BaseModel):
    content: Dict[str, Any]
    template: Optional[str] = None

class LinkedInDraftRequest(BaseModel):
    topic: str
    learning_type: str

class GitHubDraftRequest(BaseModel):
    project_name: str
    changes: str

class StreakUpdate(BaseModel):
    activity_type: str  # 'dsa', 'github', 'linkedin'

# ============ AUTH HELPERS ============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============ DSA TRACK DATA ============

DSA_TRACKS = {
    "arrays": {
        "name": "Arrays",
        "description": "Master array operations - the foundation of coding interviews",
        "order": 1,
        "tasks": [
            {
                "id": "arr-001",
                "title": "Two Sum",
                "difficulty": "Easy",
                "points": 10,
                "type": "coding",
                "description": """Given an array of integers and a target sum, find two numbers that add up to the target.

**Your Task:** Return the indices of two numbers that sum to target.

**Example:**
Input: nums = [2, 7, 11, 15], target = 9
Output: [0, 1] (because nums[0] + nums[1] = 2 + 7 = 9)

**Constraints:**
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- Only one valid answer exists

**Think about:**
- What's the brute force approach? What's its time complexity?
- Can you do better with a hash map?""",
                "starter_code": """def two_sum(nums, target):
    # Your code here
    pass

# Test your solution
print(two_sum([2, 7, 11, 15], 9))  # Expected: [0, 1]
print(two_sum([3, 2, 4], 6))  # Expected: [1, 2]""",
                "hints": ["Start with the simplest approach: check every pair", "A hash map can help you find complements in O(1)", "Think about what you need to store as you iterate"],
                "solution_explanation": """**Approach 1: Brute Force O(n²)**
Check every pair of numbers. Simple but slow.

**Approach 2: Hash Map O(n)**
As you traverse, store each number and its index. For each number, check if (target - num) exists in your map.

```python
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

**Time: O(n), Space: O(n)**"""
            },
            {
                "id": "arr-002",
                "title": "Maximum Subarray",
                "difficulty": "Medium",
                "points": 20,
                "type": "coding",
                "description": """Find the contiguous subarray with the largest sum.

**Your Task:** Return the maximum sum possible from any contiguous subarray.

**Example:**
Input: nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
Output: 6 (subarray [4, -1, 2, 1] has the largest sum)

**Constraints:**
- 1 <= nums.length <= 10^5
- -10^4 <= nums[i] <= 10^4

**Think about:**
- At each position, should you extend the previous subarray or start fresh?
- This is a classic dynamic programming problem (Kadane's Algorithm)""",
                "starter_code": """def max_subarray(nums):
    # Your code here
    pass

# Test
print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))  # Expected: 6""",
                "hints": ["At each element, you have two choices: start fresh or continue", "Track the best ending at current position"],
                "solution_explanation": """**Kadane's Algorithm O(n)**
```python
def max_subarray(nums):
    max_ending_here = max_so_far = nums[0]
    for num in nums[1:]:
        max_ending_here = max(num, max_ending_here + num)
        max_so_far = max(max_so_far, max_ending_here)
    return max_so_far
```
**Time: O(n), Space: O(1)**"""
            },
            {
                "id": "arr-003",
                "title": "Contains Duplicate",
                "difficulty": "Easy",
                "points": 10,
                "type": "coding",
                "description": """Check if any value appears at least twice in the array.

**Your Task:** Return True if duplicates exist, False otherwise.

**Example:**
Input: nums = [1, 2, 3, 1]
Output: True""",
                "starter_code": """def contains_duplicate(nums):
    # Your code here
    pass

print(contains_duplicate([1, 2, 3, 1]))  # Expected: True""",
                "hints": ["Sets have O(1) lookup", "Compare set size with array size"],
                "solution_explanation": """```python
def contains_duplicate(nums):
    return len(nums) != len(set(nums))
```
**Time: O(n), Space: O(n)**"""
            },
            {
                "id": "arr-004",
                "title": "Product of Array Except Self",
                "difficulty": "Medium",
                "points": 25,
                "type": "coding",
                "description": """Given an array nums, return an array where each element is the product of all other elements WITHOUT using division.

**Example:**
Input: nums = [1, 2, 3, 4]
Output: [24, 12, 8, 6]""",
                "starter_code": """def product_except_self(nums):
    # No division allowed!
    pass

print(product_except_self([1, 2, 3, 4]))  # Expected: [24, 12, 8, 6]""",
                "hints": ["Think prefix and suffix products", "Each answer = prefix[i-1] × suffix[i+1]"],
                "solution_explanation": """**Two Pass Approach O(n)**
```python
def product_except_self(nums):
    n = len(nums)
    result = [1] * n
    left = 1
    for i in range(n):
        result[i] = left
        left *= nums[i]
    right = 1
    for i in range(n - 1, -1, -1):
        result[i] *= right
        right *= nums[i]
    return result
```"""
            },
            {
                "id": "arr-005",
                "title": "Rotate Array",
                "difficulty": "Medium",
                "points": 20,
                "type": "coding",
                "description": """Rotate an array to the right by k steps in-place.

**Example:**
Input: nums = [1,2,3,4,5,6,7], k = 3
Output: [5,6,7,1,2,3,4]""",
                "starter_code": """def rotate(nums, k):
    # Modify in-place
    pass

arr = [1,2,3,4,5,6,7]
rotate(arr, 3)
print(arr)  # Expected: [5,6,7,1,2,3,4]""",
                "hints": ["k = k % len(nums) handles large k", "Try reversing: whole array, then first k, then rest"],
                "solution_explanation": """**Reverse Method O(n) time, O(1) space**
```python
def rotate(nums, k):
    n = len(nums)
    k = k % n
    def reverse(start, end):
        while start < end:
            nums[start], nums[end] = nums[end], nums[start]
            start += 1
            end -= 1
    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)
```"""
            }
        ]
    },
    "strings": {
        "name": "Strings",
        "description": "String manipulation and pattern matching problems",
        "order": 2,
        "tasks": [
            {
                "id": "str-001",
                "title": "Valid Palindrome",
                "difficulty": "Easy",
                "points": 10,
                "type": "coding",
                "description": """Check if a string is a palindrome, considering only alphanumeric characters.

**Example:**
Input: "A man, a plan, a canal: Panama"
Output: True""",
                "starter_code": """def is_palindrome(s):
    # Your code here
    pass

print(is_palindrome("A man, a plan, a canal: Panama"))  # True""",
                "hints": ["Use two pointers", "Filter out non-alphanumeric characters"],
                "solution_explanation": """```python
def is_palindrome(s):
    clean = ''.join(c.lower() for c in s if c.isalnum())
    return clean == clean[::-1]
```"""
            },
            {
                "id": "str-002",
                "title": "Valid Anagram",
                "difficulty": "Easy",
                "points": 10,
                "type": "coding",
                "description": """Check if two strings are anagrams of each other.

**Example:**
Input: s = "anagram", t = "nagaram"
Output: True""",
                "starter_code": """def is_anagram(s, t):
    pass

print(is_anagram("anagram", "nagaram"))  # True""",
                "hints": ["Count character frequencies", "Or sort both strings"],
                "solution_explanation": """```python
from collections import Counter
def is_anagram(s, t):
    return Counter(s) == Counter(t)
```"""
            },
            {
                "id": "str-003",
                "title": "Longest Substring Without Repeating",
                "difficulty": "Medium",
                "points": 25,
                "type": "coding",
                "description": """Find the length of the longest substring without repeating characters.

**Example:**
Input: "abcabcbb"
Output: 3 (substring "abc")""",
                "starter_code": """def length_of_longest_substring(s):
    pass

print(length_of_longest_substring("abcabcbb"))  # 3""",
                "hints": ["Use sliding window technique", "Track character positions with a hash map"],
                "solution_explanation": """```python
def length_of_longest_substring(s):
    char_index = {}
    max_len = start = 0
    for i, c in enumerate(s):
        if c in char_index and char_index[c] >= start:
            start = char_index[c] + 1
        char_index[c] = i
        max_len = max(max_len, i - start + 1)
    return max_len
```"""
            },
            {
                "id": "str-004",
                "title": "Group Anagrams",
                "difficulty": "Medium",
                "points": 20,
                "type": "coding",
                "description": """Group anagrams together from a list of strings.

**Example:**
Input: ["eat","tea","tan","ate","nat","bat"]
Output: [["bat"],["nat","tan"],["ate","eat","tea"]]""",
                "starter_code": """def group_anagrams(strs):
    pass

print(group_anagrams(["eat","tea","tan","ate","nat","bat"]))""",
                "hints": ["Use sorted string as key", "defaultdict makes grouping easier"],
                "solution_explanation": """```python
from collections import defaultdict
def group_anagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        groups[tuple(sorted(s))].append(s)
    return list(groups.values())
```"""
            }
        ]
    },
    "linked_lists": {
        "name": "Linked Lists",
        "description": "Pointer manipulation and linked data structures",
        "order": 3,
        "tasks": [
            {
                "id": "ll-001",
                "title": "Reverse Linked List",
                "difficulty": "Easy",
                "points": 15,
                "type": "coding",
                "description": """Reverse a singly linked list.

**Example:**
Input: 1 -> 2 -> 3 -> 4 -> 5
Output: 5 -> 4 -> 3 -> 2 -> 1""",
                "starter_code": """class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head):
    # Your code here
    pass""",
                "hints": ["Use three pointers: prev, curr, next", "Iterative is simpler than recursive for interviews"],
                "solution_explanation": """```python
def reverse_list(head):
    prev = None
    curr = head
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    return prev
```"""
            },
            {
                "id": "ll-002",
                "title": "Detect Cycle in Linked List",
                "difficulty": "Easy",
                "points": 15,
                "type": "coding",
                "description": """Detect if a linked list has a cycle.

**Think about:** Floyd's Cycle Detection (Tortoise and Hare)""",
                "starter_code": """def has_cycle(head):
    # Your code here
    pass""",
                "hints": ["Use slow and fast pointers", "If they meet, there's a cycle"],
                "solution_explanation": """```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```"""
            },
            {
                "id": "ll-003",
                "title": "Merge Two Sorted Lists",
                "difficulty": "Easy",
                "points": 15,
                "type": "coding",
                "description": """Merge two sorted linked lists into one sorted list.""",
                "starter_code": """def merge_two_lists(l1, l2):
    pass""",
                "hints": ["Use a dummy head node", "Compare values and advance pointers"],
                "solution_explanation": """```python
def merge_two_lists(l1, l2):
    dummy = ListNode()
    curr = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            curr.next = l1
            l1 = l1.next
        else:
            curr.next = l2
            l2 = l2.next
        curr = curr.next
    curr.next = l1 or l2
    return dummy.next
```"""
            }
        ]
    },
    "stacks_queues": {
        "name": "Stacks & Queues",
        "description": "LIFO and FIFO data structures",
        "order": 4,
        "tasks": [
            {
                "id": "sq-001",
                "title": "Valid Parentheses",
                "difficulty": "Easy",
                "points": 10,
                "type": "coding",
                "description": """Check if brackets are valid: (), {}, []

**Example:**
Input: "()[]{}"
Output: True""",
                "starter_code": """def is_valid(s):
    pass

print(is_valid("()[]{}"))  # True""",
                "hints": ["Use a stack", "Push opening brackets, pop for closing"],
                "solution_explanation": """```python
def is_valid(s):
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    for c in s:
        if c in pairs:
            if not stack or stack.pop() != pairs[c]:
                return False
        else:
            stack.append(c)
    return len(stack) == 0
```"""
            },
            {
                "id": "sq-002",
                "title": "Min Stack",
                "difficulty": "Medium",
                "points": 20,
                "type": "coding",
                "description": """Design a stack that supports getMin() in O(1) time.""",
                "starter_code": """class MinStack:
    def __init__(self):
        pass
    
    def push(self, val):
        pass
    
    def pop(self):
        pass
    
    def top(self):
        pass
    
    def getMin(self):
        pass""",
                "hints": ["Store (value, current_min) pairs", "Or maintain two stacks"],
                "solution_explanation": """```python
class MinStack:
    def __init__(self):
        self.stack = []
    
    def push(self, val):
        min_val = min(val, self.stack[-1][1]) if self.stack else val
        self.stack.append((val, min_val))
    
    def pop(self):
        self.stack.pop()
    
    def top(self):
        return self.stack[-1][0]
    
    def getMin(self):
        return self.stack[-1][1]
```"""
            }
        ]
    },
    "trees": {
        "name": "Trees",
        "description": "Binary trees and tree traversals",
        "order": 5,
        "tasks": [
            {
                "id": "tree-001",
                "title": "Maximum Depth of Binary Tree",
                "difficulty": "Easy",
                "points": 10,
                "type": "coding",
                "description": """Find the maximum depth (height) of a binary tree.""",
                "starter_code": """class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def max_depth(root):
    pass""",
                "hints": ["Use recursion", "Depth = 1 + max(left_depth, right_depth)"],
                "solution_explanation": """```python
def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```"""
            },
            {
                "id": "tree-002",
                "title": "Invert Binary Tree",
                "difficulty": "Easy",
                "points": 10,
                "type": "coding",
                "description": """Invert (mirror) a binary tree.""",
                "starter_code": """def invert_tree(root):
    pass""",
                "hints": ["Swap left and right children recursively"],
                "solution_explanation": """```python
def invert_tree(root):
    if not root:
        return None
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root
```"""
            },
            {
                "id": "tree-003",
                "title": "Validate Binary Search Tree",
                "difficulty": "Medium",
                "points": 20,
                "type": "coding",
                "description": """Check if a binary tree is a valid BST.""",
                "starter_code": """def is_valid_bst(root):
    pass""",
                "hints": ["Track valid range for each node", "Left subtree < root < right subtree"],
                "solution_explanation": """```python
def is_valid_bst(root, min_val=float('-inf'), max_val=float('inf')):
    if not root:
        return True
    if root.val <= min_val or root.val >= max_val:
        return False
    return is_valid_bst(root.left, min_val, root.val) and is_valid_bst(root.right, root.val, max_val)
```"""
            }
        ]
    },
    "dynamic_programming": {
        "name": "Dynamic Programming",
        "description": "Optimization problems with overlapping subproblems",
        "order": 6,
        "tasks": [
            {
                "id": "dp-001",
                "title": "Climbing Stairs",
                "difficulty": "Easy",
                "points": 10,
                "type": "coding",
                "description": """You can climb 1 or 2 steps at a time. How many ways to reach the top?

**Example:** n = 3 → Output: 3 (1+1+1, 1+2, 2+1)""",
                "starter_code": """def climb_stairs(n):
    pass

print(climb_stairs(3))  # 3""",
                "hints": ["It's the Fibonacci sequence!", "ways[n] = ways[n-1] + ways[n-2]"],
                "solution_explanation": """```python
def climb_stairs(n):
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b
```"""
            },
            {
                "id": "dp-002",
                "title": "House Robber",
                "difficulty": "Medium",
                "points": 20,
                "type": "coding",
                "description": """Rob houses without robbing adjacent ones. Maximize money.

**Example:** [1,2,3,1] → Output: 4 (rob house 1 and 3)""",
                "starter_code": """def rob(nums):
    pass

print(rob([1,2,3,1]))  # 4""",
                "hints": ["At each house: rob it + prev_prev OR skip it + prev", "Track two states"],
                "solution_explanation": """```python
def rob(nums):
    if not nums:
        return 0
    prev, curr = 0, 0
    for n in nums:
        prev, curr = curr, max(curr, prev + n)
    return curr
```"""
            },
            {
                "id": "dp-003",
                "title": "Coin Change",
                "difficulty": "Medium",
                "points": 25,
                "type": "coding",
                "description": """Find minimum coins needed to make the amount.

**Example:** coins = [1,2,5], amount = 11 → Output: 3 (5+5+1)""",
                "starter_code": """def coin_change(coins, amount):
    pass

print(coin_change([1,2,5], 11))  # 3""",
                "hints": ["Build up from amount 0", "dp[i] = min coins to make amount i"],
                "solution_explanation": """```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for c in coins:
            if c <= i:
                dp[i] = min(dp[i], dp[i - c] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```"""
            }
        ]
    }
}

# ============ DATA ANALYTICS TRACK ============

DATA_ANALYTICS_TRACKS = {
    "sql": {
        "name": "SQL Fundamentals",
        "description": "Master SQL for data analysis and interviews",
        "order": 1,
        "tasks": [
            {
                "id": "sql-001",
                "title": "SELECT Basics",
                "difficulty": "Easy",
                "points": 10,
                "type": "concept",
                "description": """**SELECT Statement Basics**

The SELECT statement retrieves data from tables.

```sql
-- Select all columns
SELECT * FROM employees;

-- Select specific columns
SELECT name, salary FROM employees;

-- Filter with WHERE
SELECT name, salary FROM employees WHERE salary > 50000;

-- Order results
SELECT name, salary FROM employees ORDER BY salary DESC;
```

**Practice:** Write a query to find all employees in the 'Engineering' department.""",
                "starter_code": """-- Write your SQL query
SELECT * FROM employees WHERE department = 'Engineering';""",
                "hints": ["Use WHERE to filter", "Column names are case-insensitive in most databases"],
                "solution_explanation": "SELECT filters rows, WHERE adds conditions, ORDER BY sorts results."
            },
            {
                "id": "sql-002",
                "title": "JOINs Explained",
                "difficulty": "Medium",
                "points": 20,
                "type": "concept",
                "description": """**SQL JOINs**

JOINs combine rows from multiple tables.

```sql
-- INNER JOIN: Only matching rows
SELECT e.name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.id;

-- LEFT JOIN: All from left + matches from right
SELECT e.name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.id;
```

**Interview Tip:** Always know when to use INNER vs LEFT JOIN!""",
                "starter_code": """-- Practice JOINs here""",
                "hints": ["INNER JOIN = only matches", "LEFT JOIN = all left rows + matching right"],
                "solution_explanation": "JOINs are crucial for combining normalized data."
            },
            {
                "id": "sql-003",
                "title": "GROUP BY & Aggregations",
                "difficulty": "Medium",
                "points": 20,
                "type": "concept",
                "description": """**Aggregation Functions**

```sql
-- Count, Sum, Avg
SELECT department, COUNT(*) as emp_count, AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 60000;
```

**Common Functions:** COUNT, SUM, AVG, MIN, MAX""",
                "starter_code": """-- Practice aggregations""",
                "hints": ["GROUP BY groups rows", "HAVING filters groups (not rows)"],
                "solution_explanation": "GROUP BY + aggregates = powerful data summarization"
            }
        ]
    },
    "excel": {
        "name": "Excel for Analysis",
        "description": "Essential Excel skills for data analysis",
        "order": 2,
        "tasks": [
            {
                "id": "excel-001",
                "title": "VLOOKUP & XLOOKUP",
                "difficulty": "Easy",
                "points": 10,
                "type": "concept",
                "description": """**Lookup Functions**

VLOOKUP searches vertically, XLOOKUP is the modern replacement.

```
=VLOOKUP(search_key, range, index, [is_sorted])
=XLOOKUP(search_key, lookup_range, return_range)
```

**Interview Question:** Why is XLOOKUP better?
- Can search left
- Cleaner syntax
- Better error handling""",
                "starter_code": "Practice VLOOKUP formulas",
                "hints": ["XLOOKUP is newer and more flexible", "Always use FALSE for exact match in VLOOKUP"],
                "solution_explanation": "Lookup functions are essential for joining data in Excel"
            },
            {
                "id": "excel-002",
                "title": "Pivot Tables",
                "difficulty": "Medium",
                "points": 20,
                "type": "concept",
                "description": """**Pivot Tables**

Pivot tables summarize large datasets quickly.

Steps:
1. Select data range
2. Insert → Pivot Table
3. Drag fields to Rows, Columns, Values

**Common Uses:**
- Sales by region
- Count by category
- Average by time period""",
                "starter_code": "Create a pivot table showing sales by product category",
                "hints": ["Rows = categories", "Values = what you're measuring"],
                "solution_explanation": "Pivot tables are interview favorites for data analyst roles"
            }
        ]
    },
    "eda": {
        "name": "Exploratory Data Analysis",
        "description": "Techniques for understanding data",
        "order": 3,
        "tasks": [
            {
                "id": "eda-001",
                "title": "Data Profiling Steps",
                "difficulty": "Easy",
                "points": 15,
                "type": "concept",
                "description": """**EDA Checklist**

1. **Shape & Size**: rows, columns
2. **Data Types**: numeric, categorical, datetime
3. **Missing Values**: count, percentage
4. **Distributions**: histograms, box plots
5. **Correlations**: heatmaps
6. **Outliers**: IQR method, z-scores

```python
df.info()
df.describe()
df.isnull().sum()
df.hist()
```""",
                "starter_code": """import pandas as pd
# Load and explore your data
df = pd.read_csv('data.csv')
print(df.info())""",
                "hints": ["Always start with .info() and .describe()", "Visualize before modeling"],
                "solution_explanation": "EDA is 80% of a data scientist's work!"
            }
        ]
    }
}

# ============ DATA SCIENCE TRACK ============

DATA_SCIENCE_TRACKS = {
    "python_ds": {
        "name": "Python for Data Science",
        "description": "NumPy, Pandas, and data manipulation",
        "order": 1,
        "tasks": [
            {
                "id": "pyds-001",
                "title": "NumPy Arrays",
                "difficulty": "Easy",
                "points": 10,
                "type": "coding",
                "description": """**NumPy Basics**

NumPy is the foundation of Python data science.

```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5])
print(arr.mean())  # 3.0
print(arr.std())   # 1.414...

# Broadcasting
arr * 2  # [2, 4, 6, 8, 10]
```""",
                "starter_code": """import numpy as np

# Create an array and calculate statistics
arr = np.array([10, 20, 30, 40, 50])
# Your code here""",
                "hints": ["NumPy operations are vectorized", "Use .reshape() to change dimensions"],
                "solution_explanation": "NumPy is fast because operations happen in C"
            },
            {
                "id": "pyds-002",
                "title": "Pandas DataFrames",
                "difficulty": "Easy",
                "points": 15,
                "type": "coding",
                "description": """**Pandas Essentials**

```python
import pandas as pd

df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000, 60000, 70000]
})

# Filter
df[df['age'] > 25]

# Group
df.groupby('age')['salary'].mean()
```""",
                "starter_code": """import pandas as pd

# Create and manipulate a DataFrame
df = pd.DataFrame({
    'product': ['A', 'B', 'A', 'B'],
    'sales': [100, 200, 150, 250]
})
# Group by product and sum sales""",
                "hints": ["Use .groupby() for aggregations", ".loc[] for label-based indexing"],
                "solution_explanation": "Pandas is built on NumPy, adding labels and data manipulation"
            }
        ]
    },
    "statistics": {
        "name": "Statistics Simplified",
        "description": "Statistics concepts in plain English",
        "order": 2,
        "tasks": [
            {
                "id": "stats-001",
                "title": "Mean, Median, Mode",
                "difficulty": "Easy",
                "points": 10,
                "type": "concept",
                "description": """**Central Tendency**

- **Mean**: Average (sensitive to outliers)
- **Median**: Middle value (robust to outliers)
- **Mode**: Most frequent value

**Interview Question:** When to use median over mean?
Answer: When data has outliers (e.g., income data)

```python
import numpy as np
data = [1, 2, 2, 3, 100]
np.mean(data)    # 21.6 (skewed by 100)
np.median(data)  # 2 (better representation)
```""",
                "starter_code": "# Calculate mean, median, mode",
                "hints": ["Median is robust to outliers", "Mode can have multiple values"],
                "solution_explanation": "Understanding when to use each measure is crucial for interviews"
            },
            {
                "id": "stats-002",
                "title": "Standard Deviation & Variance",
                "difficulty": "Medium",
                "points": 15,
                "type": "concept",
                "description": """**Spread Measures**

- **Variance**: Average squared distance from mean
- **Std Dev**: Square root of variance (same units as data)

```python
data = [2, 4, 6, 8, 10]
variance = np.var(data)  # 8.0
std_dev = np.std(data)   # 2.83
```

**68-95-99.7 Rule**: In normal distribution:
- 68% within 1 std dev
- 95% within 2 std dev
- 99.7% within 3 std dev""",
                "starter_code": "# Calculate variance and std dev",
                "hints": ["Std dev has same units as data", "Variance is std dev squared"],
                "solution_explanation": "Standard deviation tells you how spread out data is"
            }
        ]
    }
}

# ============ ML TRACK ============

ML_TRACKS = {
    "ml_basics": {
        "name": "ML Fundamentals",
        "description": "Core machine learning concepts",
        "order": 1,
        "tasks": [
            {
                "id": "ml-001",
                "title": "Supervised vs Unsupervised",
                "difficulty": "Easy",
                "points": 10,
                "type": "concept",
                "description": """**Types of Machine Learning**

**Supervised Learning**
- Has labeled data (X → y)
- Examples: Classification, Regression
- Algorithms: Linear Regression, Random Forest, SVM

**Unsupervised Learning**
- No labels
- Examples: Clustering, Dimensionality Reduction
- Algorithms: K-Means, PCA, DBSCAN

**Interview Question:** Give an example of each.
- Supervised: Predicting house prices (regression)
- Unsupervised: Customer segmentation (clustering)""",
                "starter_code": "# Understand the difference",
                "hints": ["Labels = supervised", "No labels = unsupervised"],
                "solution_explanation": "This is a fundamental interview question!"
            },
            {
                "id": "ml-002",
                "title": "Overfitting & Underfitting",
                "difficulty": "Medium",
                "points": 20,
                "type": "concept",
                "description": """**Model Fitting**

**Underfitting** (High Bias)
- Model too simple
- Poor on training AND test data
- Fix: More features, complex model

**Overfitting** (High Variance)
- Model memorizes training data
- Great on training, poor on test
- Fix: Regularization, more data, simpler model

**The Sweet Spot**
- Good on both training and test
- Achieved through cross-validation""",
                "starter_code": "# Identify fitting issues",
                "hints": ["Training error low, test error high = overfitting", "Both errors high = underfitting"],
                "solution_explanation": "Understanding this trade-off is crucial for ML interviews"
            },
            {
                "id": "ml-003",
                "title": "Train-Test Split",
                "difficulty": "Easy",
                "points": 10,
                "type": "coding",
                "description": """**Data Splitting**

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

**Why split?**
- Evaluate on unseen data
- Prevent overfitting
- Common splits: 80/20, 70/30""",
                "starter_code": """from sklearn.model_selection import train_test_split
# Split your data""",
                "hints": ["random_state for reproducibility", "Stratify for imbalanced classes"],
                "solution_explanation": "Never evaluate on training data!"
            }
        ]
    }
}

# ============ JOB TRENDS DATA ============

JOB_TRENDS = [
    {
        "id": "trend-1",
        "title": "AI/ML Engineers in High Demand",
        "description": "Companies are actively hiring ML engineers with PyTorch/TensorFlow experience. Average salary: $150K+",
        "skills": ["Python", "PyTorch", "TensorFlow", "MLOps"],
        "category": "ML Engineer"
    },
    {
        "id": "trend-2", 
        "title": "Data Analytics Boom",
        "description": "SQL and Python skills are must-haves. Power BI and Tableau knowledge is a plus.",
        "skills": ["SQL", "Python", "Power BI", "Excel"],
        "category": "Data Analyst"
    },
    {
        "id": "trend-3",
        "title": "Full-Stack Still Strong",
        "description": "React + Node.js remains the most popular stack. TypeScript adoption increasing.",
        "skills": ["React", "Node.js", "TypeScript", "PostgreSQL"],
        "category": "SDE"
    },
    {
        "id": "trend-4",
        "title": "Cloud Skills Essential",
        "description": "AWS, GCP, and Azure certifications boost hiring chances significantly.",
        "skills": ["AWS", "Docker", "Kubernetes", "CI/CD"],
        "category": "SDE"
    }
]

# ============ RESUME TEMPLATES ============

RESUME_TEMPLATES = {
    "google": {
        "name": "Google",
        "focus": ["Impact metrics", "Technical depth", "Leadership"],
        "tips": [
            "Quantify impact (X% improvement, $Y saved)",
            "Highlight system design experience",
            "Show cross-team collaboration",
            "Include open-source contributions"
        ],
        "sections": ["Summary", "Experience", "Projects", "Skills", "Education"]
    },
    "microsoft": {
        "name": "Microsoft",
        "focus": ["Growth mindset", "Collaboration", "Innovation"],
        "tips": [
            "Emphasize learning and adaptation",
            "Show team collaboration examples",
            "Highlight product impact",
            "Include certifications if relevant"
        ],
        "sections": ["Summary", "Experience", "Projects", "Skills", "Education", "Certifications"]
    },
    "infosys": {
        "name": "Infosys",
        "focus": ["Technical skills", "Problem-solving", "Adaptability"],
        "tips": [
            "List all technical skills clearly",
            "Include academic projects",
            "Mention relevant coursework",
            "Highlight internship experience"
        ],
        "sections": ["Objective", "Education", "Skills", "Projects", "Internships", "Achievements"]
    },
    "amazon": {
        "name": "Amazon",
        "focus": ["Leadership Principles", "Customer obsession", "Ownership"],
        "tips": [
            "Use STAR format for experiences",
            "Align with Amazon's 16 Leadership Principles",
            "Show customer-centric thinking",
            "Demonstrate bias for action"
        ],
        "sections": ["Summary", "Experience", "Projects", "Skills", "Education"]
    }
}

# ============ AUTH ROUTES ============

@api_router.post("/auth/register")
async def register(user: UserCreate):
    if not is_valid_edu_email(user.email):
        raise HTTPException(status_code=400, detail="Please use a valid educational email")
    
    existing = await db.users.find_one({"email": user.email.lower()}, {"_id": 0, "id": 1})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": user.email.lower(),
        "name": user.name,
        "password_hash": hash_password(user.password),
        "role": None,
        "points": 0,
        "level": "Beginner",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "progress": {},
        "weekly_activity": {"dsa": 0, "github": 0, "linkedin": 0},
        "streak": {"current": 0, "longest": 0, "last_activity": None},
        "resumes": []
    }
    
    await db.users.insert_one(user_doc)
    token = create_token(user_id, user.email)
    
    return {
        "token": token,
        "user": {"id": user_id, "email": user.email.lower(), "name": user.name, "role": None, "points": 0, "level": "Beginner"}
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email.lower()}, {"_id": 0})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token(user["id"], user["email"])
    return {
        "token": token,
        "user": {"id": user["id"], "email": user["email"], "name": user["name"], "role": user.get("role"), "points": user.get("points", 0), "level": user.get("level", "Beginner")}
    }

# ============ USER ROUTES ============

@api_router.get("/users/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user.get("role"),
        "points": user.get("points", 0),
        "level": user.get("level", "Beginner"),
        "progress": user.get("progress", {}),
        "weekly_activity": user.get("weekly_activity", {}),
        "streak": user.get("streak", {"current": 0, "longest": 0}),
        "resumes": user.get("resumes", [])
    }

@api_router.put("/users/role")
async def update_role(role_data: RoleUpdate, user: dict = Depends(get_current_user)):
    valid_roles = ["SDE", "Data Analyst", "Data Scientist", "ML Engineer"]
    if role_data.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Choose from: {valid_roles}")
    
    await db.users.update_one({"id": user["id"]}, {"$set": {"role": role_data.role}})
    return {"message": "Role updated", "role": role_data.role}

@api_router.post("/users/streak")
async def update_streak(streak_data: StreakUpdate, user: dict = Depends(get_current_user)):
    current_streak = user.get("streak", {"current": 0, "longest": 0, "last_activity": None})
    last_activity = current_streak.get("last_activity")
    today = datetime.now(timezone.utc).date().isoformat()
    
    if last_activity == today:
        return {"message": "Already logged today", "streak": current_streak}
    
    yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    
    if last_activity == yesterday:
        new_current = current_streak.get("current", 0) + 1
    else:
        new_current = 1
    
    new_longest = max(new_current, current_streak.get("longest", 0))
    
    new_streak = {"current": new_current, "longest": new_longest, "last_activity": today}
    
    # Update weekly activity
    activity_key = f"weekly_activity.{streak_data.activity_type}"
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"streak": new_streak}, "$inc": {activity_key: 1}}
    )
    
    return {"message": "Streak updated!", "streak": new_streak}

# ============ SKILLS ROUTES ============

@api_router.get("/skills/dsa")
async def get_dsa_tracks(user: dict = Depends(get_current_user)):
    tracks = []
    for key, track in DSA_TRACKS.items():
        user_progress = user.get("progress", {})
        completed = sum(1 for t in track["tasks"] if user_progress.get(t["id"], {}).get("completed", False))
        tracks.append({
            "id": key,
            "name": track["name"],
            "description": track["description"],
            "order": track["order"],
            "total_tasks": len(track["tasks"]),
            "completed_tasks": completed
        })
    return {"tracks": sorted(tracks, key=lambda x: x["order"])}

@api_router.get("/skills/dsa/{track_id}")
async def get_dsa_track(track_id: str, user: dict = Depends(get_current_user)):
    if track_id not in DSA_TRACKS:
        raise HTTPException(status_code=404, detail="Track not found")
    
    track = DSA_TRACKS[track_id]
    user_progress = user.get("progress", {})
    
    tasks_with_progress = []
    for task in track["tasks"]:
        task_copy = task.copy()
        task_copy["completed"] = user_progress.get(task["id"], {}).get("completed", False)
        task_copy["attempts"] = user_progress.get(task["id"], {}).get("attempts", 0)
        tasks_with_progress.append(task_copy)
    
    return {
        "id": track_id,
        "name": track["name"],
        "description": track["description"],
        "total_tasks": len(track["tasks"]),
        "completed_tasks": sum(1 for t in tasks_with_progress if t["completed"]),
        "tasks": tasks_with_progress
    }

@api_router.get("/skills/dsa/{track_id}/{task_id}")
async def get_dsa_task(track_id: str, task_id: str, user: dict = Depends(get_current_user)):
    if track_id not in DSA_TRACKS:
        raise HTTPException(status_code=404, detail="Track not found")
    
    task = next((t for t in DSA_TRACKS[track_id]["tasks"] if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    user_progress = user.get("progress", {}).get(task_id, {})
    task_copy = task.copy()
    task_copy["completed"] = user_progress.get("completed", False)
    task_copy["attempts"] = user_progress.get("attempts", 0)
    
    return task_copy

@api_router.get("/skills/analytics")
async def get_analytics_tracks(user: dict = Depends(get_current_user)):
    tracks = []
    for key, track in DATA_ANALYTICS_TRACKS.items():
        user_progress = user.get("progress", {})
        completed = sum(1 for t in track["tasks"] if user_progress.get(t["id"], {}).get("completed", False))
        tracks.append({
            "id": key,
            "name": track["name"],
            "description": track["description"],
            "total_tasks": len(track["tasks"]),
            "completed_tasks": completed
        })
    return {"tracks": tracks}

@api_router.get("/skills/analytics/{track_id}")
async def get_analytics_track(track_id: str, user: dict = Depends(get_current_user)):
    if track_id not in DATA_ANALYTICS_TRACKS:
        raise HTTPException(status_code=404, detail="Track not found")
    
    track = DATA_ANALYTICS_TRACKS[track_id]
    user_progress = user.get("progress", {})
    
    tasks = []
    for task in track["tasks"]:
        task_copy = task.copy()
        task_copy["completed"] = user_progress.get(task["id"], {}).get("completed", False)
        tasks.append(task_copy)
    
    return {"id": track_id, "name": track["name"], "tasks": tasks}

@api_router.get("/skills/datascience")
async def get_datascience_tracks(user: dict = Depends(get_current_user)):
    tracks = []
    for key, track in DATA_SCIENCE_TRACKS.items():
        user_progress = user.get("progress", {})
        completed = sum(1 for t in track["tasks"] if user_progress.get(t["id"], {}).get("completed", False))
        tracks.append({
            "id": key,
            "name": track["name"],
            "description": track["description"],
            "total_tasks": len(track["tasks"]),
            "completed_tasks": completed
        })
    return {"tracks": tracks}

@api_router.get("/skills/ml")
async def get_ml_tracks(user: dict = Depends(get_current_user)):
    tracks = []
    for key, track in ML_TRACKS.items():
        user_progress = user.get("progress", {})
        completed = sum(1 for t in track["tasks"] if user_progress.get(t["id"], {}).get("completed", False))
        tracks.append({
            "id": key,
            "name": track["name"],
            "description": track["description"],
            "total_tasks": len(track["tasks"]),
            "completed_tasks": completed
        })
    return {"tracks": tracks}

# ============ TASK SUBMISSION ============

@api_router.post("/tasks/{task_id}/submit")
async def submit_task(task_id: str, submission: TaskSubmission, user: dict = Depends(get_current_user)):
    # Find task in all tracks
    task = None
    for track_data in [DSA_TRACKS, DATA_ANALYTICS_TRACKS, DATA_SCIENCE_TRACKS, ML_TRACKS]:
        for track in track_data.values():
            task = next((t for t in track["tasks"] if t["id"] == task_id), None)
            if task:
                break
        if task:
            break
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    progress_key = f"progress.{task_id}"
    current_progress = user.get("progress", {}).get(task_id, {"attempts": 0, "completed": False})
    
    new_progress = {
        "attempts": current_progress.get("attempts", 0) + 1,
        "completed": True,
        "last_submission": datetime.now(timezone.utc).isoformat(),
        "code": submission.code
    }
    
    points_earned = 0
    if not current_progress.get("completed"):
        points_earned = task.get("points", 10)
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {progress_key: new_progress}, "$inc": {"points": points_earned}}
        )
        
        # Update level
        updated_user = await db.users.find_one({"id": user["id"]}, {"_id": 0, "points": 1})
        total_points = updated_user.get("points", 0)
        new_level = "Beginner"
        if total_points >= 200:
            new_level = "Advanced"
        elif total_points >= 100:
            new_level = "Intermediate"
        
        await db.users.update_one({"id": user["id"]}, {"$set": {"level": new_level}})
    else:
        await db.users.update_one({"id": user["id"]}, {"$set": {progress_key: new_progress}})
    
    return {"success": True, "points_earned": points_earned, "message": "Great work!" if points_earned > 0 else "Submission recorded."}

# ============ BRO MENTOR ROUTES ============

@api_router.post("/bro/chat")
async def chat_with_bro(message: ChatMessage, user: dict = Depends(get_current_user)):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    system_prompt = f"""You are BRO, an open-source AI mentor for college students preparing for tech placements.

Your personality:
- Friendly and supportive like a senior engineer friend
- Use casual but professional language
- Never spoon-feed answers - guide students to think
- Give hints and ask guiding questions
- Explain concepts in simple, relatable terms
- Use analogies from real life
- Be encouraging but realistic
- Share interview tips when relevant

Rules:
- Never give complete code solutions directly
- Ask "What have you tried?" before helping
- Break down complex problems into smaller steps
- Celebrate small wins
- If someone's stuck, give hints not answers
- Keep responses concise but helpful

You help with: DSA, Data Analytics, Data Science, ML, Resume Building, Interview Prep.
Current user: {user.get("name", "Student")} (Level: {user.get("level", "Beginner")}, Role: {user.get("role", "Not Set")})"""

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"bro-{user['id']}-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
            system_message=system_prompt
        )
        chat.with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(text=message.message)
        response = await chat.send_message(user_message)
        
        chat_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["id"],
            "message": message.message,
            "response": response,
            "context": message.context,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.chat_history.insert_one(chat_doc)
        
        return {"response": response}
    except Exception as e:
        logger.error(f"BRO chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="BRO is taking a coffee break. Try again!")

@api_router.post("/bro/voice")
async def bro_voice_input(audio: UploadFile = File(...), context: str = Form(None), user: dict = Depends(get_current_user)):
    """Handle voice input - transcribe and respond"""
    from emergentintegrations.llm.openai import OpenAISpeechToText
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        # Save uploaded audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Transcribe audio
        stt = OpenAISpeechToText(api_key=api_key)
        with open(tmp_path, "rb") as audio_file:
            transcription = await stt.transcribe(
                file=audio_file,
                model="whisper-1",
                response_format="json",
                language="en"
            )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        transcribed_text = transcription.text
        
        # Now get BRO's response
        system_prompt = f"""You are BRO, a friendly AI mentor. The user is speaking to you via voice.
Keep responses concise and conversational.
User: {user.get("name")} (Level: {user.get("level")})"""
        
        chat = LlmChat(api_key=api_key, session_id=f"bro-voice-{user['id']}", system_message=system_prompt)
        chat.with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=transcribed_text))
        
        return {
            "transcription": transcribed_text,
            "response": response
        }
    except Exception as e:
        logger.error(f"Voice processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Voice processing failed. Try text instead!")

@api_router.get("/bro/history")
async def get_chat_history(user: dict = Depends(get_current_user)):
    history = await db.chat_history.find(
        {"user_id": user["id"]}, {"_id": 0}
    ).sort("timestamp", -1).limit(50).to_list(50)
    return {"history": history}

# ============ RESUME ROUTES ============

@api_router.get("/resume/templates")
async def get_resume_templates():
    return {"templates": RESUME_TEMPLATES}

@api_router.post("/resume/create")
async def create_resume(resume_data: ResumeCreate, user: dict = Depends(get_current_user)):
    resume_id = str(uuid.uuid4())
    resume = {
        "id": resume_id,
        "company": resume_data.company,
        "template": resume_data.template,
        "content": resume_data.content,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.update_one(
        {"id": user["id"]},
        {"$push": {"resumes": resume}}
    )
    
    return {"message": "Resume created", "resume_id": resume_id}

@api_router.get("/resume/list")
async def list_resumes(user: dict = Depends(get_current_user)):
    return {"resumes": user.get("resumes", [])}

@api_router.put("/resume/{resume_id}")
async def update_resume(resume_id: str, resume_data: ResumeUpdate, user: dict = Depends(get_current_user)):
    resumes = user.get("resumes", [])
    resume_idx = next((i for i, r in enumerate(resumes) if r["id"] == resume_id), None)
    
    if resume_idx is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    resumes[resume_idx]["content"] = resume_data.content
    if resume_data.template:
        resumes[resume_idx]["template"] = resume_data.template
    resumes[resume_idx]["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.users.update_one({"id": user["id"]}, {"$set": {"resumes": resumes}})
    
    return {"message": "Resume updated"}

@api_router.post("/resume/analyze")
async def analyze_resume(resume_data: ResumeCreate, user: dict = Depends(get_current_user)):
    """AI-powered resume analysis"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    template = RESUME_TEMPLATES.get(resume_data.company.lower(), RESUME_TEMPLATES["google"])
    
    prompt = f"""Analyze this resume for {resume_data.company} application.

Resume Content:
{resume_data.content}

Company Focus Areas: {', '.join(template['focus'])}
Tips for this company: {'; '.join(template['tips'])}

Provide:
1. Strength Analysis (what's good)
2. Gap Analysis (what's missing)
3. Specific Improvement Suggestions
4. ATS Compatibility Score (1-10)

Keep it concise and actionable."""

    try:
        chat = LlmChat(api_key=api_key, session_id=f"resume-{user['id']}", system_message="You are a professional resume reviewer.")
        chat.with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=prompt))
        return {"analysis": response}
    except Exception as e:
        logger.error(f"Resume analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")

# ============ CONTENT GENERATION ============

@api_router.post("/generate/linkedin")
async def generate_linkedin_post(request: LinkedInDraftRequest, user: dict = Depends(get_current_user)):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    prompt = f"""Generate a professional LinkedIn post about learning {request.topic} ({request.learning_type}).

Requirements:
- Keep it authentic and personal
- Include what you learned
- Add a call-to-action or question
- Use 2-3 relevant hashtags
- Keep it under 200 words

User's name: {user.get('name')}
User's role goal: {user.get('role')}"""

    try:
        chat = LlmChat(api_key=api_key, session_id=f"linkedin-{user['id']}", system_message="You write engaging LinkedIn posts.")
        chat.with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=prompt))
        return {"draft": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Generation failed")

@api_router.post("/generate/github")
async def generate_github_commit(request: GitHubDraftRequest, user: dict = Depends(get_current_user)):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    prompt = f"""Generate a professional GitHub commit message and README update for:

Project: {request.project_name}
Changes: {request.changes}

Provide:
1. Commit message (conventional commits format)
2. README update snippet"""

    try:
        chat = LlmChat(api_key=api_key, session_id=f"github-{user['id']}", system_message="You write clear technical documentation.")
        chat.with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=prompt))
        return {"draft": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Generation failed")

# ============ JOB TRENDS ============

@api_router.get("/trends")
async def get_job_trends(user: dict = Depends(get_current_user)):
    user_role = user.get("role", "SDE")
    relevant_trends = [t for t in JOB_TRENDS if t["category"] == user_role or t["category"] == "All"]
    if not relevant_trends:
        relevant_trends = JOB_TRENDS[:2]
    return {"trends": relevant_trends, "user_role": user_role}

# ============ PLACEMENT READINESS ============

@api_router.get("/readiness")
async def get_readiness_score(user: dict = Depends(get_current_user)):
    progress = user.get("progress", {})
    points = user.get("points", 0)
    level = user.get("level", "Beginner")
    role = user.get("role", "SDE")
    streak = user.get("streak", {})
    
    # Calculate skill scores
    dsa_completed = sum(1 for k, v in progress.items() if k.startswith(("arr", "str", "ll", "sq", "tree", "dp")) and v.get("completed"))
    analytics_completed = sum(1 for k, v in progress.items() if k.startswith(("sql", "excel", "eda")) and v.get("completed"))
    ds_completed = sum(1 for k, v in progress.items() if k.startswith(("pyds", "stats")) and v.get("completed"))
    ml_completed = sum(1 for k, v in progress.items() if k.startswith("ml") and v.get("completed"))
    
    # Role-specific readiness
    if role == "SDE":
        skill_score = min(100, (dsa_completed / 20) * 100)
    elif role == "Data Analyst":
        skill_score = min(100, (analytics_completed / 6) * 100)
    elif role == "Data Scientist":
        skill_score = min(100, ((ds_completed + analytics_completed) / 10) * 100)
    else:  # ML Engineer
        skill_score = min(100, ((ml_completed + dsa_completed) / 15) * 100)
    
    consistency_score = min(100, (streak.get("current", 0) / 7) * 100)
    
    overall_readiness = int((skill_score * 0.6) + (consistency_score * 0.2) + (min(points, 200) / 200 * 100 * 0.2))
    
    return {
        "overall_readiness": overall_readiness,
        "skill_score": int(skill_score),
        "consistency_score": int(consistency_score),
        "points": points,
        "level": level,
        "role": role,
        "breakdown": {
            "dsa": dsa_completed,
            "analytics": analytics_completed,
            "datascience": ds_completed,
            "ml": ml_completed
        },
        "streak": streak,
        "recommendations": [
            "Complete more DSA problems" if dsa_completed < 10 else "Great DSA progress!",
            "Maintain your streak for better consistency" if streak.get("current", 0) < 7 else "Awesome streak!",
            "Try SQL problems for analytics" if analytics_completed < 3 else "Good analytics skills!"
        ]
    }

# ============ CODE EXECUTION ============

@api_router.post("/code/run")
async def run_code(request: CodeRunRequest, user: dict = Depends(get_current_user)):
    code = request.code
    
    dangerous_keywords = ["import os", "import subprocess", "exec(", "eval(", "open(", "__import__"]
    for kw in dangerous_keywords:
        if kw in code:
            return {"success": False, "output": "", "error": f"Security Error: '{kw}' is not allowed."}
    
    if "print(" in code:
        return {
            "success": True,
            "output": "Code executed! (Demo mode)\n\nTip: Use 'Submit' to validate against test cases.",
            "error": None
        }
    
    return {"success": True, "output": "No output. Add print() statements.", "error": None}

# ============ ROOT ============

@api_router.get("/")
async def root():
    return {"message": "SkillForge API", "version": "2.0.0"}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
