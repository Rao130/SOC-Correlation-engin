"""
SOAR (Security Orchestration, Automation and Response) API Routes
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.soar_engine import soar_engine
from app.core.auth import get_current_user
from app.core.logging import logger

router = APIRouter()

# Pydantic models
class PlaybookTrigger(BaseModel):
    playbook_id: str = Field(..., description="ID of the playbook to trigger")
    trigger_data: Dict[str, Any] = Field(..., description="Trigger data for the playbook")

class PlaybookRegistration(BaseModel):
    id: str = Field(..., description="Unique playbook ID")
    name: str = Field(..., description="Playbook name")
    description: str = Field(..., description="Playbook description")
    triggers: List[str] = Field(..., description="Trigger events")
    actions: List[Dict[str, Any]] = Field(..., description="Playbook actions")

class CustomAction(BaseModel):
    name: str = Field(..., description="Action name")
    action_type: str = Field(..., description="Action type")
    parameters: Dict[str, Any] = Field(..., description="Action parameters")
    dependencies: List[str] = Field(default_factory=list, description="Action dependencies")

@router.get("/playbooks")
async def list_playbooks(current_user: dict = Depends(get_current_user)):
    """List all available playbooks"""
    try:
        playbooks = soar_engine.list_playbooks()
        return {
            "status": "success",
            "playbooks": playbooks,
            "total": len(playbooks)
        }
    except Exception as e:
        logger.error(f"Error listing playbooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/playbooks/{playbook_id}")
async def get_playbook(playbook_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific playbook details"""
    try:
        if playbook_id not in soar_engine.playbooks:
            raise HTTPException(status_code=404, detail="Playbook not found")
        
        playbook = soar_engine.playbooks[playbook_id]
        return {
            "status": "success",
            "playbook": playbook
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting playbook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/playbooks/register")
async def register_playbook(
    playbook: PlaybookRegistration,
    current_user: dict = Depends(get_current_user)
):
    """Register a new playbook"""
    try:
        playbook_config = {
            'name': playbook.name,
            'description': playbook.description,
            'triggers': playbook.triggers,
            'actions': playbook.actions
        }
        
        soar_engine.register_playbook(playbook.id, playbook_config)
        
        return {
            "status": "success",
            "message": f"Playbook '{playbook.id}' registered successfully",
            "playbook_id": playbook.id
        }
    except Exception as e:
        logger.error(f"Error registering playbook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/playbooks/trigger")
async def trigger_playbook(
    trigger: PlaybookTrigger,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Trigger a playbook execution"""
    try:
        execution_id = soar_engine.trigger_playbook(
            trigger.playbook_id,
            trigger.trigger_data
        )
        
        return {
            "status": "success",
            "message": f"Playbook '{trigger.playbook_id}' triggered successfully",
            "execution_id": execution_id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering playbook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions")
async def list_executions(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """List recent playbook executions"""
    try:
        executions = soar_engine.get_executions(limit=limit)
        return {
            "status": "success",
            "executions": executions,
            "total": len(executions)
        }
    except Exception as e:
        logger.error(f"Error listing executions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions/{execution_id}")
async def get_execution_status(
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific execution status"""
    try:
        execution = soar_engine.get_execution_status(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return {
            "status": "success",
            "execution": execution
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/executions/{execution_id}/pause")
async def pause_execution(
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Pause a running execution"""
    try:
        execution = soar_engine.executions.get(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        if execution.status.value != "running":
            raise HTTPException(status_code=400, detail="Execution is not running")
        
        execution.status = soar_engine.PlaybookStatus.PAUSED
        
        return {
            "status": "success",
            "message": f"Execution '{execution_id}' paused successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/executions/{execution_id}/resume")
async def resume_execution(
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Resume a paused execution"""
    try:
        execution = soar_engine.executions.get(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        if execution.status.value != "paused":
            raise HTTPException(status_code=400, detail="Execution is not paused")
        
        execution.status = soar_engine.PlaybookStatus.RUNNING
        
        # Resume execution asynchronously
        import asyncio
        asyncio.create_task(soar_engine._execute_playbook(execution_id))
        
        return {
            "status": "success",
            "message": f"Execution '{execution_id}' resumed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/executions/{execution_id}")
async def cancel_execution(
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel an execution"""
    try:
        execution = soar_engine.executions.get(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        if execution.status.value in ["completed", "failed"]:
            raise HTTPException(status_code=400, detail="Cannot cancel completed execution")
        
        execution.status = soar_engine.PlaybookStatus.FAILED
        execution.end_time = datetime.now()
        
        return {
            "status": "success",
            "message": f"Execution '{execution_id}' cancelled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/actions/types")
async def list_action_types(current_user: dict = Depends(get_current_user)):
    """List available action types"""
    try:
        action_types = list(soar_engine.action_handlers.keys())
        return {
            "status": "success",
            "action_types": action_types,
            "total": len(action_types)
        }
    except Exception as e:
        logger.error(f"Error listing action types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_soar_stats(current_user: dict = Depends(get_current_user)):
    """Get SOAR engine statistics"""
    try:
        total_playbooks = len(soar_engine.playbooks)
        total_executions = len(soar_engine.executions)
        
        # Calculate execution statistics
        executions_by_status = {}
        for execution in soar_engine.executions.values():
            status = execution.status.value
            executions_by_status[status] = executions_by_status.get(status, 0) + 1
        
        # Calculate playbook usage
        playbook_usage = {}
        for execution in soar_engine.executions.values():
            playbook_id = execution.playbook_id
            playbook_usage[playbook_id] = playbook_usage.get(playbook_id, 0) + 1
        
        return {
            "status": "success",
            "stats": {
                "total_playbooks": total_playbooks,
                "total_executions": total_executions,
                "executions_by_status": executions_by_status,
                "playbook_usage": playbook_usage,
                "available_actions": len(soar_engine.action_handlers)
            }
        }
    except Exception as e:
        logger.error(f"Error getting SOAR stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-action")
async def test_action(
    action_type: str,
    parameters: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Test an action without executing a full playbook"""
    try:
        if action_type not in soar_engine.action_handlers:
            raise HTTPException(status_code=404, detail="Action type not found")
        
        # Create a test execution and action
        from app.services.soar_engine import PlaybookExecution, PlaybookAction
        test_execution = PlaybookExecution(
            id="test",
            playbook_id="test",
            trigger_data={}
        )
        
        test_action = PlaybookAction(
            id="test_action",
            name="Test Action",
            action_type=action_type,
            parameters=parameters
        )
        
        # Execute the action
        import asyncio
        result = await soar_engine._execute_action(test_execution, test_action)
        
        return {
            "status": "success",
            "action_type": action_type,
            "parameters": parameters,
            "result": test_action.result,
            "execution_time": test_action.execution_time
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Auto-trigger endpoint for integration with other systems
@router.post("/auto-trigger")
async def auto_trigger(
    event_type: str,
    event_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Automatically trigger playbooks based on event type"""
    try:
        triggered_playbooks = []
        
        # Find playbooks that match the event type
        for playbook_id, playbook in soar_engine.playbooks.items():
            if event_type in playbook.get('triggers', []):
                try:
                    execution_id = soar_engine.trigger_playbook(playbook_id, event_data)
                    triggered_playbooks.append({
                        'playbook_id': playbook_id,
                        'execution_id': execution_id
                    })
                except Exception as e:
                    logger.error(f"Error auto-triggering playbook {playbook_id}: {e}")
        
        return {
            "status": "success",
            "event_type": event_type,
            "triggered_playbooks": triggered_playbooks,
            "total_triggered": len(triggered_playbooks)
        }
    except Exception as e:
        logger.error(f"Error in auto-trigger: {e}")
        raise HTTPException(status_code=500, detail=str(e))
