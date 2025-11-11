import os
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

# ✅ Updated imports (no more pydantic_v1 warning)
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


# ------------------------- Pydantic Schemas -------------------------
class FilterOperator(BaseModel):
    """Schema for complex filter operations"""
    operator: str = Field(description="Comparison operator: >, <, >=, <=, !=, =")
    value: float = Field(description="Value to compare against")


class QueryIntent(BaseModel):
    """Schema for parsed query intent and filters"""
    intent: str = Field(description="Query intent: list, count, show, or filter")
    filters: Dict = Field(default={}, description="Dictionary of column filters")
    date_filter: Optional[str] = Field(default=None, description="Date filter: today, yesterday, last_week, last_month, next_week, or null")
    specific_date: Optional[str] = Field(default=None, description="Specific date in YYYY-MM-DD format")
    sort_by: Optional[str] = Field(default=None, description="Column name to sort by")
    limit: Optional[int] = Field(default=None, description="Maximum number of results to return")


# ------------------------- Query Parser -------------------------
class QueryParser:
    """Parse natural language queries using Groq API with LangChain"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GROQ_API_KEY not found. Please set it in .env file")

        # ✅ Always use an active Groq model
        self.llm = ChatGroq(
            groq_api_key=self.api_key,
            model_name=os.getenv("MODEL_NAME", "llama-3.1-8b-instant"),
            temperature=0,
            max_tokens=500
        )

        self.parser = JsonOutputParser(pydantic_object=QueryIntent)

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a query parser for a student management system.
Extract structured information from natural language queries.

Available data columns: {columns}

Rules:
1. homework_status must be either "submitted" or "not_submitted"
   - Treat "pending", "not submitted", "haven't submitted" as "not_submitted"
   - Treat "submitted", "completed", "done" as "submitted"

2. For score comparisons:
   {{"quiz_score": {{"operator": ">", "value": 80}}}}

3. Intent types:
   - "list" → show records
   - "count" → count records
   - "filter" → filter records

{format_instructions}

Examples:
"Which students haven't submitted homework?"
→ {{"intent": "list", "filters": {{"homework_status": "not_submitted"}}}}

"Show me Grade 8 students who scored above 80"
→ {{"intent": "list", "filters": {{"grade": 8, "quiz_score": {{"operator": ">", "value": 80}}}}}}

"Count students with pending homework"
→ {{"intent": "count", "filters": {{"homework_status": "not_submitted"}}}}

"Show top 5 performers"
→ {{"intent": "list", "filters": {{}}, "sort_by": "quiz_score", "limit": 5}}
"""),
            ("human", "{query}")
        ])

        self.chain = self.prompt_template | self.llm | self.parser

    # ------------------------- Parse Query -------------------------
    def parse_query(self, user_query: str, available_columns: List[str]) -> Dict:
        try:
            format_instructions = self.parser.get_format_instructions()
            result = self.chain.invoke({
                "query": user_query,
                "columns": ", ".join(available_columns),
                "format_instructions": format_instructions
            })

            result.setdefault("intent", "list")
            result.setdefault("filters", {})
            print(f"✅ Parsed query: {result}")
            return result
        except Exception as e:
            print(f"⚠️ Error parsing query: {str(e)}")
            return self._get_default_query()

    def _get_default_query(self) -> Dict:
        return {
            "intent": "list",
            "filters": {},
            "date_filter": None,
            "specific_date": None,
            "sort_by": None,
            "limit": None
        }

    # ------------------------- Apply Filters -------------------------
    def apply_filters(self, df: pd.DataFrame, parsed_query: Dict) -> pd.DataFrame:
        if df is None or df.empty:
            return df

        filtered_df = df.copy()

        # ✅ Normalize homework_status variations
        if "homework_status" in filtered_df.columns:
            filtered_df["homework_status"] = filtered_df["homework_status"].str.lower().replace({
                "pending": "not_submitted",
                "not submitted": "not_submitted",
                "haven't submitted": "not_submitted",
                "submitted": "submitted",
                "completed": "submitted",
                "done": "submitted"
            })

        # ✅ Convert 'date' column to datetime if it's string
        if "date" in filtered_df.columns:
            filtered_df["date"] = pd.to_datetime(filtered_df["date"], errors="coerce")

        # Apply filters
        for column, value in parsed_query.get("filters", {}).items():
            if column not in filtered_df.columns:
                print(f"⚠️ Column '{column}' not found, skipping filter")
                continue

            if isinstance(value, dict) and "operator" in value:
                op, val = value["operator"], value["value"]
                if op in [">", "greater than"]:
                    filtered_df = filtered_df[filtered_df[column] > val]
                elif op in ["<", "less than"]:
                    filtered_df = filtered_df[filtered_df[column] < val]
                elif op in [">=", "greater than or equal"]:
                    filtered_df = filtered_df[filtered_df[column] >= val]
                elif op in ["<=", "less than or equal"]:
                    filtered_df = filtered_df[filtered_df[column] <= val]
                elif op in ["!=", "not equal"]:
                    filtered_df = filtered_df[filtered_df[column] != val]
                elif op in ["=", "equal"]:
                    filtered_df = filtered_df[filtered_df[column] == val]
            else:
                filtered_df = filtered_df[filtered_df[column] == value]

        # ✅ Date filters
        today = pd.Timestamp.now()
        date_filter = parsed_query.get("date_filter")
        if date_filter and "date" in filtered_df.columns:
            if date_filter == "today":
                filtered_df = filtered_df[filtered_df["date"].dt.date == today.date()]
            elif date_filter == "yesterday":
                yesterday = today - timedelta(days=1)
                filtered_df = filtered_df[filtered_df["date"].dt.date == yesterday.date()]
            elif date_filter == "last_week":
                last_week = today - timedelta(days=7)
                filtered_df = filtered_df[filtered_df["date"] >= last_week]
            elif date_filter == "last_month":
                last_month = today - timedelta(days=30)
                filtered_df = filtered_df[filtered_df["date"] >= last_month]
            elif date_filter == "next_week":
                next_week = today + timedelta(days=7)
                filtered_df = filtered_df[(filtered_df["date"] >= today) & (filtered_df["date"] <= next_week)]

        # ✅ Specific date
        if parsed_query.get("specific_date") and "date" in filtered_df.columns:
            target = pd.to_datetime(parsed_query["specific_date"], errors="coerce")
            filtered_df = filtered_df[filtered_df["date"].dt.date == target.date()]

        # ✅ Sorting and limit
        sort_by = parsed_query.get("sort_by")
        if sort_by in filtered_df.columns:
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=False)

        limit = parsed_query.get("limit")
        if isinstance(limit, int):
            filtered_df = filtered_df.head(limit)

        return filtered_df

    # ------------------------- Execute Query -------------------------
    def execute_query(self, df: pd.DataFrame, parsed_query: Dict) -> Dict:
        filtered_df = self.apply_filters(df, parsed_query)
        intent = parsed_query.get("intent", "list")

        if intent == "count":
            return {"intent": "count", "count": len(filtered_df), "data": None, "parsed_query": parsed_query}
        else:
            return {"intent": intent, "count": len(filtered_df), "data": filtered_df, "parsed_query": parsed_query}

    # ------------------------- Generate Summary -------------------------
    def generate_summary(self, results: Dict) -> str:
        count = results.get("count", 0)
        intent = results.get("intent", "list")

        if count == 0:
            return "No records found matching your query."
        if intent == "count":
            return f"Found {count} record(s) matching your criteria."
        if count == 1:
            return "Found 1 record matching your query."
        return f"Found {count} records matching your query."
