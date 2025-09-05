from ..base_workflow import BaseWorkflow

class MeetingSummarizer(BaseWorkflow):
    def run(self, input_data: str) -> dict:
        # returns lightweight meeting notes
        lines = [line.strip() for line in input_data.split('\n') if line.strip()]
        return {"highlights": lines[:3], "num_lines": len(lines)}
