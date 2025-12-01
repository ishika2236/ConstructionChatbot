import json
import re
from typing import List, Dict, Any, Tuple
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from config import settings
from document_processor import document_processor


class StructuredExtractor:
    """Handles structured data extraction from construction documents"""
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            azure_deployment=settings.azure_openai_deployment,
            openai_api_version=settings.azure_openai_api_version,
            temperature=0,  # Low temperature for more deterministic extraction
        )
    
    def extract_door_schedule(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Extract door schedule from construction documents
        
        Returns:
            Tuple of (extracted_data, source_documents)
        """
        # Search for door-related content with higher k for better coverage
        vector_store = document_processor.get_vector_store()
        
        if not vector_store:
            return [], []
        
        # Query for door schedule information
        queries = [
            "door schedule marks types sizes ratings",
            "door specifications hardware fire rating",
            "door dimensions width height material"
        ]
        
        all_docs = []
        seen_content = set()  # Avoid duplicates
        
        for query in queries:
            docs = vector_store.similarity_search(query, k=10)
            for doc in docs:
                content_hash = hash(doc.page_content[:100])  # Hash first 100 chars
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    all_docs.append(doc)
        
        if not all_docs:
            return [], []
        
        # Combine content from retrieved documents
        combined_context = "\n\n".join([
            f"[{doc.metadata.get('source', 'Unknown')}, Page {doc.metadata.get('page', '?')}]\n{doc.page_content}"
            for doc in all_docs[:15]  # Limit to avoid token limits
        ])
        
        # Extraction prompt
        extraction_prompt = f"""You are an expert at extracting structured data from construction documents.

Extract all door information from the following construction documents into a JSON array.
Each door should be an object with these fields (use null if not found):
- mark: Door identifier (e.g., "D-101", "101", "1A")
- location: Where the door is located
- width_mm: Width in millimeters (convert from inches/feet if needed)
- height_mm: Height in millimeters (convert from inches/feet if needed)
- fire_rating: Fire rating (e.g., "1 HR", "90 MIN", "2 HR")
- material: Door material (e.g., "Hollow Metal", "Wood", "Glass")

Documents:
{combined_context}

Important:
- Extract ALL doors mentioned in the documents
- Be precise with measurements and convert units as needed
- If dimensions are in inches, convert to mm (1 inch = 25.4 mm)
- Only include doors that are explicitly mentioned
- Return ONLY a valid JSON array, no other text

JSON Array:"""

        try:
            response = self.llm.invoke(extraction_prompt)
            answer = response.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', answer, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON array directly
                json_match = re.search(r'\[.*\]', answer, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = answer
            
            # Parse JSON
            extracted_data = json.loads(json_str)
            
            # Validate and clean data
            cleaned_data = []
            for item in extracted_data:
                if isinstance(item, dict) and 'mark' in item:
                    cleaned_data.append(item)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response: {answer[:500]}")
            # Fallback: try to extract manually
            cleaned_data = self._manual_door_extraction(combined_context)
        except Exception as e:
            print(f"Extraction error: {e}")
            cleaned_data = []
        
        # Format sources
        sources = [
            {
                'file_name': doc.metadata.get('source', 'Unknown'),
                'page_number': doc.metadata.get('page', None),
                'content_snippet': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            }
            for doc in all_docs[:10]
        ]
        
        return cleaned_data, sources
    
    def _manual_door_extraction(self, text: str) -> List[Dict[str, Any]]:
        """
        Fallback manual extraction using regex patterns
        
        Args:
            text: Text to extract from
            
        Returns:
            List of door dictionaries
        """
        doors = []
        
        # Pattern for door marks like "D-101", "101", "1A"
        mark_pattern = r'\b(?:[D]-?\d+[A-Z]?|\d{3}[A-Z]?)\b'
        
        # Find all potential door marks
        marks = re.findall(mark_pattern, text)
        
        for mark in marks[:20]:  # Limit to first 20 to avoid noise
            # Try to find context around this mark
            context_pattern = rf'{re.escape(mark)}[^\n]{{0,200}}'
            context_match = re.search(context_pattern, text)
            
            if context_match:
                context = context_match.group(0)
                
                door_data = {
                    'mark': mark,
                    'location': None,
                    'width_mm': None,
                    'height_mm': None,
                    'fire_rating': None,
                    'material': None
                }
                
                # Try to extract dimensions (e.g., "36x84", "900x2100")
                dim_match = re.search(r'(\d+)\s*[xX×]\s*(\d+)', context)
                if dim_match:
                    w, h = int(dim_match.group(1)), int(dim_match.group(2))
                    # If values are small, likely inches; convert to mm
                    if w < 100:
                        door_data['width_mm'] = int(w * 25.4)
                        door_data['height_mm'] = int(h * 25.4)
                    else:
                        door_data['width_mm'] = w
                        door_data['height_mm'] = h
                
                # Try to extract fire rating
                rating_match = re.search(r'(\d+)\s*(?:HR|HOUR|MIN)', context, re.IGNORECASE)
                if rating_match:
                    door_data['fire_rating'] = rating_match.group(0).upper()
                
                doors.append(door_data)
        
        return doors
    
    def extract_room_summary(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Extract room summary from construction documents
        
        Returns:
            Tuple of (extracted_data, source_documents)
        """
        vector_store = document_processor.get_vector_store()
        
        if not vector_store:
            return [], []
        
        # Search for room-related content
        docs = vector_store.similarity_search("room schedule area finishes floor", k=10)
        
        if not docs:
            return [], []
        
        combined_context = "\n\n".join([
            f"[{doc.metadata.get('source', 'Unknown')}, Page {doc.metadata.get('page', '?')}]\n{doc.page_content}"
            for doc in docs
        ])
        
        extraction_prompt = f"""Extract all room information from these construction documents into a JSON array.
Each room should have: room_number, room_name, area_sqft, floor_finish, wall_finish, ceiling_finish.

Documents:
{combined_context}

Return ONLY a valid JSON array:"""

        try:
            response = self.llm.invoke(extraction_prompt)
            answer = response.content.strip()
            
            # Extract JSON
            json_match = re.search(r'\[.*\]', answer, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group(0))
            else:
                extracted_data = []
                
        except Exception as e:
            print(f"Room extraction error: {e}")
            extracted_data = []
        
        sources = [
            {
                'file_name': doc.metadata.get('source', 'Unknown'),
                'page_number': doc.metadata.get('page', None),
                'content_snippet': doc.page_content[:200] + "..."
            }
            for doc in docs
        ]
        
        return extracted_data, sources


# Add missing import
from typing import Tuple

# Global instance
structured_extractor = StructuredExtractor()
