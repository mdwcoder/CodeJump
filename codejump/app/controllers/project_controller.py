from __future__ import annotations

from codejump.core.models import Project
from codejump.storage.projects_store import ProjectsStore


class ProjectController:
    def __init__(self, store: ProjectsStore) -> None:
        self.store = store
        self.projects = self.store.load()
        self.active_project_id: str | None = None

    def persist(self) -> None:
        self.store.save(self.projects)

    def set_active(self, project_id: str | None) -> Project | None:
        self.active_project_id = project_id
        return self.get_active_project()

    def get_active_project(self) -> Project | None:
        for project in self.projects:
            if project.id == self.active_project_id:
                return project
        return None

    def upsert(self, project: Project) -> Project:
        for index, current in enumerate(self.projects):
            if current.id == project.id:
                self.projects[index] = project
                self.persist()
                return project
        self.projects.append(project)
        self.projects.sort(key=lambda item: item.name.lower())
        self.persist()
        return project

    def delete(self, project_id: str) -> Project | None:
        self.projects = [project for project in self.projects if project.id != project_id]
        if self.active_project_id == project_id:
            self.active_project_id = self.projects[0].id if self.projects else None
        self.persist()
        return self.get_active_project()

