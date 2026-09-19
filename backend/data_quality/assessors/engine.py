"""
Quality assessment engine that coordinates all assessors.
"""

import logging
from typing import Any, Dict, List, Optional

from backend.data_quality.assessors.base import AssessmentResult
from backend.data_quality.assessors.consistency import ConsistencyAssessor
from backend.data_quality.assessors.agreement import AgreementAssessor
from backend.data_quality.assessors.outlier import OutlierAssessor
from backend.data_quality.assessors.bias import BiasAssessor
from backend.data_quality.assessors.completeness import CompletenessAssessor
from backend.data_quality.models import (
    QualityReport,
    QualityIssue,
    ReportType,
    SeverityLevel,
)

logger = logging.getLogger(__name__)

# Registry of available assessors
ASSESSOR_REGISTRY = {
    "consistency": ConsistencyAssessor,
    "agreement": AgreementAssessor,
    "outlier": OutlierAssessor,
    "bias": BiasAssessor,
    "completeness": CompletenessAssessor,
}


class QualityAssessmentEngine:
    """
    Engine for running quality assessments.

    Coordinates multiple assessors and generates consolidated reports.
    """

    def __init__(self, project_id: int):
        """
        Initialize engine.

        Args:
            project_id: Project ID
        """
        self.project_id = project_id
        self.results: Dict[str, AssessmentResult] = {}

    def get_assessor(self, name: str) -> Any:
        """
        Get assessor instance by name.

        Args:
            name: Assessor name

        Returns:
            Assessor instance
        """
        if name not in ASSESSOR_REGISTRY:
            raise ValueError(
                f"Unknown assessor: {name}. "
                f"Available: {list(ASSESSOR_REGISTRY.keys())}"
            )

        return ASSESSOR_REGISTRY[name](self.project_id)

    def run_assessment(
        self,
        tasks: List[Dict[str, Any]],
        annotations: List[Dict[str, Any]],
        assessors: Optional[List[str]] = None,
        include_details: bool = True,
        user_id: Optional[int] = None,
    ) -> QualityReport:
        """
        Run quality assessment.

        Args:
            tasks: List of task data
            annotations: List of annotation data
            assessors: List of assessor names to run (None for all)
            include_details: Whether to include detailed statistics
            user_id: User running the assessment

        Returns:
            QualityReport instance
        """
        # Determine which assessors to run
        if assessors is None:
            assessors = list(ASSESSOR_REGISTRY.keys())

        # Run each assessor
        all_issues = []
        all_statistics = {}
        scores = []

        for assessor_name in assessors:
            try:
                assessor = self.get_assessor(assessor_name)
                result = assessor.assess(
                    tasks=tasks,
                    annotations=annotations,
                    include_details=include_details,
                )

                self.results[assessor_name] = result
                all_issues.extend(result.issues)
                all_statistics[assessor_name] = result.statistics
                scores.append(result.score)

                logger.info(
                    f"Assessor {assessor_name} completed: "
                    f"score={result.score:.3f}, issues={len(result.issues)}"
                )

            except Exception as e:
                logger.error(
                    f"Error in assessor {assessor_name}: {str(e)}", exc_info=True
                )
                scores.append(0.0)
                all_statistics[assessor_name] = {"error": str(e)}

        # Compute overall score
        overall_score = sum(scores) / len(scores) if scores else 0.0

        # Count issues by severity
        issue_count = len(all_issues)
        critical_count = sum(1 for i in all_issues if i.severity == "critical")

        # Count unique annotators
        annotator_ids = set(ann.get("annotator_id") for ann in annotations)

        # Create report
        report = QualityReport(
            id=0,  # Would be assigned by database
            project_id=self.project_id,
            report_type=ReportType.PROJECT,
            overall_score=overall_score,
            consistency_score=self.results.get(
                "consistency", AssessmentResult("", 0, {}, [])
            ).score,
            agreement_score=self.results.get(
                "agreement", AssessmentResult("", 0, {}, [])
            ).score,
            completeness_score=self.results.get(
                "completeness", AssessmentResult("", 0, {}, [])
            ).score,
            statistics=all_statistics,
            issue_count=issue_count,
            critical_issue_count=critical_count,
            tasks_analyzed=len(tasks),
            annotations_analyzed=len(annotations),
            annotators_analyzed=len(annotator_ids),
            issues=[
                QualityIssue(
                    id=i,
                    report_id=0,
                    issue_type=issue.issue_type,
                    severity=issue.severity,
                    title=issue.title,
                    description=issue.description,
                    task_id=issue.task_id,
                    annotation_id=issue.annotation_id,
                    annotator_id=issue.annotator_id,
                    details=issue.details,
                )
                for i, issue in enumerate(all_issues)
            ],
            created_by=user_id,
        )

        logger.info(
            f"Quality assessment completed for project {self.project_id}: "
            f"score={overall_score:.3f}, issues={issue_count}, critical={critical_count}"
        )

        return report
