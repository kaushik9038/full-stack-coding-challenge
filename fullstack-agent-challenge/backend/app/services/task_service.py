"""Service layer for task creation and retrieval."""

import json
from typing import Optional

from sqlalchemy.orm import Session

from app.agent.controller import TaskController, TaskRejectedError
from app.db.models import TaskRecord
from app.db.schemas import TaskResponse


class TaskService:
    def __init__(self, db: Session, controller: Optional[TaskController] = None) -> None:
        self.db = db
        self.controller = controller or TaskController()

    def create_task(self, task_text: str) -> TaskResponse:
        try:
            task_result = self.controller.run_task(task_text)
        except TaskRejectedError as exc:
            record = TaskRecord(
                task=task_text,
                final_output=str(exc),
                selected_tool=exc.selected_tool,
                tools_used_json=json.dumps(exc.tools_used),
                execution_steps_json=json.dumps(exc.execution_steps),
            )
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            raise

        record = TaskRecord(
            task=task_result["task"],
            final_output=task_result["final_output"],
            selected_tool=task_result["selected_tool"],
            tools_used_json=json.dumps(task_result["tools_used"]),
            execution_steps_json=json.dumps([step.model_dump() for step in task_result["execution_steps"]]),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return self._to_response(record)

    def list_tasks(self) -> list[TaskResponse]:
        # History reads newest-first in the sidebar.
        records = self.db.query(TaskRecord).order_by(TaskRecord.id.desc()).all()
        return [self._to_response(record) for record in records]

    def get_task(self, task_id: int) -> Optional[TaskResponse]:
        record = self.db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
        return self._to_response(record) if record else None

    def _to_response(self, record: TaskRecord) -> TaskResponse:
        return TaskResponse(
            id=record.id,
            task=record.task,
            final_output=record.final_output,
            selected_tool=record.selected_tool,
            tools_used=json.loads(record.tools_used_json),
            execution_steps=json.loads(record.execution_steps_json),
            timestamp=record.created_at,
        )
