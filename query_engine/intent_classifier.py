# import re


# class QueryIntentClassifier:
#     """
#     Classifies query into intent categories.
#     """

#     def classify(self, query: str):
#         q = query.lower()

#         # Metadata queries
#         if any(k in q for k in ["how many pages", "how many words", "document language", "file size"]):
#             return "metadata"

#         # Aggregate queries
#         if any(k in q for k in ["how many", "count", "total number of"]):
#             return "aggregate"

#         # Analytical / derived queries
#         if any(k in q for k in ["how old", "age of", "year difference", "timeline"]):
#             return "analytical"

#         # Summary / structure queries
#         if any(k in q for k in ["structure", "outline", "sections", "articles"]):
#             return "analytical"

#         # Default → content-based
#         return "content"




''' CLAUDE '''

"""
Query Intent Classification Module
Enhanced with expanded keywords and detailed categorization.
"""

import re
from typing import Dict, List, Optional
from enum import Enum
from typing import Any, Dict


class QueryIntent(Enum):
    """Enumeration of all supported query intents"""
    METADATA = "metadata"
    AGGREGATE = "aggregate"
    ANALYTICAL = "analytical"
    STRUCTURAL = "structural"
    CONTENT_EXTRACTION = "content_extraction"
    SUMMARIZATION = "summarization"
    COMPARISON = "comparison"
    INTERPRETATION = "interpretation"
    SEARCH_LOOKUP = "search_lookup"
    QUANTITATIVE = "quantitative"
    CAUSATION = "causation"
    PREDICTIVE = "predictive"
    CRITICAL_ANALYSIS = "critical_analysis"
    CONTEXTUAL = "contextual"
    CROSS_REFERENCE = "cross_reference"
    VISUAL_ELEMENTS = "visual_elements"
    PROCEDURAL = "procedural"
    OPINION_STANCE = "opinion_stance"
    DEFINITIONAL = "definitional"
    COMPLIANCE = "compliance"
    SENTIMENT = "sentiment"
    FORMAT_PRESENTATION = "format_presentation"
    GENERAL_CONTENT = "general_content"


