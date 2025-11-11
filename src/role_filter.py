import pandas as pd
from typing import Dict, Optional

class RoleFilter:
    """Apply role-based access control to data"""
    
    @staticmethod
    def filter_by_admin_scope(df: pd.DataFrame, admin: Dict) -> pd.DataFrame:
        """
        Filter DataFrame based on admin's assigned scope
        Admin can only see data for their assigned grade/class/region
        """
        if df is None or len(df) == 0:
            return df
            
        filtered_df = df.copy()
        
        # Filter by grade if admin has assigned grade
        if 'assigned_grade' in admin and admin['assigned_grade'] is not None:
            filtered_df = filtered_df[filtered_df['grade'] == admin['assigned_grade']]
        
        # Filter by class if admin has assigned class
        if 'assigned_class' in admin and admin['assigned_class'] is not None:
            filtered_df = filtered_df[filtered_df['class'] == admin['assigned_class']]
        
        # Filter by region if admin has assigned region
        if 'region' in admin and admin['region'] is not None:
            if 'region' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['region'] == admin['region']]
        
        return filtered_df
    
    @staticmethod
    def get_admin_scope_description(admin: Dict) -> str:
        """Get human-readable description of admin's access scope"""
        scope_parts = []
        
        if admin.get('assigned_grade'):
            scope_parts.append(f"Grade {admin['assigned_grade']}")
        
        if admin.get('assigned_class'):
            scope_parts.append(f"Class {admin['assigned_class']}")
        
        if admin.get('region'):
            scope_parts.append(f"{admin['region']} Region")
        
        return " • ".join(scope_parts) if scope_parts else "All data"
    
    @staticmethod
    def validate_access(admin: Dict, requested_grade: Optional[int] = None, 
                       requested_class: Optional[str] = None) -> tuple[bool, str]:
        """
        Validate if admin has access to requested data
        Returns (is_valid, error_message)
        """
        # If admin has assigned grade and user requests different grade
        if admin.get('assigned_grade') and requested_grade:
            if admin['assigned_grade'] != requested_grade:
                return False, f"❌ Access Denied: You can only access Grade {admin['assigned_grade']} data"
        
        # If admin has assigned class and user requests different class
        if admin.get('assigned_class') and requested_class:
            if admin['assigned_class'] != requested_class:
                return False, f"❌ Access Denied: You can only access Class {admin['assigned_class']} data"
        
        return True, ""
    
    @staticmethod
    def get_scope_stats(df: pd.DataFrame, admin: Dict) -> Dict:
        """Get statistics about admin's accessible data"""
        filtered = RoleFilter.filter_by_admin_scope(df, admin)
        
        if len(filtered) == 0:
            return {
                "total_students": 0,
                "homework_submitted": 0,
                "homework_pending": 0,
                "avg_score": 0
            }
        
        return {
            "total_students": len(filtered),
            "homework_submitted": len(filtered[filtered['homework_status'] == 'submitted']),
            "homework_pending": len(filtered[filtered['homework_status'] == 'not_submitted']),
            "avg_score": round(filtered['quiz_score'].mean(), 2),
            "highest_score": filtered['quiz_score'].max(),
            "lowest_score": filtered['quiz_score'].min()
        }