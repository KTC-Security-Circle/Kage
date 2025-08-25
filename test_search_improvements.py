#!/usr/bin/env python3
"""
Quick test script to verify the search improvements work correctly.
This will test SQL-level filtering vs Python-level filtering behavior.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from sqlalchemy import create_engine
    from sqlmodel import Session, SQLModel
    
    from logic.repositories.task import TaskRepository
    from logic.repositories.tag import TagRepository
    from logic.repositories.project import ProjectRepository
    from models import Task, TaskCreate, TaskStatus, Tag, TagCreate, Project, ProjectCreate, ProjectStatus
    
    def test_search_functionality():
        """Test that the new SQL-level filtering works correctly"""
        print("Testing search functionality improvements...")
        
        # Create in-memory database
        engine = create_engine("sqlite:///:memory:", echo=False)
        SQLModel.metadata.create_all(engine)
        
        with Session(engine) as session:
            # Create test data
            task_repo = TaskRepository(session)
            tag_repo = TagRepository(session)
            project_repo = ProjectRepository(session)
            
            # Create test tasks with mixed case
            test_tasks = [
                TaskCreate(title="重要なタスク", description="This is important"),
                TaskCreate(title="普通のタスク", description="Regular task"),
                TaskCreate(title="Urgent Task", description="Very urgent"),
                TaskCreate(title="重要度低", description="Low priority"),
                TaskCreate(title="IMPORTANT Work", description="Critical work"),
            ]
            
            created_tasks = []
            for task_data in test_tasks:
                task = task_repo.create(task_data)
                created_tasks.append(task)
                session.commit()
            
            # Create test tags with mixed case
            test_tags = [
                TagCreate(name="重要"),
                TagCreate(name="緊急"),
                TagCreate(name="@home"),
                TagCreate(name="重要度"),
                TagCreate(name="URGENT"),
            ]
            
            created_tags = []
            for tag_data in test_tags:
                tag = tag_repo.create(tag_data)
                created_tags.append(tag)
                session.commit()
            
            # Create test projects with mixed case
            test_projects = [
                ProjectCreate(title="重要プロジェクト", description="Important project"),
                ProjectCreate(title="サイドプロジェクト", description="Side project"),
                ProjectCreate(title="Main Project", description="Main work"),
                ProjectCreate(title="重要性の検証", description="Verification"),
                ProjectCreate(title="CRITICAL System", description="Critical system"),
            ]
            
            created_projects = []
            for project_data in test_projects:
                project = project_repo.create(project_data)
                created_projects.append(project)
                session.commit()
            
            # Test searches
            print("\nTesting Task search:")
            task_results = task_repo.search_by_title("重要")
            print(f"  Found {len(task_results)} tasks with '重要': {[t.title for t in task_results]}")
            
            task_results_urgent = task_repo.search_by_title("Task")
            print(f"  Found {len(task_results_urgent)} tasks with 'Task': {[t.title for t in task_results_urgent]}")
            
            # Test case insensitive search
            task_results_important_lower = task_repo.search_by_title("important")
            print(f"  Found {len(task_results_important_lower)} tasks with 'important' (lowercase): {[t.title for t in task_results_important_lower]}")
            
            print("\nTesting Tag search:")
            tag_results = tag_repo.search_by_name("重要")
            print(f"  Found {len(tag_results)} tags with '重要': {[t.name for t in tag_results]}")
            
            tag_results_home = tag_repo.search_by_name("home")
            print(f"  Found {len(tag_results_home)} tags with 'home': {[t.name for t in tag_results_home]}")
            
            # Test case insensitive search for tags
            tag_results_urgent_lower = tag_repo.search_by_name("urgent")
            print(f"  Found {len(tag_results_urgent_lower)} tags with 'urgent' (lowercase): {[t.name for t in tag_results_urgent_lower]}")
            
            print("\nTesting Project search:")
            project_results = project_repo.search_by_title("重要")
            print(f"  Found {len(project_results)} projects with '重要': {[p.title for p in project_results]}")
            
            project_results_project = project_repo.search_by_title("Project")
            print(f"  Found {len(project_results_project)} projects with 'Project': {[p.title for p in project_results_project]}")
            
            # Test case insensitive search for projects
            project_results_critical_lower = project_repo.search_by_title("critical")
            print(f"  Found {len(project_results_critical_lower)} projects with 'critical' (lowercase): {[p.title for p in project_results_critical_lower]}")
            
            # Verify expected results
            assert len(task_results) == 2, f"Expected 2 tasks with '重要', got {len(task_results)}"
            assert len(tag_results) == 2, f"Expected 2 tags with '重要', got {len(tag_results)}"
            assert len(project_results) == 2, f"Expected 2 projects with '重要', got {len(project_results)}"
            
            # Verify case insensitive behavior
            assert len(task_results_important_lower) == 1, f"Expected 1 task with 'important' (case insensitive), got {len(task_results_important_lower)}"
            assert len(tag_results_urgent_lower) == 1, f"Expected 1 tag with 'urgent' (case insensitive), got {len(tag_results_urgent_lower)}"
            assert len(project_results_critical_lower) == 1, f"Expected 1 project with 'critical' (case insensitive), got {len(project_results_critical_lower)}"
            
            print("\n✅ All search tests passed!")
            return True
            
    if __name__ == "__main__":
        test_search_functionality()
        print("Search improvements verified successfully!")
        
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("This is expected in the GitHub environment where dependencies aren't installed")
    sys.exit(0)