class IntentClassifier:
    """
    Enhanced deterministic intent classifier with comprehensive keyword coverage.
    """
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[QueryIntent, List[Dict]]:
        """
        Initialize comprehensive pattern rules for each intent category.
        """
        return {
            # ============================================
            # METADATA QUERIES
            # ============================================
            QueryIntent.METADATA: [
                {
                    "keywords": [
                        # Page-related (PDF property)
                        "how many pages", "number of pages", "page count", "total pages",
                        "pages in this document", "page numbers in document",
                        
                        # Word/character count (PDF property)
                        "word count", "how many words in this document", "number of words in document",
                        "total words in document", "character count", "how many characters in document",
                        "size of this document", "document file size", "file size of document",
                        "how big is this document",
                        
                        # Date/time metadata (PDF file metadata only - requires "this document" context)
                        "when was this document published", "when was this document created",
                        "when was this document written", "publication date of this document",
                        "created date of this document", "date this document was published",
                        "date this document was created", "last modified date",
                        "document creation date", "document publication date",
                        
                        # Author/creator (PDF metadata only - requires document context)
                        "who wrote this document", "who is the author of this document",
                        "author of this document", "written by who", "created by who",
                        "authors of this document", "author name of this document",
                        "writer of this document", "who created this document",
                        
                        # Title (PDF metadata)
                        "title of this document", "document title", "what is the title of this document",
                        "name of this document", "document name", "what is this document called",
                        "what is this document titled",
                        
                        # Type/format (PDF property)
                        "type of this document", "what type of document is this",
                        "kind of document is this", "what type is this document",
                        "format of this document", "document format", "file format",
                        
                        # Language (document property)
                        "what language is this document", "language of this document",
                        "written in which language", "document language", "what language",
                        
                        # Version (PDF metadata)
                        "version of this document", "document version", "edition",
                        "revision number", "draft number",
                    ],
                    "patterns": [
                        # Require "this document" or "document" context for metadata queries
                        r"\bhow many pages\b.*\b(document|file|pdf)\b",
                        r"\bpage count\b.*\b(document|file|pdf)\b",
                        r"\bword count\b.*\b(document|file|pdf)\b",
                        r"\b(document|this document|the document)\b.*\bpublished\b.*\b(when|date)\b",
                        r"\bwhen was (this|the) document\b.*\b(published|created|written)\b",
                        r"\b(document|this document|the document)\b.*\btitle\b",
                        r"\btitle\b.*\b(this|the) document\b",
                        r"\b(document|this document|the document)\b.*\bauthor\b",
                        r"\bauthor\b.*\b(this|the) document\b",
                        r"\bhow (long|big|large)\b.*\b(this|the) document\b",
                        r"\b(this|the) document\b.*\b(length|size)\b",
                        r"\bfile size\b",
                        r"\bdocument (file )?size\b",
                    ],
                    "negative_patterns": [
                        # Exclude queries about content (not metadata)
                        r"\bwhen was .+ (written|created|published|established|founded|adopted|enacted)\b",
                        r"\bwhen did .+ happen\b",
                        r"\bwhen .+ (occurred|took place|was founded|was established)\b",
                    ]
                }
            ],
            
            # ============================================
            # AGGREGATE QUERIES (Counting)
            # ============================================
            QueryIntent.AGGREGATE: [
                {
                    "keywords": [
                        # General counting
                        "count", "how many", "total number", "number of", "total count",
                        "enumerate", "list all", "show all", "how much",
                        
                        # Sections/chapters
                        "how many sections", "count sections", "number of sections",
                        "how many chapters", "count chapters", "number of chapters",
                        "how many parts", "count parts", "number of parts",
                        
                        # References/citations
                        "how many references", "count references", "number of references",
                        "how many citations", "count citations", "number of citations",
                        "how many sources", "bibliography count",
                        
                        # Tables/figures
                        "how many tables", "count tables", "number of tables",
                        "how many figures", "count figures", "number of figures",
                        "how many images", "count images", "number of images",
                        "how many charts", "count charts", "number of charts",
                        "how many graphs", "count graphs", "number of graphs",
                        "how many diagrams", "count diagrams",
                        
                        # Specific mentions
                        "how many times", "occurrences of", "frequency of",
                        "mentions of", "appears how many", "count mentions",
                        
                        # Articles/clauses (legal docs)
                        "how many articles", "count articles", "number of articles",
                        "how many clauses", "count clauses", "number of clauses",
                        "how many provisions", "count provisions",
                        
                        # Appendices/annexures
                        "how many appendices", "how many annexures", "count appendices",
                        
                        # Authors/contributors
                        "how many authors", "number of authors", "count authors",
                        "how many contributors", "number of contributors",
                    ],
                    "patterns": [
                        r"\bcount\b.*\b(sections?|chapters?|parts?|articles?|clauses?)\b",
                        r"\bhow many\b.*\b(times?|sections?|chapters?|references?|tables?|figures?)\b",
                        r"\bnumber of\b.*\b(sections?|chapters?|references?|citations?)\b",
                        r"\btotal (number|count) of\b",
                        r"\blist all\b.*\b(sections?|chapters?|references?)\b",
                        r"\bhow many times\b.*\b(mentioned|appears?|occur)\b",
                        r"\bfrequency of\b",
                        r"\boccurrences? of\b",
                    ]
                }
            ],
            
            # ============================================
            # ANALYTICAL QUERIES (Computation)
            # ============================================
            QueryIntent.ANALYTICAL: [
                {
                    "keywords": [
                        # Age/time calculations
                        "how old", "age of", "how long ago", "years old",
                        "when was this document written", "how recent", "how outdated",
                        
                        # Time spans
                        "time span", "time period", "duration", "time range",
                        "period covered", "covers what period", "from when to when",
                        "time frame", "temporal range",
                        
                        # Averages/statistics
                        "average", "mean", "median", "typical", "generally",
                        "on average", "average value", "mean value",
                        
                        # Percentages
                        "percentage", "percent", "what percent", "how much percent",
                        "proportion", "ratio",
                        
                        # Growth/trends
                        "growth rate", "rate of growth", "increase rate",
                        "change over time", "how much increased", "how much decreased",
                        "rate of change", "velocity", "acceleration",
                        
                        # Comparisons (numerical)
                        "difference between", "gap between", "deviation",
                        "variance", "how much more", "how much less",
                        
                        # Maximum/minimum
                        "highest", "lowest", "maximum", "minimum", "peak",
                        "greatest", "smallest", "largest", "least",
                        
                        # Trends
                        "trend", "pattern", "trajectory", "direction",
                        "going up", "going down", "increasing", "decreasing",
                        
                        # Calculations
                        "calculate", "compute", "sum", "total", "aggregate",
                        "add up", "sum up",
                    ],
                    "patterns": [
                        r"\bhow old\b.*\bdocument\b",
                        r"\bage of\b.*\bdocument\b",
                        r"\btime span\b",
                        r"\bperiod covered\b",
                        r"\baverage\b.*\b(of|value|number)\b",
                        r"\b(highest|lowest|maximum|minimum)\b.*\b(value|percentage|number)\b",
                        r"\bgrowth rate\b",
                        r"\b(increase|decrease)d?\b.*\bby\b.*\b(percent|%)\b",
                        r"\btrend\b.*\b(analysis|over time|pattern)\b",
                        r"\bcalculate\b.*\b(total|average|sum)\b",
                    ]
                }
            ],
            
            # ============================================
            # STRUCTURAL QUERIES
            # ============================================
            QueryIntent.STRUCTURAL: [
                {
                    "keywords": [
                        # Organization
                        "structure", "organization", "organized", "structured",
                        "how is it organized", "how is it structured",
                        "document structure", "document organization",
                        
                        # Table of contents
                        "table of contents", "toc", "contents", "index",
                        "outline", "overview of structure",
                        
                        # Hierarchy
                        "hierarchy", "hierarchical", "levels", "nested",
                        "parent sections", "subsections", "sub-sections",
                        
                        # Layout
                        "layout", "format", "formatting", "arrangement",
                        "how is it laid out", "document layout",
                        
                        # Order/sequence
                        "order", "sequence", "ordering", "arranged",
                        "what comes first", "what follows",
                        
                        # Divisions
                        "divided into", "split into", "broken into",
                        "sections breakdown", "chapter breakdown",
                    ],
                    "patterns": [
                        r"\btable of contents\b",
                        r"\bstructure of\b.*\bdocument\b",
                        r"\bdocument\b.*\bstructure\b",
                        r"\bhow (is|are)\b.*\b(organized|structured|arranged)\b",
                        r"\blayout of\b.*\bdocument\b",
                        r"\bhierarchy\b",
                        r"\bdivided into\b.*\b(sections?|parts?|chapters?)\b",
                    ]
                }
            ],
            
            # ============================================
            # SUMMARIZATION QUERIES
            # ============================================
            QueryIntent.SUMMARIZATION: [
                {
                    "keywords": [
                        # Direct summarization (English)
                        "summarize", "summary", "summarise", "sum up",
                        "brief summary", "quick summary", "short summary",
                        
                        # Overview
                        "overview", "brief overview", "general overview",
                        "high-level overview", "quick overview",
                        
                        # Key points
                        "key points", "main points", "important points",
                        "key takeaways", "main takeaways", "takeaways",
                        "highlights", "key highlights",
                        
                        # Essence
                        "gist", "essence", "crux", "core", "heart of",
                        "in a nutshell", "in brief", "briefly",
                        
                        # Abstract
                        "abstract", "synopsis", "précis", "digest",
                        
                        # Condensed versions
                        "condensed version", "shortened version",
                        "in short", "in summary", "to summarize",
                        
                        # Main ideas
                        "main ideas", "central ideas", "key ideas",
                        "core concepts", "main themes", "central themes",
                        
                        # Telugu summarization keywords
                        "సంగ్రహ", "సంగ్రహం", "సంగ్రహించు", "సంగ్రహించగలరా",
                        "సంక్షిప్త", "సారాంశ", "సారాంశం",
                        "ప్రధానాంశాలు", "కీ పాయింట్", "ముఖ్యాంశాలు",
                        
                        # Hindi summarization keywords
                        "सारांश", "सार", "संक्षेप", "संक्षिप्त", "सारांशित",
                        "मुख्य बिंदु", "प्रमुख बिंदु", "अवलोकन",
                        
                        # Tamil summarization keywords
                        "சுருக்கம்", "சுருக்க", "சுருக்கமாக",
                        "முக்கிய புள்ளிகள்", "முக்கிய கருத்துக்கள்",
                        
                        # Malayalam summarization keywords
                        "സംഗ്രഹം", "സംഗ്രഹിക്കുക", "സംഗ്രഹിക്കാം",
                        "സംക്ഷേപം", "പ്രധാന പോയിന്റുകൾ",
                        
                        # Bengali summarization keywords
                        "সারাংশ", "সংক্ষিপ্ত", "সারসংক্ষেপ",
                        "মূল বিষয়", "প্রধান পয়েন্ট",
                    ],
                    "patterns": [
                        r"\bsummarize\b",
                        r"\bsummary (of|for)\b",
                        r"\bin (brief|short|summary)\b",
                        r"\boverview of\b",
                        r"\bkey (points|takeaways|highlights)\b",
                        r"\bmain (points|ideas|themes)\b",
                        r"\bgist of\b",
                        r"\bwhat (is|are)\b.*\b(main|key|important)\b",
                    ]
                }
            ],
            
            # ============================================
            # COMPARISON QUERIES
            # ============================================
            QueryIntent.COMPARISON: [
                {
                    "keywords": [
                        # Direct comparison
                        "compare", "comparison", "compare and contrast",
                        "in comparison", "comparatively",
                        
                        # Differences
                        "difference", "differences between", "differ",
                        "what's different", "how different", "differentiate",
                        "distinguish between", "distinction",
                        
                        # Versus
                        "versus", "vs", "vs.", "against",
                        
                        # Similarities
                        "similarities", "similar to", "alike", "resemble",
                        "common between", "shared", "in common",
                        
                        # Contrast
                        "contrast", "contrasting", "in contrast",
                        "as opposed to", "rather than",
                        
                        # Relative comparisons
                        "better than", "worse than", "more than", "less than",
                        "superior to", "inferior to", "preferable to",
                        
                        # How does X relate to Y
                        "how does", "relationship between", "relation between",
                        "compared to", "relative to", "with respect to",
                    ],
                    "patterns": [
                        r"\bcompare\b.*\b(with|to|and)\b",
                        r"\bdifference(s)? between\b",
                        r"\bvs\.?\b",
                        r"\bversus\b",
                        r"\bcontrast\b.*\b(with|between)\b",
                        r"\b(similar|different)\b.*\b(to|from|than)\b",
                        r"\bhow does\b.*\b(compare|differ|relate)\b",
                        r"\b(better|worse|more|less) than\b",
                    ]
                }
            ],
            
            # ============================================
            # INTERPRETATION QUERIES
            # ============================================
            QueryIntent.INTERPRETATION: [
                {
                    "keywords": [
                        # Meaning
                        "what does", "what do", "mean", "meaning of",
                        "means", "meant by", "meaning behind",
                        
                        # Explanation
                        "explain", "explanation", "elaborate", "clarify",
                        "clarification", "elucidate",
                        
                        # Interpretation
                        "interpret", "interpretation", "how to interpret",
                        
                        # Significance
                        "significance", "significant", "important",
                        "importance of", "why is it important",
                        
                        # Implications
                        "implies", "implication", "what does this imply",
                        "suggest", "indicates", "signifies",
                        
                        # Understanding
                        "understand", "understanding", "how to understand",
                        "make sense of", "comprehend",
                        
                        # Context/intent
                        "intended meaning", "actual meaning", "real meaning",
                        "trying to say", "getting at",
                    ],
                    "patterns": [
                        r"\bwhat does\b.*\bmean\b",
                        r"\bmeaning (of|behind)\b",
                        r"\bexplain\b.*\b(concept|term|phrase)\b",
                        r"\binterpretation (of|for)\b",
                        r"\bsignificance of\b",
                        r"\bwhat (is|are)\b.*\b(implying|suggesting|indicating)\b",
                        r"\bimplications? (of|for)\b",
                        r"\bwhat (is|are|does)\b.*\b(document|text|about)\b",
                    ]
                }
            ],
            
            # ============================================
            # SEARCH/LOOKUP QUERIES
            # ============================================
            QueryIntent.SEARCH_LOOKUP: [
                {
                    "keywords": [
                        # Finding
                        "find", "find all", "find the", "can you find",
                        
                        # Locating
                        "locate", "where is", "where are", "where can i find",
                        "location of", "position of",
                        
                        # Which page
                        "which page", "what page", "on which page",
                        "page number", "found on page",
                        
                        # Searching
                        "search", "search for", "look for", "looking for",
                        "seek", "seeking",
                        
                        # Showing/displaying
                        "show", "show me", "display", "get", "get me",
                        "retrieve", "fetch",
                        
                        # Extraction
                        "extract", "pull", "pull out", "get all",
                        
                        # Presence checks
                        "does it mention", "is there", "are there",
                        "contains", "includes", "has",
                        
                        # Point to
                        "point to", "direct me to", "take me to",
                    ],
                    "patterns": [
                        r"\bfind (all|the)?\b.*\b(mentions?|references?|instances?)\b",
                        r"\blocate\b.*\b(section|page|paragraph)\b",
                        r"\bwhere (is|are|does|can)\b",
                        r"\bwhich page\b.*\b(mentions?|discusses?|contains?)\b",
                        r"\bsearch for\b",
                        r"\bshow me\b.*\b(all|the)?\b",
                        r"\bdoes (it|the document)\b.*\b(mention|contain|include)\b",
                    ]
                }
            ],
            
            # ============================================
            # QUANTITATIVE QUERIES
            # ============================================
            QueryIntent.QUANTITATIVE: [
                {
                    "keywords": [
                        # Statistics
                        "statistics", "stats", "statistical", "data",
                        "metrics", "measurements", "figures",
                        
                        # Numbers
                        "numbers", "numerical", "numeric", "values",
                        "quantities", "amounts",
                        
                        # Specific metrics
                        "revenue", "cost", "price", "sales", "profit",
                        "expenses", "budget", "spending",
                        
                        # Percentages
                        "percentage", "percent", "%", "proportion",
                        
                        # Rates
                        "rate", "rates", "ratio", "ratios",
                        
                        # Financial
                        "financial", "fiscal", "monetary", "economic",
                        
                        # Performance metrics
                        "performance", "kpi", "indicator", "benchmark",
                    ],
                    "patterns": [
                        r"\bstatistics\b.*\b(for|on|about)\b",
                        r"\bnumerical (data|values?|information)\b",
                        r"\bpercentage\b.*\b(of|for)\b",
                        r"\b(revenue|cost|price|sales)\b.*\b(figures?|data|numbers?)\b",
                        r"\bwhat (is|are)\b.*\b(numbers?|values?|amounts?)\b",
                        r"\bfinancial (data|information|figures?)\b",
                    ]
                }
            ],
            
            # ============================================
            # CAUSATION QUERIES
            # ============================================
            QueryIntent.CAUSATION: [
                {
                    "keywords": [
                        # Why
                        "why", "why did", "why does", "why is", "why are",
                        "why was", "why were", "for what reason",
                        
                        # Reason
                        "reason", "reasons", "reason for", "reason behind",
                        "reasoning", "rationale",
                        
                        # Cause
                        "cause", "caused", "causes", "caused by",
                        "causation", "causal",
                        
                        # Result/effect
                        "led to", "resulted in", "leads to", "results in",
                        "consequence", "outcome", "effect",
                        
                        # Due to
                        "due to", "because", "because of",
                        "owing to", "on account of",
                        
                        # Driving factors
                        "what drove", "what prompted", "what triggered",
                        "what motivated", "driving force",
                        
                        # Origins
                        "origin", "root cause", "source of",
                        "stems from", "originates from",
                    ],
                    "patterns": [
                        r"\bwhy (did|does|is|are|was|were)\b",
                        r"\breason(s)? (for|behind|why)\b",
                        r"\bcause(d)? (of|by|for)\b",
                        r"\b(led|lead) to\b",
                        r"\bresulted? in\b",
                        r"\bdue to\b",
                        r"\bbecause (of)?\b",
                        r"\bwhat (drove|prompted|triggered|caused)\b",
                    ]
                }
            ],
            
            # ============================================
            # PREDICTIVE QUERIES
            # ============================================
            QueryIntent.PREDICTIVE: [
                {
                    "keywords": [
                        # Future
                        "future", "in the future", "going forward",
                        "ahead", "coming", "upcoming",
                        
                        # Predictions
                        "predict", "predicted", "prediction", "predictions",
                        "predicts", "predicting",
                        
                        # Forecasts
                        "forecast", "forecasts", "forecasted", "forecasting",
                        
                        # Projections
                        "projection", "projections", "projected",
                        "project", "projects",
                        
                        # Expectations
                        "expect", "expected", "expectation", "expectations",
                        "anticipate", "anticipated", "anticipation",
                        
                        # Outlook
                        "outlook", "prospects", "perspective",
                        
                        # Trends
                        "trends", "trending", "trend analysis",
                        "future trends", "emerging trends",
                        
                        # Next steps
                        "next steps", "next phase", "following steps",
                        "what's next", "what next", "moving forward",
                        
                        # Planning
                        "plans", "planning", "planned", "roadmap",
                        "strategy", "strategic",
                    ],
                    "patterns": [
                        r"\bfuture\b.*\b(trends?|plans?|outlook)\b",
                        r"\bpredict(ed|ion|s)?\b",
                        r"\bforecast(s|ed)?\b",
                        r"\bprojection(s)?\b.*\b(for|of)\b",
                        r"\bexpect(ed|ation)?\b.*\b(future|next|coming)\b",
                        r"\bnext steps?\b",
                        r"\bwhat (is|are)\b.*\b(expected|anticipated|predicted)\b",
                    ]
                }
            ],
            
            # ============================================
            # DEFINITIONAL QUERIES
            # ============================================
            QueryIntent.DEFINITIONAL: [
                {
                    "keywords": [
                        # Define
                        "define", "definition", "defined as",
                        "what is the definition",
                        
                        # What is/are
                        "what is", "what are", "what does", "what do",
                        "what's", "whats",
                        
                        # Meaning (definitional context)
                        "meaning", "means", "mean",
                        
                        # Terminology
                        "terminology", "term", "terms",
                        "technical term", "jargon",
                        
                        # Glossary
                        "glossary", "vocabulary", "lexicon",
                        
                        # Acronyms
                        "acronym", "abbreviation", "stands for",
                        "short for", "abbreviated as",
                        
                        # Concept explanation
                        "concept of", "notion of", "idea of",
                        
                        # Refers to
                        "refers to", "referring to", "reference to",
                    ],
                    "patterns": [
                        r"\bdefine\b.*\b(term|concept|word)\b",
                        r"\bdefinition (of|for)\b",
                        r"\bwhat (is|are)\b.*\b(term|concept|word|meaning)\b",
                        r"\bacronym\b.*\b(for|of|means?)\b",
                        r"\bstands for\b",
                        r"\bterminology\b.*\b(used|in)\b",
                        r"\bglossary\b",
                        r"\b(what|which)\b.*\brefers? to\b",
                    ]
                }
            ],
            
            # ============================================
            # PROCEDURAL QUERIES
            # ============================================
            QueryIntent.PROCEDURAL: [
                {
                    "keywords": [
                        # How to
                        "how to", "how do", "how can", "how should",
                        "how would", "how do i", "how can i",
                        
                        # Steps
                        "steps", "step by step", "step-by-step",
                        "steps to", "steps for", "steps in",
                        
                        # Procedure
                        "procedure", "procedures", "procedural",
                        
                        # Process
                        "process", "processes", "processing",
                        "what is the process",
                        
                        # Instructions
                        "instructions", "instruction", "instructed",
                        "how to follow",
                        
                        # Method
                        "method", "methodology", "methods",
                        "approach", "way to",
                        
                        # Guide
                        "guide", "guideline", "guidelines",
                        
                        # Implementation
                        "implement", "implementation", "implementing",
                        "how to implement",
                        
                        # Walkthrough
                        "walkthrough", "walk through", "walk me through",
                        
                        # Execution
                        "execute", "carry out", "perform",
                        "accomplish", "achieve",
                    ],
                    "patterns": [
                        r"\bhow to\b.*\b(do|perform|execute|implement)\b",
                        r"\bsteps (to|for|in)\b",
                        r"\bprocedure (for|to|of)\b",
                        r"\bprocess (of|for|to)\b",
                        r"\binstructions (for|to|on)\b",
                        r"\bmethod(ology)? (for|of|to)\b",
                        r"\bwalkthrough (of|for)\b",
                        r"\bhow (do|can|should) (i|we|you)\b",
                    ]
                }
            ],
            
            # ============================================
            # VISUAL ELEMENTS QUERIES
            # ============================================
            QueryIntent.VISUAL_ELEMENTS: [
                {
                    "keywords": [
                        # Charts
                        "chart", "charts", "bar chart", "pie chart",
                        "line chart", "flow chart", "flowchart",
                        
                        # Graphs
                        "graph", "graphs", "bar graph", "line graph",
                        
                        # Figures
                        "figure", "figures", "fig", "fig.",
                        
                        # Tables
                        "table", "tables", "data table",
                        
                        # Diagrams
                        "diagram", "diagrams", "schematic",
                        "illustration", "illustrations",
                        
                        # Images
                        "image", "images", "picture", "pictures",
                        "photo", "photos", "photograph",
                        
                        # Visuals
                        "visual", "visuals", "visualization",
                        "infographic", "infographics",
                        
                        # Describe visual
                        "describe the", "what does the", "explain the",
                        "show in the", "depicted in",
                        
                        # Shows/displays
                        "shows", "displays", "illustrates",
                        "represents", "depicts",
                    ],
                    "patterns": [
                        r"\b(chart|graph|figure|table|diagram)\b.*\b(shows?|displays?)\b",
                        r"\b(shows?|displays?)\b.*\b(chart|graph|figure|table)\b",
                        r"\bdescribe (the|this)?\b.*\b(chart|figure|image|diagram)\b",
                        r"\bwhat (does|is)\b.*\b(figure|chart|graph|table)\b.*\b(show|display|illustrate)\b",
                        r"\bon page\b.*\b(figure|chart|table|diagram)\b",
                        r"\bfigure \d+\b",
                        r"\btable \d+\b",
                    ]
                }
            ],

            # ============================================
            # CRITICAL ANALYSIS QUERIES
            # ============================================
            QueryIntent.CRITICAL_ANALYSIS: [
                {
                    "keywords": [
                        # Limitations
                        "limitation", "limitations", "limited by",
                        "limits", "constrained by", "constraints",
                        
                        # Weaknesses
                        "weakness", "weaknesses", "weak point",
                        "shortcoming", "shortcomings", "flaw", "flaws",
                        
                        # Gaps
                        "gap", "gaps", "missing", "lacking",
                        "absence of", "not covered", "omitted",
                        
                        # Assumptions
                        "assumption", "assumptions", "assumed",
                        "presupposed", "presupposition",
                        
                        # Critique
                        "critique", "criticism", "criticize",
                        "critical analysis", "critically",
                        
                        # Evaluation
                        "evaluate", "evaluation", "assess", "assessment",
                        "appraisal", "review",
                        
                        # Validity
                        "validity", "valid", "reliability", "reliable",
                        "credibility", "credible", "trustworthy",
                        
                        # Bias
                        "bias", "biased", "prejudice", "one-sided",
                        
                        # Challenges
                        "challenge", "challenges", "problem", "problems",
                        "issue", "issues", "concern", "concerns",
                    ],
                    "patterns": [
                        r"\blimitation(s)?\b.*\b(of|in|with)\b",
                        r"\bweakness(es)?\b",
                        r"\bgap(s)? (in|of)\b",
                        r"\bassumption(s)?\b.*\b(made|in|of)\b",
                        r"\bcritique\b.*\b(of|on)\b",
                        r"\bevaluate\b.*\b(validity|reliability|credibility)\b",
                        r"\bbias(ed)?\b.*\b(in|of)\b",
                        r"\bchallenge(s)?\b.*\b(with|in|of)\b",
                        r"\bflaw(s)?\b.*\b(in|of|with)\b",
                        r"\bshortcoming(s)?\b",
                    ]
                }
            ],
            
            # ============================================
            # CONTEXTUAL QUERIES
            # ============================================
            QueryIntent.CONTEXTUAL: [
                {
                    "keywords": [
                        # Context
                        "context", "contextual", "in context",
                        "background", "setting", "circumstances",
                        
                        # Historical context
                        "historical context", "historical background",
                        "when it was written", "time period",
                        
                        # Cultural context
                        "cultural context", "cultural background",
                        "social context", "political context",
                        
                        # Situation
                        "situation", "conditions", "environment",
                        "surrounding", "circumstances",
                        
                        # Framework
                        "framework", "perspective", "lens",
                        "viewpoint", "standpoint",
                        
                        # Relevance
                        "relevant to", "relevance", "applies to",
                        "applicable to", "pertains to",
                        
                        # Background info
                        "background information", "backdrop",
                        "preceding events", "prior context",
                    ],
                    "patterns": [
                        r"\bcontext (of|for|in)\b",
                        r"\bhistorical (context|background)\b",
                        r"\bcultural (context|background)\b",
                        r"\bin (what|which)\b.*\bcontext\b",
                        r"\bbackground\b.*\b(of|for|to)\b",
                        r"\brelevant to\b.*\b(situation|context)\b",
                        r"\bsurrounding\b.*\b(circumstances|conditions)\b",
                    ]
                }
            ],
            
            # ============================================
            # CROSS-REFERENCE QUERIES
            # ============================================
            QueryIntent.CROSS_REFERENCE: [
                {
                    "keywords": [
                        # References
                        "refer to", "refers to", "reference to",
                        "referenced in", "referring to",
                        
                        # Citations
                        "cite", "cited", "citation", "cites",
                        "source", "sources",
                        
                        # Links
                        "link", "linked", "links to", "connection",
                        "connected to", "related to", "relates to",
                        
                        # Mentions
                        "mention", "mentioned", "mentions",
                        "discussed in", "appears in",
                        
                        # Sections
                        "see section", "see chapter", "see page",
                        "as mentioned in", "as discussed in",
                        
                        # Bibliography
                        "bibliography", "works cited", "references list",
                        "footnote", "endnote",
                        
                        # Cross-links
                        "cross-reference", "cross reference",
                        "elsewhere in", "other parts",
                    ],
                    "patterns": [
                        r"\brefer(s)?\b.*\b(to|in)\b",
                        r"\bcite(d|s)?\b.*\b(in|as|from)\b",
                        r"\bmentioned (in|on|at)\b.*\b(section|chapter|page)\b",
                        r"\bsee (section|chapter|page)\b",
                        r"\bcross[- ]?reference\b",
                        r"\blinked? to\b.*\b(section|page|document)\b",
                        r"\belsewhere in\b.*\bdocument\b",
                    ]
                }
            ],
            
            # ============================================
            # OPINION/STANCE QUERIES
            # ============================================
            QueryIntent.OPINION_STANCE: [
                {
                    "keywords": [
                        # Opinion
                        "opinion", "opinions", "view", "views",
                        "viewpoint", "perspective",
                        
                        # Stance
                        "stance", "position", "stand", "standing",
                        "take on", "position on",
                        
                        # Argument
                        "argument", "arguments", "argues", "arguing",
                        "claim", "claims", "contention",
                        
                        # Belief
                        "believe", "believes", "belief", "beliefs",
                        
                        # Advocate
                        "advocate", "advocates", "advocating",
                        "support", "supports", "supporting",
                        "endorse", "endorses",
                        
                        # Oppose
                        "oppose", "opposes", "opposing", "opposition",
                        "against", "disagree", "disagrees",
                        
                        # Recommendation
                        "recommend", "recommends", "recommendation",
                        "suggest", "suggests", "suggestion",
                        
                        # Author's view
                        "author's view", "author's opinion",
                        "author's stance", "author argues",
                    ],
                    "patterns": [
                        r"\bauthor(s)?\b.*\b(view|opinion|stance|position|argument)\b",
                        r"\bwhat (is|are)\b.*\b(opinion|view|stance|position)\b",
                        r"\b(argue|claim|believe|advocate)s?\b.*\b(that|for)\b",
                        r"\bstance (on|toward)\b",
                        r"\bposition (on|regarding)\b",
                        r"\b(support|oppose)s?\b.*\b(idea|notion|concept)\b",
                        r"\brecommend(s|ation)?\b",
                    ]
                }
            ],
            
            # ============================================
            # COMPLIANCE QUERIES
            # ============================================
            QueryIntent.COMPLIANCE: [
                {
                    "keywords": [
                        # Regulations
                        "regulation", "regulations", "regulatory",
                        "compliant", "compliance",
                        
                        # Legal
                        "legal", "law", "laws", "legislation",
                        "statute", "statutes", "legal requirement",
                        
                        # Standards
                        "standard", "standards", "standard compliance",
                        "meets standards", "adheres to",
                        
                        # Requirements
                        "requirement", "requirements", "required",
                        "mandatory", "obligatory", "must comply",
                        
                        # Guidelines
                        "guideline", "guidelines", "policy", "policies",
                        "protocol", "protocols",
                        
                        # Certification
                        "certification", "certified", "accreditation",
                        "accredited", "certified as",
                        
                        # Violations
                        "violation", "violations", "violate", "breach",
                        "non-compliant", "non-compliance",
                        
                        # Audit
                        "audit", "audited", "auditing", "inspection",
                        
                        # Conformity
                        "conform", "conforms", "conformity",
                        "accordance with", "in compliance with",
                    ],
                    "patterns": [
                        r"\bcompl(y|iance|iant)\b.*\b(with|to)\b",
                        r"\bregulation(s)?\b.*\b(require|mandate)\b",
                        r"\blegal requirement(s)?\b",
                        r"\bstandard(s)?\b.*\b(met|followed|adhered)\b",
                        r"\bmeets?\b.*\b(requirement|standard|regulation)\b",
                        r"\bviolation(s)?\b.*\b(of|with)\b",
                        r"\bin accordance with\b",
                        r"\bcertif(ied|ication)\b.*\b(by|from|to)\b",
                    ]
                }
            ],
            
            # ============================================
            # SENTIMENT QUERIES
            # ============================================
            QueryIntent.SENTIMENT: [
                {
                    "keywords": [
                        # Tone
                        "tone", "tonal", "tonality",
                        
                        # Sentiment
                        "sentiment", "sentiments", "feeling",
                        "emotional tone", "mood",
                        
                        # Positive/negative
                        "positive", "negative", "neutral",
                        "optimistic", "pessimistic",
                        
                        # Attitude
                        "attitude", "attitudes", "disposition",
                        
                        # Emotion
                        "emotion", "emotions", "emotional",
                        "feeling", "feelings",
                        
                        # Favorable/unfavorable
                        "favorable", "unfavorable", "supportive",
                        "critical", "approving", "disapproving",
                        
                        # Perspective
                        "hopeful", "skeptical", "cautious",
                        "enthusiastic", "concerned",
                    ],
                    "patterns": [
                        r"\btone (of|in)\b.*\b(document|text|writing)\b",
                        r"\bsentiment\b.*\b(toward|about|regarding)\b",
                        r"\b(positive|negative|neutral)\b.*\b(tone|view|sentiment)\b",
                        r"\bemotional (tone|content)\b",
                        r"\battitude\b.*\b(toward|about)\b",
                        r"\bhow (is|are)\b.*\b(portrayed|presented|described)\b",
                    ]
                }
            ],
            
            # ============================================
            # FORMAT/PRESENTATION QUERIES
            # ============================================
            QueryIntent.FORMAT_PRESENTATION: [
                {
                    "keywords": [
                        # Format
                        "format", "formatted", "formatting",
                        "file format", "document format",
                        
                        # Presentation
                        "presentation", "presented", "presents",
                        "how is it presented",
                        
                        # Style
                        "style", "styling", "styled",
                        "writing style", "citation style",
                        
                        # Layout
                        "layout", "design", "visual design",
                        "page layout", "document design",
                        
                        # Typography
                        "font", "fonts", "typeface", "typography",
                        "text formatting", "bold", "italic",
                        
                        # Sections styling
                        "headers", "headings", "subheadings",
                        "bullet points", "numbered lists",
                        
                        # Margins/spacing
                        "margins", "spacing", "line spacing",
                        "paragraph spacing", "indentation",
                        
                        # PDF specific
                        "pages", "page numbers", "page layout",
                        
                        # Export
                        "export", "convert", "save as",
                        "download format",
                    ],
                    "patterns": [
                        r"\bformat (of|for)\b.*\bdocument\b",
                        r"\bhow (is|are)\b.*\b(formatted|presented|styled)\b",
                        r"\blayout (of|for)\b",
                        r"\bstyle\b.*\b(used|applied|guide)\b",
                        r"\bdocument\b.*\b(format|style|design)\b",
                        r"\bfont(s)?\b.*\b(used|in)\b",
                        r"\bpage\b.*\b(layout|design|formatting)\b",
                    ]
                }
            ],
            
            # ============================================
            # CONTENT EXTRACTION QUERIES
            # ============================================
            QueryIntent.CONTENT_EXTRACTION: [
                {
                    "keywords": [
                        # Extract
                        "extract", "extraction", "pull out",
                        "get the", "retrieve the",
                        
                        # Specific content
                        "text from", "content from", "data from",
                        "information from", "details from",
                        
                        # Copy/paste
                        "copy", "paste", "reproduce",
                        "verbatim", "exact text",
                        
                        # Quote
                        "quote", "quotes", "quotation",
                        "direct quote", "excerpt",
                        
                        # Passages
                        "passage", "passages", "paragraph",
                        "section text", "full text",
                        
                        # List extraction
                        "list of", "all the", "every",
                        "complete list", "full list",
                        
                        # Names/entities
                        "names mentioned", "people mentioned",
                        "organizations mentioned", "dates mentioned",
                        
                        # Raw data
                        "raw data", "raw text", "unprocessed",
                    ],
                    "patterns": [
                        r"\bextract\b.*\b(text|data|information|content)\b",
                        r"\bget (the|all)?\b.*\b(text|content|data|names)\b",
                        r"\blist (of|all)?\b.*\b(from|in)\b",
                        r"\bquote(s)?\b.*\b(from|in)\b",
                        r"\bverbatim\b.*\b(text|quote|content)\b",
                        r"\ball\b.*\b(names|dates|people|organizations)\b.*\bmentioned\b",
                        r"\bcopy\b.*\b(text|content|section)\b",
                    ]
                }
            ],
            
            # ============================================
            # GENERAL CONTENT QUERIES
            # ============================================
            QueryIntent.GENERAL_CONTENT: [
                {
                    "keywords": [
                        # What
                        "what", "what's", "whats",
                        
                        # About
                        "about", "regarding", "concerning",
                        "related to", "pertaining to",
                        
                        # Content
                        "content", "contents", "information",
                        "discuss", "discusses", "discussed",
                        
                        # Topic
                        "topic", "topics", "subject", "subjects",
                        "theme", "themes", "focus",
                        
                        # Says/states
                        "says", "states", "mentions", "describes",
                        "explains", "talks about",
                        
                        # Covers
                        "covers", "covering", "coverage",
                        "addresses", "deals with",
                        
                        # Main content
                        "main content", "primary content",
                        "core content", "key content",
                        
                        # General questions
                        "tell me about", "information about",
                        "details about", "explain about",
                    ],
                    "patterns": [
                        r"\btell me about\b",
                        r"\binformation (about|on|regarding)\b",
                        r"\bcontent (of|in)\b.*\bdocument\b",
                        r"\btopic(s)?\b.*\b(covered|discussed)\b",
                        r"\bwhat does\b.*\b(discuss|cover|address|say)\b",
                        r"\bmain (topic|subject|theme|focus)\b",
                    ]
                }
            ],
        }
    
    # def classify(self, query: str) -> QueryIntent:
    #     """
    #     Classify a query into one of the defined intent categories.
        
    #     Args:
    #         query: The user query string
            
    #     Returns:
    #         QueryIntent: The classified intent
    #     """
    #     query_lower = query.lower().strip()
        
    #     # Score each intent
    #     intent_scores = {}
        
    #     for intent, rules_list in self.patterns.items():
    #         score = 0
    #         negative_match = False
            
    #         for rules in rules_list:
    #             # Check negative patterns first (exclude this intent if matched)
    #             for neg_pattern in rules.get("negative_patterns", []):
    #                 if re.search(neg_pattern, query_lower, re.IGNORECASE):
    #                     negative_match = True
    #                     break  # Skip this intent if negative pattern matches
                
    #             if negative_match:
    #                 break  # Don't score this intent
                
    #             # Check keywords
    #             for keyword in rules.get("keywords", []):
    #                 if keyword.lower() in query_lower:
    #                     score += 1
                
    #             # Check regex patterns
    #             for pattern in rules.get("patterns", []):
    #                 if re.search(pattern, query_lower, re.IGNORECASE):
    #                     score += 2  # Patterns weighted higher
            
    #         # Only add to scores if no negative match and score > 0
    #         if not negative_match and score > 0:
    #             intent_scores[intent] = score
        
    #     # Return intent with highest score
    #     if intent_scores:
    #         return max(intent_scores.items(), key=lambda x: x[1])[0]
        
    #     # Default to general content
    #     return QueryIntent.GENERAL_CONTENT

    def classify(self, query: str) -> QueryIntent:
        """
        Classify a query into one of the defined intent categories
        with detailed logging for debugging.
        """

        query_lower = query.lower().strip()
        print("\n" + "=" * 60)
        print(f"QUERY: '{query_lower}'")

        intent_scores = {}

        for intent, rules_list in self.patterns.items():
            print("\n" + "-" * 40)
            #print(f"Checking intent: {intent}")

            score = 0
            negative_match = False

            # Safety check: ensure rules_list is iterable list of dicts
            if not isinstance(rules_list, list):
                print(f"❌ Invalid rules format for intent {intent}: {type(rules_list)}")
                continue

            for rules in rules_list:
                if not isinstance(rules, dict):
                    print(f"❌ Skipping invalid rules entry: {rules}")
                    continue

                # 1️⃣ Check negative patterns
                for neg_pattern in rules.get("negative_patterns", []):
                    if re.search(neg_pattern, query_lower, re.IGNORECASE):
                        print(f"  ❌ Negative pattern matched: '{neg_pattern}'")
                        negative_match = True
                        break

                if negative_match:
                    print("  ⛔ Intent disqualified due to negative pattern")
                    break

                # 2️⃣ Keyword matches (+1)
                for keyword in rules.get("keywords", []):
                    if keyword.lower() in query_lower:
                        print(f"  ✅ Keyword matched (+1): '{keyword}'")
                        score += 1

                # 3️⃣ Regex pattern matches (+2)
                for pattern in rules.get("patterns", []):
                    if re.search(pattern, query_lower, re.IGNORECASE):
                        print(f"  ✅ Regex matched (+2): '{pattern}'")
                        score += 2

            print(f" Final score for {intent}: {score}")

            if negative_match:
                print(f" ❌ Intent {intent} excluded (negative match)")
                continue

            if score > 0:
                intent_scores[intent] = score
                print(f" ✅ Intent {intent} accepted with score {score}")
            else:
                print(f" ❌ Intent {intent} rejected (score = 0)")

        print("\n" + "=" * 60)
        print("INTENT SCORES:", intent_scores)

        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
            print(f"🎯 SELECTED INTENT: {best_intent}")
            return best_intent

        print("⚠️ No intent matched — returning GENERAL_CONTENT")
        return QueryIntent.GENERAL_CONTENT
        
    def classify_with_confidence(self, query: str) -> Dict[str, any]:
        """
        Classify query and return confidence score.
        
        Args:
            query: The user query string
        
        Returns:
            Dict with intent, confidence, and top alternatives
        """
        query_lower = query.lower().strip()
        intent_scores = {}
        
        for intent, rules_list in self.patterns.items():
            score = 0
            negative_match = False
            
            for rules in rules_list:
                # Check negative patterns first (exclude this intent if matched)
                for neg_pattern in rules.get("negative_patterns", []):
                    if re.search(neg_pattern, query_lower, re.IGNORECASE):
                        negative_match = True
                        break  # Skip this intent if negative pattern matches
                
                if negative_match:
                    break  # Don't score this intent
                
                for keyword in rules.get("keywords", []):
                    if keyword.lower() in query_lower:
                        score += 1
                
                for pattern in rules.get("patterns", []):
                    if re.search(pattern, query_lower, re.IGNORECASE):
                        score += 2
            
            # Only add to scores if no negative match and score > 0
            if not negative_match and score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return {
                "intent": QueryIntent.GENERAL_CONTENT,
                "confidence": 0.0,
                "alternatives": []
            }
        
        # Sort by score
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        
        top_intent, top_score = sorted_intents[0]
        total_score = sum(intent_scores.values())
        confidence = top_score / total_score if total_score > 0 else 0.0
        
        alternatives = [
            {"intent": intent, "score": score}
            for intent, score in sorted_intents[1:4]  # Top 3 alternatives
        ]
        
        return {
            "intent": top_intent,
            "confidence": confidence,
            "alternatives": alternatives
        }

    def get_explanation(self, intent: Optional[str] = None, query: Optional[str] = None) -> str:
        """
        Get explanation for classification.
        Required by your routing system.
        
        Args:
            intent: The classified intent (optional, will use last if not provided)
            query: The query that was classified (optional)
        
        Returns:
            str: Human-readable explanation
        """
        # If intent provided, use it; otherwise use last classification
        if intent:
            details = {
                "intent": intent,
                "query": query or self._last_classification_details.get("query", ""),
                "score": self._last_classification_details.get("score", 0),
                "confidence": self._last_classification_details.get("confidence", 0.0),
                "alternatives": self._last_classification_details.get("alternatives", [])
            }
        elif self._last_classification_details:
            details = self._last_classification_details
        else:
            return "No classification has been performed yet."
        
        intent_val = details.get("intent", "unknown")
        score = details.get("score", 0)
        confidence = details.get("confidence", 0.0)
        
        explanation = f"Query classified as '{intent_val}' with score {score}"
        
        if confidence > 0:
            explanation += f" (confidence: {confidence:.1%})"
        
        alternatives = details.get("alternatives", [])
        if alternatives:
            alt_text = ", ".join([f"{a['intent']} ({a['score']})" for a in alternatives[:2]])
            explanation += f". Alternative intents: {alt_text}"
        
        return explanation

    def get_routing_decision(self, query: str) -> Dict[str, Any]:
        """
        Get complete routing decision for query.
        Used by routing engine.
        
        Args:
            query: User query
            
        Returns:
            Dict with routing information
        """
        result = self.classify_with_confidence(query)
        
        # Map intents to engines
        intent_to_engine = {
            "metadata": "MetadataEngine",
            "aggregate": "AggregateEngine",
            "analytical": "AnalyticalEngine",
            "structural": "StructuralEngine",
            "summarization": "SummarizationEngine",
            "comparison": "ComparisonEngine",
            "search_lookup": "SearchEngine",
            "definitional": "RetrievalEngine",
            "procedural": "RetrievalEngine",
            "general_content": "RetrievalEngine"
        }
        
        intent = result["intent"]
        engine = intent_to_engine.get(intent, "RetrievalEngine")
        
        return {
            "intent": intent,
            "engine": engine,
            "confidence": result["confidence"],
            "should_route": result["confidence"] > 0.3,
            "explanation": self.get_explanation(),
            "alternatives": result.get("alternatives", [])
        }
    
    def should_use_metadata_engine(self, query: str) -> bool:
        """Check if query should use metadata engine"""
        intent = self.classify(query)
        return intent == "metadata"
    
    def should_use_aggregate_engine(self, query: str) -> bool:
        """Check if query should use aggregate engine"""
        intent = self.classify(query)
        return intent == "aggregate"

    def get_intent_details(self, query: str = None) -> Dict[str, Any]:
        """
        Get detailed information about classification.
        Alternative to get_explanation for structured data.
        
        Args:
            query: Optional query to classify
            
        Returns:
            Dict with classification details
        """
        if query:
            self.classify_with_confidence(query)
        
        return self._last_classification_details.copy() if self._last_classification_details else {}
    

    def __call__(self, query: str) -> str:
        """
        Allow classifier to be called directly.
        Makes it compatible with: classifier(query)
        
        Args:
            query: User query
            
        Returns:
            str: Intent
        """
        return self.classify(query)


# Example usage
if __name__ == "__main__":
    classifier = IntentClassifier()
    
    '''
    # Test queries
    test_queries = [
        "How many pages are in this document?",
        "Summarize the main points",
        "What is the definition of quantum entanglement?",
        "Compare the results from section 2 and section 3",
        "Find all mentions of climate change",
        "What are the limitations of this study?",
        "How to implement the proposed solution?",
        "What is the author's stance on this issue?",
        "Does this comply with GDPR regulations?",
        "What is the tone of this article?",
    ]
    
    print("Query Intent Classification Examples:\n")
    for query in test_queries:
        result = classifier.classify_with_confidence(query)
        print(f"Query: {query}")
        print(f"Intent: {result['intent'].value}")
        print(f"Confidence: {result['confidence']:.2%}")
        if result['alternatives']:
            print(f"Alternatives: {[alt['intent'].value for alt in result['alternatives']]}")
        print()

        '''