from ..base_workflow import BaseWorkflow

class MeetingSummarizer(BaseWorkflow):
    def run(self, input_data: str) -> dict:
        # returns lightweight meeting notes
        lines = [l.strip() for l in input_data.split('\n') if l.strip()]
        return {"highlights": lines[:3], "num_lines": len(lines)}
