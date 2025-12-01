"""
Evaluation script for testing RAG pipeline quality

This script runs predefined test queries and evaluates the system's responses
"""

import asyncio
from typing import List, Dict, Any
from retriever import rag_retriever
from structured_extractor import structured_extractor
from datetime import datetime
import json


class RAGEvaluator:
    """Evaluate RAG pipeline with test queries"""
    
    def __init__(self):
        self.test_queries = [
            {
                'id': 1,
                'query': 'What is the fire rating for corridor partitions?',
                'expected_keywords': ['fire', 'rating', 'corridor', 'partition', 'hour', 'hr'],
                'category': 'specifications'
            },
            {
                'id': 2,
                'query': 'What flooring material is specified for the lobby?',
                'expected_keywords': ['floor', 'lobby', 'material', 'finish'],
                'category': 'specifications'
            },
            {
                'id': 3,
                'query': 'Are there accessibility requirements for doors?',
                'expected_keywords': ['accessibility', 'door', 'ada', 'requirement'],
                'category': 'compliance'
            },
            {
                'id': 4,
                'query': 'What are the typical door dimensions in the project?',
                'expected_keywords': ['door', 'dimension', 'size', 'width', 'height'],
                'category': 'dimensions'
            },
            {
                'id': 5,
                'query': 'Generate a door schedule',
                'expected_keywords': ['door', 'schedule', 'mark', 'type'],
                'category': 'structured_extraction'
            },
            {
                'id': 6,
                'query': 'What is the specified door hardware?',
                'expected_keywords': ['door', 'hardware', 'lock', 'hinge'],
                'category': 'specifications'
            },
            {
                'id': 7,
                'query': 'What are the wage rates for carpenters?',
                'expected_keywords': ['wage', 'carpenter', 'rate', 'hour'],
                'category': 'wages'
            },
            {
                'id': 8,
                'query': 'List all door types mentioned in the drawings',
                'expected_keywords': ['door', 'type', 'drawing'],
                'category': 'drawings'
            },
        ]
        
        self.results = []
    
    def evaluate_response(self, query_info: Dict[str, Any], answer: str, sources: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate a single response
        
        Returns evaluation result dictionary
        """
        answer_lower = answer.lower()
        
        # Check if expected keywords are in the answer
        keywords_found = sum(1 for keyword in query_info['expected_keywords'] 
                           if keyword.lower() in answer_lower)
        keyword_score = keywords_found / len(query_info['expected_keywords'])
        
        # Check if sources are provided
        has_sources = len(sources) > 0
        
        # Check for hallucination indicators
        hallucination_flags = [
            "i don't know",
            "not found",
            "no information",
            "cannot find",
            "don't have"
        ]
        admits_uncertainty = any(flag in answer_lower for flag in hallucination_flags)
        
        # Simple quality assessment
        if keyword_score > 0.5 and has_sources:
            quality = "good"
        elif keyword_score > 0.3 or has_sources:
            quality = "partial"
        elif admits_uncertainty:
            quality = "honest_unknown"
        else:
            quality = "poor"
        
        return {
            'query_id': query_info['id'],
            'query': query_info['query'],
            'category': query_info['category'],
            'answer': answer[:300] + "..." if len(answer) > 300 else answer,
            'sources_count': len(sources),
            'keyword_score': keyword_score,
            'quality': quality,
            'has_sources': has_sources,
            'admits_uncertainty': admits_uncertainty
        }
    
    async def run_evaluation(self):
        """Run evaluation on all test queries"""
        print("=" * 80)
        print("RAG PIPELINE EVALUATION")
        print("=" * 80)
        print(f"Starting evaluation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total test queries: {len(self.test_queries)}\n")
        
        for i, query_info in enumerate(self.test_queries, 1):
            print(f"\n[{i}/{len(self.test_queries)}] Testing query: {query_info['query']}")
            print("-" * 80)
            
            try:
                # Check if it's a structured extraction query
                is_extraction, extraction_type = rag_retriever.detect_extraction_intent(
                    query_info['query']
                )
                
                if is_extraction and extraction_type == 'door_schedule':
                    # Test structured extraction
                    extracted_data, sources = structured_extractor.extract_door_schedule()
                    answer = f"Extracted {len(extracted_data)} door entries"
                    
                    print(f"  Extraction type: {extraction_type}")
                    print(f"  Extracted items: {len(extracted_data)}")
                    
                else:
                    # Test regular Q&A
                    answer, sources = rag_retriever.answer_question(query_info['query'])
                    
                    print(f"  Answer preview: {answer[:150]}...")
                
                print(f"  Sources found: {len(sources)}")
                
                # Evaluate response
                result = self.evaluate_response(query_info, answer, sources)
                self.results.append(result)
                
                print(f"  Quality: {result['quality']}")
                print(f"  Keyword score: {result['keyword_score']:.2f}")
                
            except Exception as e:
                print(f"  ERROR: {str(e)}")
                self.results.append({
                    'query_id': query_info['id'],
                    'query': query_info['query'],
                    'category': query_info['category'],
                    'error': str(e),
                    'quality': 'error'
                })
        
        # Print summary
        self._print_summary()
        
        # Save results to file
        self._save_results()
    
    def _print_summary(self):
        """Print evaluation summary"""
        print("\n" + "=" * 80)
        print("EVALUATION SUMMARY")
        print("=" * 80)
        
        total = len(self.results)
        quality_counts = {}
        
        for result in self.results:
            quality = result.get('quality', 'error')
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        print(f"\nTotal queries evaluated: {total}")
        print("\nQuality breakdown:")
        for quality, count in sorted(quality_counts.items()):
            percentage = (count / total) * 100
            print(f"  {quality:20s}: {count:2d} ({percentage:5.1f}%)")
        
        # Calculate average keyword score
        avg_keyword_score = sum(r.get('keyword_score', 0) for r in self.results if 'keyword_score' in r) / total
        print(f"\nAverage keyword score: {avg_keyword_score:.2f}")
        
        # Sources statistics
        queries_with_sources = sum(1 for r in self.results if r.get('has_sources', False))
        print(f"Queries with sources: {queries_with_sources}/{total} ({queries_with_sources/total*100:.1f}%)")
    
    def _save_results(self):
        """Save results to JSON file"""
        output_file = "evaluation_results.json"
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'total_queries': len(self.results),
            'results': self.results,
            'summary': {
                'quality_breakdown': {},
                'avg_keyword_score': sum(r.get('keyword_score', 0) for r in self.results) / len(self.results),
                'queries_with_sources': sum(1 for r in self.results if r.get('has_sources', False))
            }
        }
        
        for result in self.results:
            quality = result.get('quality', 'error')
            output['summary']['quality_breakdown'][quality] = \
                output['summary']['quality_breakdown'].get(quality, 0) + 1
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")


async def main():
    """Main evaluation function"""
    evaluator = RAGEvaluator()
    await evaluator.run_evaluation()


if __name__ == "__main__":
    asyncio.run(main())
