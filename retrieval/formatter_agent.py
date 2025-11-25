"""
Formatter Agent for Session 11
Formats final answers from globals_schema.
"""

from typing import Dict, Any, Optional


class FormatterAgent:
    """Agent for formatting final reports and answers."""
    
    def format_report(self, findings: Dict[str, Any], instruction: Optional[str] = None) -> str:
        """
        Format final answer from globals_schema.
        
        Args:
            findings: Dictionary with findings/globals_schema
            instruction: Optional instruction for summarization
        
        Returns:
            Formatted answer string
        """
        if instruction:
            # Use instruction if provided
            return self._format_with_instruction(findings, instruction)
        
        # Default formatting
        if "last_result" in findings:
            return str(findings["last_result"])
        
        if "final_answer" in findings:
            return str(findings["final_answer"])
        
        # Fallback: format all available data
        formatted_parts = []
        for key, value in findings.items():
            if key not in ["last_node", "last_result"]:
                formatted_parts.append(f"{key}: {value}")
        
        if formatted_parts:
            return "\n".join(formatted_parts)
        
        return "No answer available"
    
    def _format_with_instruction(self, findings: Dict[str, Any], instruction: str) -> str:
        """Format with specific instruction."""
        # Extract relevant data based on instruction
        if "concise" in instruction.lower():
            if "last_result" in findings:
                return str(findings["last_result"])
        
        if "summary" in instruction.lower():
            summary_parts = []
            for key, value in findings.items():
                if isinstance(value, (str, int, float)):
                    summary_parts.append(f"{key}: {value}")
            return "\n".join(summary_parts)
        
        # Default: use instruction as template
        result = instruction
        for key, value in findings.items():
            result = result.replace(f"{{{key}}}", str(value))
        
        return result

