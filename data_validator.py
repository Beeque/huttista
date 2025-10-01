#!/usr/bin/env python3
"""
Data Validator and Quality Control
Validates scraped NHL data for consistency and completeness
"""

import json
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self):
        self.required_fields = {
            'player_id': int,
            'full_name': str,
            'nationality': str,
            'overall': int,
            'position': str
        }
        
        self.numeric_fields = [
            'overall', 'aOVR', 'acceleration', 'agility', 'balance', 'endurance', 'speed',
            'slap_shot_accuracy', 'slap_shot_power', 'wrist_shot_accuracy', 'wrist_shot_power',
            'deking', 'off_awareness', 'hand_eye', 'passing', 'puck_control', 'body_checking',
            'strength', 'aggression', 'durability', 'fighting_skill', 'def_awareness',
            'shot_blocking', 'stick_checking', 'faceoffs', 'discipline', 'weight', 'height',
            'salary', 'salary_number', 'weight_kg', 'height_cm'
        ]
        
        self.goalie_numeric_fields = [
            'overall', 'aOVR', 'glove_high', 'glove_low', 'stick_high', 'stick_low',
            'shot_recovery', 'aggression', 'agility', 'speed', 'positioning', 'breakaway',
            'vision', 'poke_check', 'rebound_control', 'passing', 'weight', 'height',
            'salary', 'salary_number', 'weight_kg', 'height_cm'
        ]
        
        self.valid_positions = ['LW', 'RW', 'C', 'D', 'G']
        self.valid_hands = ['LEFT', 'RIGHT']
        self.valid_leagues = ['NHL', 'AHL', 'ECHL', 'KHL', 'SHL', 'Liiga', 'DEL', 'NLA', 'Extraliga']

    def validate_record(self, record: Dict[str, Any], is_goalie: bool = False) -> Dict[str, List[str]]:
        """Validate a single record and return issues found"""
        issues = {
            'missing_fields': [],
            'invalid_types': [],
            'invalid_values': [],
            'data_quality': []
        }
        
        # Check required fields
        for field, expected_type in self.required_fields.items():
            if field not in record:
                issues['missing_fields'].append(f"Missing required field: {field}")
            elif not isinstance(record[field], expected_type):
                issues['invalid_types'].append(f"Field {field} should be {expected_type.__name__}, got {type(record[field]).__name__}")
        
        # Check numeric fields
        numeric_fields = self.goalie_numeric_fields if is_goalie else self.numeric_fields
        for field in numeric_fields:
            if field in record:
                value = record[field]
                if not isinstance(value, (int, float)):
                    issues['invalid_types'].append(f"Field {field} should be numeric, got {type(value).__name__}")
                elif isinstance(value, (int, float)) and (value < 0 or value > 100):
                    if field not in ['salary', 'salary_number', 'weight', 'height', 'weight_kg', 'height_cm']:
                        issues['invalid_values'].append(f"Field {field} value {value} is outside valid range (0-100)")
        
        # Check position validity
        if 'position' in record:
            position = record['position']
            if position not in self.valid_positions:
                issues['invalid_values'].append(f"Invalid position: {position}")
        
        # Check hand validity
        if 'hand' in record:
            hand = record['hand']
            if hand not in self.valid_hands:
                issues['invalid_values'].append(f"Invalid hand: {hand}")
        
        # Check league validity
        if 'league' in record:
            league = record['league']
            if league not in self.valid_leagues:
                issues['data_quality'].append(f"Unknown league: {league}")
        
        # Check data consistency
        if 'weight' in record and 'weight_kg' in record:
            if record['weight'] != record['weight_kg']:
                issues['data_quality'].append("Weight and weight_kg values don't match")
        
        if 'height' in record and 'height_cm' in record:
            if record['height'] != record['height_cm']:
                issues['data_quality'].append("Height and height_cm values don't match")
        
        if 'salary' in record and 'salary_number' in record:
            if record['salary'] != record['salary_number']:
                issues['data_quality'].append("Salary and salary_number values don't match")
        
        return issues

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate a JSON file and return comprehensive report"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {'error': f"File not found: {file_path}"}
        
        logger.info(f"Validating {file_path}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            return {'error': f"Failed to load file: {e}"}
        
        # Handle both direct array and metadata wrapper formats
        if isinstance(data, dict) and 'data' in data:
            records = data['data']
            metadata = data.get('metadata', {})
        else:
            records = data
            metadata = {}
        
        if not isinstance(records, list):
            return {'error': "Data is not a list of records"}
        
        # Validation results
        validation_results = {
            'file_path': str(file_path),
            'total_records': len(records),
            'valid_records': 0,
            'invalid_records': 0,
            'issues_by_type': {
                'missing_fields': 0,
                'invalid_types': 0,
                'invalid_values': 0,
                'data_quality': 0
            },
            'record_issues': [],
            'statistics': {},
            'metadata': metadata
        }
        
        # Validate each record
        for i, record in enumerate(records):
            is_goalie = 'glove_high' in record or 'glove_low' in record
            issues = self.validate_record(record, is_goalie)
            
            has_issues = any(issues.values())
            if has_issues:
                validation_results['invalid_records'] += 1
                validation_results['record_issues'].append({
                    'record_index': i,
                    'player_id': record.get('player_id', 'unknown'),
                    'full_name': record.get('full_name', 'unknown'),
                    'issues': issues
                })
                
                # Count issue types
                for issue_type, issue_list in issues.items():
                    validation_results['issues_by_type'][issue_type] += len(issue_list)
            else:
                validation_results['valid_records'] += 1
        
        # Calculate statistics
        if records:
            validation_results['statistics'] = self._calculate_statistics(records)
        
        return validation_results

    def _calculate_statistics(self, records: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics for the dataset"""
        stats = {}
        
        # Overall rating distribution
        overalls = [r.get('overall') for r in records if isinstance(r.get('overall'), (int, float))]
        if overalls:
            stats['overall_stats'] = {
                'min': min(overalls),
                'max': max(overalls),
                'mean': round(statistics.mean(overalls), 2),
                'median': statistics.median(overalls)
            }
        
        # Position distribution
        positions = [r.get('position') for r in records if r.get('position')]
        if positions:
            position_counts = {}
            for pos in positions:
                position_counts[pos] = position_counts.get(pos, 0) + 1
            stats['position_distribution'] = position_counts
        
        # Nationality distribution
        nationalities = [r.get('nationality') for r in records if r.get('nationality')]
        if nationalities:
            nationality_counts = {}
            for nat in nationalities:
                nationality_counts[nat] = nationality_counts.get(nat, 0) + 1
            stats['nationality_distribution'] = nationality_counts
        
        # League distribution
        leagues = [r.get('league') for r in records if r.get('league')]
        if leagues:
            league_counts = {}
            for league in leagues:
                league_counts[league] = league_counts.get(league, 0) + 1
            stats['league_distribution'] = league_counts
        
        return stats

    def validate_directory(self, directory: str, pattern: str = "*.json") -> Dict[str, Any]:
        """Validate all JSON files in a directory"""
        directory = Path(directory)
        
        if not directory.exists():
            return {'error': f"Directory not found: {directory}"}
        
        json_files = list(directory.glob(pattern))
        
        if not json_files:
            return {'error': f"No JSON files found in {directory}"}
        
        logger.info(f"Validating {len(json_files)} files in {directory}")
        
        results = {
            'directory': str(directory),
            'total_files': len(json_files),
            'files': {},
            'summary': {
                'total_records': 0,
                'valid_records': 0,
                'invalid_records': 0,
                'total_issues': 0
            }
        }
        
        for file_path in json_files:
            file_results = self.validate_file(file_path)
            results['files'][file_path.name] = file_results
            
            if 'error' not in file_results:
                results['summary']['total_records'] += file_results['total_records']
                results['summary']['valid_records'] += file_results['valid_records']
                results['summary']['invalid_records'] += file_results['invalid_records']
                results['summary']['total_issues'] += sum(file_results['issues_by_type'].values())
        
        return results

    def generate_report(self, validation_results: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Generate a human-readable validation report"""
        report_lines = []
        
        if 'error' in validation_results:
            return f"ERROR: {validation_results['error']}"
        
        # File-level report
        report_lines.append(f"Validation Report for {validation_results['file_path']}")
        report_lines.append("=" * 50)
        report_lines.append(f"Total Records: {validation_results['total_records']}")
        report_lines.append(f"Valid Records: {validation_results['valid_records']}")
        report_lines.append(f"Invalid Records: {validation_results['invalid_records']}")
        report_lines.append("")
        
        # Issue summary
        report_lines.append("Issue Summary:")
        for issue_type, count in validation_results['issues_by_type'].items():
            if count > 0:
                report_lines.append(f"  {issue_type.replace('_', ' ').title()}: {count}")
        
        report_lines.append("")
        
        # Statistics
        if validation_results['statistics']:
            report_lines.append("Statistics:")
            stats = validation_results['statistics']
            
            if 'overall_stats' in stats:
                overall = stats['overall_stats']
                report_lines.append(f"  Overall Rating - Min: {overall['min']}, Max: {overall['max']}, Mean: {overall['mean']}")
            
            if 'position_distribution' in stats:
                report_lines.append("  Position Distribution:")
                for pos, count in stats['position_distribution'].items():
                    report_lines.append(f"    {pos}: {count}")
        
        report_lines.append("")
        
        # Detailed issues
        if validation_results['record_issues']:
            report_lines.append("Detailed Issues:")
            for issue in validation_results['record_issues'][:10]:  # Show first 10 issues
                report_lines.append(f"  Record {issue['record_index']} ({issue['player_id']} - {issue['full_name']}):")
                for issue_type, issues in issue['issues'].items():
                    if issues:
                        for issue_msg in issues:
                            report_lines.append(f"    - {issue_msg}")
            
            if len(validation_results['record_issues']) > 10:
                report_lines.append(f"  ... and {len(validation_results['record_issues']) - 10} more issues")
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to {output_file}")
        
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate NHL player data')
    parser.add_argument('input', help='Input JSON file or directory')
    parser.add_argument('--output', help='Output file for validation report')
    parser.add_argument('--pattern', default='*.json', help='File pattern for directory processing')
    
    args = parser.parse_args()
    
    validator = DataValidator()
    
    try:
        input_path = Path(args.input)
        
        if input_path.is_file():
            # Single file validation
            results = validator.validate_file(input_path)
            report = validator.generate_report(results, args.output)
            print(report)
            
        elif input_path.is_dir():
            # Directory validation
            results = validator.validate_directory(input_path, args.pattern)
            if 'error' in results:
                print(f"ERROR: {results['error']}")
                sys.exit(1)
            
            # Generate summary report
            print(f"Directory Validation Summary for {results['directory']}")
            print("=" * 50)
            print(f"Total Files: {results['total_files']}")
            print(f"Total Records: {results['summary']['total_records']}")
            print(f"Valid Records: {results['summary']['valid_records']}")
            print(f"Invalid Records: {results['summary']['invalid_records']}")
            print(f"Total Issues: {results['summary']['total_issues']}")
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                logger.info(f"Detailed results saved to {args.output}")
        else:
            print(f"Invalid input: {input_path}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()