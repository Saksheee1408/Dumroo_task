# 🎓 Dumroo Admin Panel - AI-Powered Student Query System

An intelligent admin panel that allows administrators to query student data using **natural language**, powered by Groq AI and LangChain.

## ✨ Features

- 🤖 **Natural Language Queries** - Ask questions in plain English
- 🔒 **Role-Based Access Control** - Admins see only their scope (region/grade/class)
- 📊 **Smart Data Filtering** - Automatic filtering based on admin permissions
- 📥 **CSV Export** - Download query results instantly
- ⚡ **Fast Processing** - Powered by Groq AI (Free & Fast)
- 🎯 **Simple UI** - Clean, intuitive interface with no clutter

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API Key (Free: https://console.groq.com)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Dumroo.ai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.1-8b-instant
```

4. **Run the application**
```bash
streamlit run app.py
```

5. **Open in browser**
```
http://localhost:8501
```

## 📁 Project Structure

```
Dumroo.ai/
├── src/
│   ├── __init__.py
│   ├── data_loader.py      # Load student & admin data
│   ├── query_parser.py     # AI query parser (Groq + LangChain)
│   └── role_filter.py      # Role-based access control
├── data/
│   ├── students.json       # Student records
│   └── admins.json         # Admin profiles
├── tests/
│   └── test_queries.py     # Query testing
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
└── README.md
```

## 📊 Data Format

### students.json
```json
[
  {
    "student_id": "S001",
    "student_name": "Rahul Sharma",
    "grade": 8,
    "class": "A",
    "region": "North",
    "quiz_score": 85,
    "homework_status": "submitted",
    "date": "2024-01-15"
  }
]
```

### admins.json
```json
[
  {
    "admin_id": "A001",
    "name": "Priya Patel",
    "role": "principal",
    "region": "all",
    "grade": "all",
    "class": "all"
  }
]
```

## 💬 Example Queries

### Basic Queries
- "Who is the topper student?"
- "Show all students"
- "Count total students"

### Homework Queries
- "Which students haven't submitted homework?"
- "Show students with pending homework"
- "List submitted homework"

### Score-Based Queries
- "Show students who scored above 80"
- "Students with scores below 70"
- "Top 5 performers"
- "Students between 75 and 90 marks"

### Filtered Queries
- "Grade 8 students with pending homework"
- "Class A students who scored above 85"
- "Show North region students"

### Advanced Queries
- "Show Grade 8 Class A students from North region with quiz score above 80"
- "Count students with pending homework in Grade 9"
- "Top 10 students sorted by quiz score"

## 🔑 Admin Roles & Permissions

| Role | Access Level | Can View |
|------|-------------|----------|
| **Principal** | Full Access | All regions, grades, classes |
| **Regional Manager** | Region-specific | All grades/classes in their region |
| **Grade Coordinator** | Grade-specific | All classes in their grade |
| **Class Teacher** | Class-specific | Only their class students |

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python Web Framework)
- **AI Engine**: Groq AI (Fast LLM Inference)
- **Framework**: LangChain (AI Application Framework)
- **Data Processing**: Pandas
- **Language Model**: Llama 3.1 8B Instant

## 📖 How It Works

1. **Admin Login** → Select admin profile from sidebar
2. **Query Input** → Type natural language question or use quick actions
3. **AI Processing** → Groq AI parses query and extracts filters
4. **Role Filtering** → System applies role-based access control
5. **Results Display** → Shows filtered data in clean table
6. **Export** → Download results as CSV

## 🧪 Testing

Run the test suite:
```bash
python tests/test_queries.py
```

Test various query patterns:
- Homework status queries
- Score-based filtering
- Role-based access
- Date filtering
- Sorting and limiting

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key | Required |
| `MODEL_NAME` | Groq model to use | `llama-3.1-8b-instant` |

### Customize Quick Actions

Edit `app.py` to add/modify quick action buttons:
```python
if st.button("🏆 Show Topper"):
    user_query = "Who is the topper student?"
```

## 📝 Adding New Data

### Add Students
1. Open `data/students.json`
2. Add new student records following the schema
3. Restart the app

### Add Admins
1. Open `data/admins.json`
2. Add new admin profiles with appropriate roles
3. Restart the app

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
- Ensure `.env` file exists in root directory
- Verify `GROQ_API_KEY` is set correctly

### "No students in your scope"
- Check admin role permissions in `admins.json`
- Verify student data exists in `students.json`

### Query not working
- Try rephrasing the question
- Use quick action buttons for common queries
- Check available columns in student data

## 🚧 Roadmap

- [ ] Authentication system (login/logout)
- [ ] Student profile editing
- [ ] Bulk data import (CSV/Excel)
- [ ] Email notifications
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please create an issue in the repository.

---

**Built with ❤️ using Groq AI, LangChain & Streamlit**
