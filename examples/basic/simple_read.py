"""
Simple READ Example

Shows how to find objects with minimal code.
"""

from sqlalchemy import Column, String
from andamios_orm import SimpleModel, save, find_by_id, find_all, create_tables

# Define a simple model
class Project(SimpleModel):
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"Project(id={self.id}, name='{self.name}')"

# Setup and create some data
create_tables()

# Create a few projects
project1 = Project(name="WebApp")
project2 = Project(name="MobileApp")
save(project1)
save(project2)

# READ by ID - Ultra simple!
found = find_by_id(Project, project1.id)
print(f"Found by ID: {found}")

# READ all - Ultra simple!
all_projects = find_all(Project)
print(f"All projects: {all_projects}")