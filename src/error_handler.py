"""
Error Handler Module - Professional error handling and logging
Provides comprehensive error handling, logging, and user-friendly error messages
"""

import logging
import traceback
from typing import Optional, Dict, Any, Callable
from enum import Enum
from datetime import datetime
import os

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Minor issues, can continue
    MEDIUM = "medium"     # Significant issues, degraded service
    HIGH = "high"         # Critical issues, major features broken
    CRITICAL = "critical" # System failure, cannot continue

class ErrorCategory(Enum):
    """Error categories for better organization"""
    API = "api"                    # API-related errors (Gemini, MCP)
    VALIDATION = "validation"      # Input validation errors
    FILESYSTEM = "filesystem"      # File I/O errors
    NETWORK = "network"           # Network/connectivity errors
    PARSING = "parsing"           # JSON/data parsing errors
    CONFIGURATION = "configuration"  # Configuration/setup errors
    UNKNOWN = "unknown"           # Unknown errors

class MVPAgentError(Exception):
    """Base exception for MVP Agent"""
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.user_message = user_message or self._generate_user_message()
        self.timestamp = datetime.now()
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly error message"""
        category_messages = {
            ErrorCategory.API: "We're having trouble connecting to our AI services. Please try again in a moment.",
            ErrorCategory.VALIDATION: "There's an issue with your input. Please check and try again.",
            ErrorCategory.FILESYSTEM: "We couldn't save your files. Please check disk space and permissions.",
            ErrorCategory.NETWORK: "Network connection issue. Please check your internet connection.",
            ErrorCategory.PARSING: "We received an unexpected response. Trying alternative approach...",
            ErrorCategory.CONFIGURATION: "Configuration issue detected. Please check your API keys and settings.",
            ErrorCategory.UNKNOWN: "An unexpected error occurred. We're working to resolve it."
        }
        return category_messages.get(self.category, self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging"""
        return {
            "message": self.message,
            "user_message": self.user_message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

class ErrorLogger:
    """Centralized error logging"""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize error logger"""
        self.log_dir = log_dir
        self._ensure_log_dir()
        self._setup_logging()
    
    def _ensure_log_dir(self):
        """Ensure log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _setup_logging(self):
        """Set up logging configuration"""
        log_file = os.path.join(
            self.log_dir,
            f"mvp_agent_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()  # Also print to console
            ]
        )
        
        self.logger = logging.getLogger('MVPAgent')
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Log an error with context
        
        Args:
            error: The exception that occurred
            context: Additional context information
        """
        if isinstance(error, MVPAgentError):
            error_dict = error.to_dict()
            error_dict['context'] = context or {}
            self.logger.error(f"MVP Agent Error: {error_dict}")
        else:
            self.logger.error(
                f"Unexpected error: {str(error)}\n"
                f"Context: {context}\n"
                f"Traceback: {traceback.format_exc()}"
            )
    
    def log_warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a warning"""
        self.logger.warning(f"{message} | Context: {context}")
    
    def log_info(self, message: str):
        """Log informational message"""
        self.logger.info(message)

