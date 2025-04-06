from fastapi import HTTPException, APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any
from pathlib import Path
from .main import save_report_to_text, format_report_for_display
from .langraph_workflow import employee_analysis_graph

router = APIRouter()

# Create reports directory in parent folder
REPORTS_DIR = Path(__file__).parent.parent / "emp_reports"
REPORTS_DIR.mkdir(exist_ok=True)


class EmployeeDataRequest(BaseModel):
    employee_data: Dict[str, Any]
    chain_id: str


@router.post("/analyze")
async def analyze_employee_data(request: EmployeeDataRequest):
    """
    Analyze employee data and generate a report.
    """
    try:
        # Get employee ID from the request
        emp_id = request.employee_data.get("employee_id")
        if not emp_id:
            raise HTTPException(
                status_code=400, detail="Employee ID is required in the request data"
            )
        
        chain_id = request.chain_id
        if not chain_id:
            raise HTTPException(
                status_code=400, detail="Chain ID is required in the request data"
            )

        # Initialize the state
        initial_state = {"employee_data": request.employee_data, "chain_id": chain_id, "status": "started"}

        print("Starting employee analysis...", initial_state)

        # Run the analysis
        result = employee_analysis_graph.invoke(initial_state)

        print("Analysis complete.")

        # Extract the consolidated report
        consolidated_report = result.get("consolidated_report", {})

        if not consolidated_report:
            raise HTTPException(
                status_code=500, detail="No consolidated report generated"
            )

        # Generate report filename using employee ID
        report_filename = f"{chain_id}_report.txt"
        report_path = REPORTS_DIR / report_filename

        # Save the report
        save_report_to_text(consolidated_report, str(report_path))

        return {
            "summary": format_report_for_display(result),
            "report_path": str(report_path),
            "message": f"Report generated successfully for employee {emp_id}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download-report/{chain_id}")
async def download_report(chain_id: str):
    """
    Download the generated report file for a specific employee.
    """
    try:
        report_path = REPORTS_DIR / f"{chain_id}_report.txt"
        if report_path.exists():
            return FileResponse(
                str(report_path),
                media_type="text/plain",
                filename=f"{chain_id}_report.txt",
            )
        else:
            raise HTTPException(
                status_code=404, detail=f"Report not found with chain_id {chain_id}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list-reports")
async def list_reports():
    """
    List all available reports.
    """
    try:
        reports = []
        for report_file in REPORTS_DIR.glob("*_report.txt"):
            chain_id = report_file.stem.replace("_report", "")
            reports.append(
                {
                    "chain_id": chain_id,
                    "report_path": str(report_file),
                    "created_at": report_file.stat().st_ctime,
                }
            )
        return {"reports": reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report-exists/{chain_id}")
async def report_exists(chain_id: str):
    """
    Get the report for a specific chain ID.
    """

    report_path = REPORTS_DIR / f"{chain_id}_report.txt"
    if report_path.exists():
        return {"exists": True}
    else:
        return {"exists": False}
