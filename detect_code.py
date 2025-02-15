import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import re
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class CodeAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b\w+\b|[^\w\s]',
            max_features=5000
        )
        self.logger = logging.getLogger(__name__)

    def _extract_features(self, code):
        """Extract various code features for analysis."""
        features = defaultdict(float)

        # Analyze code structure
        lines = code.split('\n')
        features['avg_line_length'] = np.mean([len(line.strip()) for line in lines if line.strip()])
        features['blank_line_ratio'] = len([l for l in lines if not l.strip()]) / (len(lines) or 1)

        # Enhanced indentation analysis
        indent_patterns = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        features['indent_consistency'] = np.std(indent_patterns) if indent_patterns else 0
        features['max_indent_depth'] = max(indent_patterns) if indent_patterns else 0

        # Advanced naming pattern analysis
        words = re.findall(r'\b[a-zA-Z_]\w*\b', code)
        if words:
            # Calculate average word length
            features['avg_name_length'] = np.mean([len(w) for w in words])

            # Enhanced naming convention analysis
            camel_case = len([w for w in words if re.match(r'^[a-z]+([A-Z][a-z]*)*$', w)])
            pascal_case = len([w for w in words if re.match(r'^[A-Z][a-z]+([A-Z][a-z]*)*$', w)])
            snake_case = len([w for w in words if re.match(r'^[a-z_]+$', w)])
            features['naming_consistency'] = max(camel_case, pascal_case, snake_case) / (len(words) or 1)
            features['naming_complexity'] = len(set([len(w) for w in words])) / (len(words) or 1)

        # Enhanced comment analysis
        single_line_comments = re.findall(r'#.*$', code, re.MULTILINE)
        multi_line_comments = re.findall(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', code)

        features['comment_ratio'] = len(''.join(single_line_comments + multi_line_comments)) / (len(code) or 1)
        features['comment_frequency'] = len(single_line_comments + multi_line_comments) / (len(lines) or 1)

        # Documentation patterns
        features['has_docstrings'] = bool(re.search(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', code))
        features['has_type_hints'] = bool(re.search(r':\s*[A-Za-z_][A-Za-z0-9_]*(\[[^\]]*\])?', code))
        features['has_parameter_docs'] = bool(re.search(r'@param|:param|Args:', code))
        features['has_return_docs'] = bool(re.search(r'@return|:return|Returns:', code))

        # Code complexity features
        features['line_complexity'] = len(re.findall(r'if|elif|else|for|while|try|except|with', code)) / (len(lines) or 1)
        features['nested_depth'] = max([line.count('    ') for line in lines]) if lines else 0

        return features

    def _calculate_ai_probability(self, features):
        """Calculate probability of code being AI-generated based on features."""
        # Enhanced weights for different features
        weights = {
            'avg_line_length': 0.1,       # AI tends to write medium-length lines
            'blank_line_ratio': 0.05,     # AI often has very consistent spacing
            'indent_consistency': 0.15,    # AI has very consistent indentation
            'max_indent_depth': 0.05,     # AI might use deeper nesting
            'avg_name_length': 0.1,       # AI often uses more descriptive names
            'naming_consistency': 0.15,    # AI is very consistent in naming
            'naming_complexity': 0.05,     # AI might use more complex names
            'comment_ratio': 0.1,         # AI often includes more comments
            'comment_frequency': 0.05,     # AI comments more regularly
            'has_docstrings': 0.05,       # AI usually includes docstrings
            'has_type_hints': 0.05,       # AI often uses type hints
            'has_parameter_docs': 0.05,    # AI includes parameter documentation
            'has_return_docs': 0.05,      # AI documents return values
            'line_complexity': 0.1,       # AI might write more complex lines
            'nested_depth': 0.05          # AI might use deeper nesting
        }

        # Calculate base probability with weighted features
        probability = 0

        # Line length (medium lines suggest AI)
        if 30 <= features['avg_line_length'] <= 80:
            probability += weights['avg_line_length']

        # Blank line ratio (very consistent spacing suggests AI)
        if 0.1 <= features['blank_line_ratio'] <= 0.3:
            probability += weights['blank_line_ratio']

        # Indentation (very consistent indentation suggests AI)
        if features['indent_consistency'] < 1:
            probability += weights['indent_consistency']

        # Max indent depth (deeper nesting might suggest AI)
        if features['max_indent_depth'] >= 3:
            probability += weights['max_indent_depth']

        # Variable naming (very consistent naming suggests AI)
        if features['naming_consistency'] > 0.8:
            probability += weights['naming_consistency']

        # Name complexity (more complex names suggest AI)
        if features['naming_complexity'] > 0.6:
            probability += weights['naming_complexity']

        # Comment patterns (high comment ratio suggests AI)
        if features['comment_ratio'] > 0.2:
            probability += weights['comment_ratio']

        # Regular commenting (consistent comment frequency suggests AI)
        if 0.2 <= features['comment_frequency'] <= 0.5:
            probability += weights['comment_frequency']

        # Documentation features
        if features['has_docstrings']:
            probability += weights['has_docstrings']
        if features['has_type_hints']:
            probability += weights['has_type_hints']
        if features['has_parameter_docs']:
            probability += weights['has_parameter_docs']
        if features['has_return_docs']:
            probability += weights['has_return_docs']

        # Code complexity
        if features['line_complexity'] > 0.3:
            probability += weights['line_complexity']
        if features['nested_depth'] >= 3:
            probability += weights['nested_depth']

        return min(100, max(0, probability * 100))

    def _generate_reasoning(self, features, probability):
        """Generate detailed reasoning for the analysis."""
        reasons = []

        # Code structure analysis
        reasons.append(f"Code Structure Analysis:\n"
                     f"- Average line length: {features['avg_line_length']:.1f} characters\n"
                     f"- Blank line ratio: {features['blank_line_ratio']:.1%}\n"
                     f"- Maximum indentation depth: {features['max_indent_depth']} levels\n"
                     f"- Line complexity: {features['line_complexity']:.2f} control structures per line")

        # Pattern analysis
        reasons.append(f"Pattern Analysis:\n"
                     f"- Indentation consistency: {'High' if features['indent_consistency'] < 1 else 'Variable'}\n"
                     f"- Naming convention consistency: {features['naming_consistency']:.1%}\n"
                     f"- Name complexity score: {features['naming_complexity']:.2f}")

        # Documentation analysis
        doc_features = []
        if features['has_docstrings']: doc_features.append("docstrings")
        if features['has_type_hints']: doc_features.append("type hints")
        if features['has_parameter_docs']: doc_features.append("parameter documentation")
        if features['has_return_docs']: doc_features.append("return value documentation")

        doc_status = "Comprehensive" if len(doc_features) >= 3 else "Partial" if doc_features else "Minimal"
        doc_details = f"including {', '.join(doc_features)}" if doc_features else "no formal documentation found"

        reasons.append(f"Documentation Analysis:\n"
                     f"- Documentation level: {doc_status} ({doc_details})\n"
                     f"- Comment ratio: {features['comment_ratio']:.1%}\n"
                     f"- Comment frequency: {features['comment_frequency']:.2f} comments per line")

        # Overall conclusion
        conclusion = (
            f"Based on the comprehensive analysis of code patterns, this code exhibits "
            f"{probability:.1f}% likelihood of being AI-generated. "
            f"This assessment is derived from the combination of "
            f"{'highly ' if probability > 70 else 'moderately ' if probability > 40 else 'loosely '}"
            f"structured code patterns, "
            f"{'systematic' if features['naming_consistency'] > 0.8 else 'natural'} naming conventions, "
            f"and {doc_status.lower()} documentation practices."
        )

        return "\n\n".join(reasons + [conclusion])

    def analyze(self, code):
        """Analyze code and return probability of being AI-generated with reasoning."""
        try:
            # Extract features
            features = self._extract_features(code)

            # Calculate probability
            probability = self._calculate_ai_probability(features)

            # Generate reasoning
            reasoning = self._generate_reasoning(features, probability)

            return {
                'probability': probability,
                'reasoning': reasoning
            }

        except Exception as e:
            self.logger.error(f"Error during code analysis: {str(e)}")
            return {
                'probability': 50,
                'reasoning': f"Error during analysis: {str(e)}"
            }