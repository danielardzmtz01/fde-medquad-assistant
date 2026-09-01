# src/backend/app/tools/mock_trials_tool.py
"""Clinical trials and supplementary literature tool."""

from typing import Dict, Any, List


class ClinicalTrialsTool:
    """Provides supplementary metadata regarding ongoing NIH and NCI clinical trials."""

    def __init__(self):
        self.trials_db = {
            "hodgkin": [
                {
                    "nct_id": "NCT03907488",
                    "title": "Nivolumab and AVD in Treating Patients With Newly Diagnosed Stage II-IV Classical Hodgkin Lymphoma",
                    "phase": "Phase 3",
                    "status": "Active, not recruiting",
                    "sponsor": "National Cancer Institute (NCI)",
                }
            ]
        }

    async def get_active_trials(self, condition: str) -> List[Dict[str, Any]]:
        """Queries mock clinical trial database for matching condition."""
        for key, trials in self.trials_db.items():
            if key in condition.lower():
                return trials
        return []


trials_tool = ClinicalTrialsTool()
