import json
import pandas as pd
from typing import Dict, List, Optional

class DataLoader:
    """Load and manage JSON data for students and admins"""
    
    def __init__(self, students_path: str = "data/students.json", 
                 admins_path: str = "data/admins.json"):
        self.students_path = students_path
        self.admins_path = admins_path
        self.students_df = None
        self.admins = None
        
    def load_students(self) -> pd.DataFrame:
        """Load students from JSON file into DataFrame"""
        try:
            with open(self.students_path, 'r', encoding='utf-8') as f:
                students = json.load(f)
            
            # Data is a direct list
            if not isinstance(students, list):
                raise ValueError("students.json should be a JSON array")
            
            self.students_df = pd.DataFrame(students)
            
            # Convert date column to datetime
            if 'date' in self.students_df.columns:
                self.students_df['date'] = pd.to_datetime(self.students_df['date'])
            
            # Standardize homework_status values
            if 'homework_status' in self.students_df.columns:
                # Map variations to standard values
                status_map = {
                    'pending': 'not_submitted',
                    'not submitted': 'not_submitted',
                    'submitted': 'submitted'
                }
                self.students_df['homework_status'] = self.students_df['homework_status'].str.lower().map(
                    lambda x: status_map.get(x, x)
                )
            
            print(f"✅ Loaded {len(self.students_df)} student records")
            return self.students_df
        
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ Students file not found at {self.students_path}")
        except Exception as e:
            raise Exception(f"❌ Error loading students: {str(e)}")
    
    def load_admins(self) -> List[Dict]:
        """Load admins from JSON file"""
        try:
            with open(self.admins_path, 'r', encoding='utf-8') as f:
                admins = json.load(f)
            
            # Data is a direct list
            if not isinstance(admins, list):
                raise ValueError("admins.json should be a JSON array")
            
            self.admins = admins
            print(f"✅ Loaded {len(self.admins)} admin profiles")
            return self.admins
        
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ Admins file not found at {self.admins_path}")
        except Exception as e:
            raise Exception(f"❌ Error loading admins: {str(e)}")
    
    def get_admin_by_id(self, admin_id: str) -> Optional[Dict]:
        """Get admin profile by ID"""
        if self.admins is None:
            self.load_admins()
        
        for admin in self.admins:
            if admin.get('admin_id') == admin_id:
                return admin
        return None
    
    def get_student_columns(self) -> List[str]:
        """Get list of available columns in student data"""
        if self.students_df is None:
            self.load_students()
        return list(self.students_df.columns)
    
    def get_data_summary(self) -> Dict:
        """Get summary statistics of the data"""
        if self.students_df is None:
            self.load_students()
        
        return {
            "total_students": len(self.students_df),
            "grades": sorted(self.students_df['grade'].unique().tolist()),
            "classes": sorted(self.students_df['class'].unique().tolist()),
            "regions": sorted(self.students_df['region'].unique().tolist()),
            "homework_submitted": len(self.students_df[self.students_df['homework_status'] == 'submitted']),
            "homework_pending": len(self.students_df[self.students_df['homework_status'] == 'not_submitted']),
            "avg_quiz_score": round(self.students_df['quiz_score'].mean(), 2)
        }