class ErrorHandler:
    """Professional error handling with fallbacks and recovery"""
    
    def __init__(self, logger: Optional[ErrorLogger] = None):
        """Initialize error handler"""
        self.logger = logger or ErrorLogger()
        self.error_history = []
    
    def handle_api_error(
        self,
        error: Exception,
        operation: str,
        fallback: Optional[Callable] = None
    ) -> Any:
        """
        Handle API errors with fallback strategy
        
        Args:
            error: The API error
            operation: Description of the operation that failed
            fallback: Optional fallback function to try
            
        Returns:
            Result from fallback if successful, or raises
        """
        agent_error = MVPAgentError(
            message=f"API error during {operation}: {str(error)}",
            category=ErrorCategory.API,
            severity=ErrorSeverity.HIGH,
            details={"operation": operation, "original_error": str(error)}
        )
        
        self.logger.log_error(agent_error, {"operation": operation})
        self.error_history.append(agent_error)
        
        if fallback:
            try:
                self.logger.log_info(f"Attempting fallback for {operation}")
                return fallback()
            except Exception as fallback_error:
                self.logger.log_error(
                    fallback_error,
                    {"operation": f"{operation}_fallback"}
                )
                raise agent_error
        
        raise agent_error
    
    def handle_validation_error(self, error: Exception, field: str) -> MVPAgentError:
        """
        Handle validation errors
        
        Args:
            error: The validation error
            field: The field that failed validation
            
        Returns:
            MVPAgentError instance
        """
        agent_error = MVPAgentError(
            message=f"Validation error for {field}: {str(error)}",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details={"field": field, "original_error": str(error)},
            user_message=f"Please check your {field} and try again."
        )
        
        self.logger.log_error(agent_error, {"field": field})
        self.error_history.append(agent_error)
        
        return agent_error
    
    def handle_filesystem_error(
        self,
        error: Exception,
        operation: str,
        path: str
    ) -> MVPAgentError:
        """
        Handle filesystem errors
        
        Args:
            error: The filesystem error
            operation: Description of file operation
            path: File path involved
            
        Returns:
            MVPAgentError instance
        """
        agent_error = MVPAgentError(
            message=f"Filesystem error during {operation}: {str(error)}",
            category=ErrorCategory.FILESYSTEM,
            severity=ErrorSeverity.MEDIUM,
            details={"operation": operation, "path": path, "original_error": str(error)},
            user_message="We couldn't save your files. Please check disk space and try again."
        )
        
        self.logger.log_error(agent_error, {"operation": operation, "path": path})
        self.error_history.append(agent_error)
        
        return agent_error
    
    def handle_parsing_error(
        self,
        error: Exception,
        data_type: str,
        fallback: Optional[Callable] = None
    ) -> Any:
        """
        Handle parsing errors (e.g., JSON parsing)
        
        Args:
            error: The parsing error
            data_type: Type of data being parsed
            fallback: Optional fallback parser
            
        Returns:
            Result from fallback or raises
        """
        agent_error = MVPAgentError(
            message=f"Parsing error for {data_type}: {str(error)}",
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.MEDIUM,
            details={"data_type": data_type, "original_error": str(error)}
        )
        
        self.logger.log_error(agent_error, {"data_type": data_type})
        self.error_history.append(agent_error)
        
        if fallback:
            try:
                self.logger.log_info(f"Attempting fallback parser for {data_type}")
                return fallback()
            except Exception as fallback_error:
                self.logger.log_error(
                    fallback_error,
                    {"data_type": f"{data_type}_fallback"}
                )
                raise agent_error
        
        raise agent_error
    
    def safe_execute(
        self,
        func: Callable,
        operation: str,
        fallback: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Safely execute a function with error handling
        
        Args:
            func: Function to execute
            operation: Description of the operation
            fallback: Optional fallback function
            *args, **kwargs: Arguments for func
            
        Returns:
            Result from func or fallback
        """
        try:
            return func(*args, **kwargs)
        except MVPAgentError:
            raise  # Re-raise our own errors
        except Exception as e:
            self.logger.log_error(e, {"operation": operation})
            
            if fallback:
                try:
                    self.logger.log_warning(
                        f"Using fallback for {operation}",
                        {"original_error": str(e)}
                    )
                    return fallback(*args, **kwargs)
                except Exception as fallback_error:
                    self.logger.log_error(
                        fallback_error,
                        {"operation": f"{operation}_fallback"}
                    )
                    raise MVPAgentError(
                        message=f"Both primary and fallback failed for {operation}",
                        category=ErrorCategory.UNKNOWN,
                        severity=ErrorSeverity.HIGH,
                        details={
                            "primary_error": str(e),
                            "fallback_error": str(fallback_error)
                        }
                    )
            
            raise MVPAgentError(
                message=f"Error during {operation}: {str(e)}",
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.MEDIUM,
                details={"original_error": str(e)}
            )
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered"""
        return {
            "total_errors": len(self.error_history),
            "by_category": self._count_by_category(),
            "by_severity": self._count_by_severity(),
            "recent_errors": [e.to_dict() for e in self.error_history[-5:]]
        }
    
    def _count_by_category(self) -> Dict[str, int]:
        """Count errors by category"""
        counts = {}
        for error in self.error_history:
            category = error.category.value
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def _count_by_severity(self) -> Dict[str, int]:
        """Count errors by severity"""
        counts = {}
        for error in self.error_history:
            severity = error.severity.value
            counts[severity] = counts.get(severity, 0) + 1
        return counts

# Singleton instances
_error_logger = None
_error_handler = None

def get_error_logger() -> ErrorLogger:
    """Get or create error logger singleton"""
    global _error_logger
    if _error_logger is None:
        _error_logger = ErrorLogger()
    return _error_logger

def get_error_handler() -> ErrorHandler:
    """Get or create error handler singleton"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler(get_error_logger())
    return _error_handler
