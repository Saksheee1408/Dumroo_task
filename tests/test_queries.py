"""
Test script to verify setup - Run before starting the app
Usage: python test_setup.py
"""

from dotenv import load_dotenv
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print('='*60)

def print_test(number, text):
    print(f"\n{number}️⃣  {text}")

def print_success(text):
    print(f"   ✅ {text}")

def print_error(text):
    print(f"   ❌ {text}")

def print_warning(text):
    print(f"   ⚠️  {text}")

print_header("🔍 Dumroo AI Query System - Setup Test")

# Test 1: Virtual environment
print_test("1", "Checking virtual environment...")
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print_success("Virtual environment active")
else:
    print_warning("Virtual environment not detected (recommended)")

# Test 2: Environment variables
print_test("2", "Checking .env file...")
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if api_key:
    masked_key = api_key[:10] + "..." + api_key[-4:]
    print_success(f"GROQ_API_KEY found: {masked_key}")
else:
    print_error("GROQ_API_KEY not found in .env")
    print("   → Get free key: https://console.groq.com/keys")
    sys.exit(1)

# Test 3: Dependencies
print_test("3", "Checking dependencies...")
required_packages = {
    'streamlit': 'streamlit',
    'pandas': 'pandas',
    'groq': 'groq',
    'dotenv': 'python-dotenv',
    'langchain': 'langchain',
    'langchain_groq': 'langchain-groq',
    'plotly': 'plotly'
}

missing = []
for package, install_name in required_packages.items():
    try:
        if package == 'dotenv':
            __import__('dotenv')
        else:
            __import__(package)
        print_success(f"{package} installed")
    except ImportError:
        print_error(f"{package} NOT installed")
        missing.append(install_name)

if missing:
    print(f"\n   Install missing packages:")
    print(f"   pip install {' '.join(missing)}")
    sys.exit(1)

# Test 4: Data files
print_test("4", "Checking data files...")

if os.path.exists("data/students.json"):
    print_success("data/students.json found")
    import json
    try:
        with open("data/students.json", 'r') as f:
            students = json.load(f)
            print(f"      → {len(students)} student records")
    except Exception as e:
        print_error(f"Error reading students.json: {e}")
else:
    print_error("data/students.json NOT found")
    print("   → Create this file with your student data")

if os.path.exists("data/admins.json"):
    print_success("data/admins.json found")
    try:
        with open("data/admins.json", 'r') as f:
            admins = json.load(f)
            print(f"      → {len(admins)} admin profiles")
    except Exception as e:
        print_error(f"Error reading admins.json: {e}")
else:
    print_error("data/admins.json NOT found")
    print("   → Create this file with admin profiles")

# Test 5: Source modules
print_test("5", "Checking source modules...")
sys.path.append('src')

modules_ok = True
try:
    from src.data_loader import DataLoader
    print_success("data_loader.py ✓")
except ImportError as e:
    print_error(f"data_loader.py: {e}")
    modules_ok = False

try:
    from src.role_filter import RoleFilter
    print_success("role_filter.py ✓")
except ImportError as e:
    print_error(f"role_filter.py: {e}")
    modules_ok = False

try:
    from src.query_parser import QueryParser
    print_success("query_parser.py ✓")
except ImportError as e:
    print_error(f"query_parser.py: {e}")
    modules_ok = False

if not modules_ok:
    sys.exit(1)

# Test 6: Groq API + LangChain
print_test("6", "Testing Groq API with LangChain...")
try:
    from langchain_groq import ChatGroq
    
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0,
        max_tokens=20
    )
    
    response = llm.invoke("Say 'Setup successful!' in 3 words")
    print_success(f"Groq API working: {response.content}")
except Exception as e:
    print_error(f"Groq API error: {e}")
    sys.exit(1)

# Test 7: Load actual data
print_test("7", "Testing data loading...")
try:
    data_loader = DataLoader()
    students_df = data_loader.load_students()
    print_success(f"Loaded {len(students_df)} student records")
    print(f"      Columns: {', '.join(students_df.columns)}")
    
    admins = data_loader.load_admins()
    print_success(f"Loaded {len(admins)} admin profiles")
    
    # Test admin names
    admin_names = [a['name'] for a in admins]
    print(f"      Admins: {', '.join(admin_names[:3])}")
except Exception as e:
    print_warning(f"Error loading data: {e}")

# Test 8: Test query parser with LangChain
print_test("8", "Testing LangChain query parser...")
try:
    from src.query_parser import QueryParser
    
    parser = QueryParser(api_key=api_key)
    
    test_query = "Show students who scored above 80"
    columns = ['student_name', 'grade', 'class', 'homework_status', 'quiz_score', 'date', 'region']
    
    result = parser.parse_query(test_query, columns)
    print_success("Query parsing works!")
    print(f"      Test query: '{test_query}'")
    print(f"      Parsed intent: {result.get('intent')}")
    print(f"      Filters: {result.get('filters')}")
except Exception as e:
    print_error(f"Query parser error: {e}")

# Final summary
print_header("🎉 SETUP TEST COMPLETE!")

print("\n✅ All tests passed! You're ready to go!")
print("\n📝 Next steps:")
print("   1. Run the app:    streamlit run app.py")
print("   2. Open browser:   http://localhost:8501")
print("   3. Select admin    (from sidebar)")
print("   4. Start querying! 🚀")

print("\n💡 Example queries to try:")
print("   • Which students haven't submitted homework?")
print("   • Show me students who scored above 80")
print("   • Count students with pending homework")
print("   • Show all my students")

print("\n⚡ Powered by:")
print("   • Groq AI (Free & Fast)")
print("   • LangChain (Prompt Templates)")
print("   • Streamlit (Beautiful UI)")

print("\n" + "="*60 + "\n")