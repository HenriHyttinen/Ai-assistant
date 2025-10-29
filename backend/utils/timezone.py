"""
Timezone utilities for ISO 8601 datetime handling
"""
import pytz
from datetime import datetime, timezone
from typing import Optional, Union
import zoneinfo

def get_user_timezone(user_timezone: str = "UTC") -> timezone:
    """
    Get timezone object from user timezone string
    
    Args:
        user_timezone: Timezone string (e.g., "UTC", "America/New_York", "Europe/London")
    
    Returns:
        timezone object
    """
    try:
        if user_timezone == "UTC":
            return timezone.utc
        
        # Try using zoneinfo first (Python 3.9+)
        try:
            return zoneinfo.ZoneInfo(user_timezone)
        except (zoneinfo.ZoneInfoNotFoundError, AttributeError):
            # Fallback to pytz for older Python versions
            return pytz.timezone(user_timezone)
    except Exception:
        # Default to UTC if timezone is invalid
        return timezone.utc

def to_iso8601_with_timezone(dt: datetime, user_timezone: str = "UTC") -> str:
    """
    Convert datetime to ISO 8601 format with timezone
    
    Args:
        dt: datetime object
        user_timezone: User's timezone string
    
    Returns:
        ISO 8601 formatted string with timezone
    """
    try:
        tz = get_user_timezone(user_timezone)
        
        # If datetime is naive, assume it's in user's timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        
        # Convert to user's timezone
        dt_in_user_tz = dt.astimezone(tz)
        
        # Return ISO 8601 format
        return dt_in_user_tz.isoformat()
    except Exception:
        # Fallback to UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

def from_iso8601_with_timezone(iso_string: str, user_timezone: str = "UTC") -> datetime:
    """
    Parse ISO 8601 string and convert to user's timezone
    
    Args:
        iso_string: ISO 8601 formatted string
        user_timezone: User's timezone string
    
    Returns:
        datetime object in user's timezone
    """
    try:
        # Parse ISO 8601 string
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        
        # Convert to user's timezone
        tz = get_user_timezone(user_timezone)
        return dt.astimezone(tz)
    except Exception:
        # Fallback to current time in UTC
        return datetime.now(timezone.utc)

def get_current_time_in_timezone(user_timezone: str = "UTC") -> datetime:
    """
    Get current time in user's timezone
    
    Args:
        user_timezone: User's timezone string
    
    Returns:
        Current datetime in user's timezone
    """
    try:
        tz = get_user_timezone(user_timezone)
        return datetime.now(tz)
    except Exception:
        return datetime.now(timezone.utc)

def format_datetime_for_user(dt: datetime, user_timezone: str = "UTC", format_type: str = "iso") -> str:
    """
    Format datetime for user display
    
    Args:
        dt: datetime object
        user_timezone: User's timezone string
        format_type: "iso" for ISO 8601, "display" for user-friendly format
    
    Returns:
        Formatted datetime string
    """
    try:
        tz = get_user_timezone(user_timezone)
        
        # Convert to user's timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt_in_user_tz = dt.astimezone(tz)
        
        if format_type == "iso":
            return dt_in_user_tz.isoformat()
        elif format_type == "display":
            return dt_in_user_tz.strftime("%Y-%m-%d %H:%M:%S %Z")
        else:
            return dt_in_user_tz.isoformat()
    except Exception:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

def get_user_timezone_info(user_timezone: str = "UTC") -> dict:
    """
    Get timezone information for a user
    
    Args:
        user_timezone: User's timezone string
    
    Returns:
        Dictionary with timezone info including current time in ISO format
    """
    try:
        current_time = get_current_time_in_timezone(user_timezone)
        return {
            "timezone": user_timezone,
            "current_time": current_time,
            "current_time_iso": to_iso8601_with_timezone(current_time, user_timezone),
            "timezone_offset": current_time.strftime("%z"),
            "is_dst": current_time.dst().total_seconds() != 0 if current_time.dst() else False
        }
    except Exception:
        # Fallback to UTC
        current_time = datetime.now(timezone.utc)
        return {
            "timezone": "UTC",
            "current_time": current_time,
            "current_time_iso": current_time.isoformat(),
            "timezone_offset": "+00:00",
            "is_dst": False
        }

def get_common_timezones() -> list:
    """
    Get list of common timezones for user selection
    
    Returns:
        List of timezone dictionaries with display names and values
    """
    return [
        {"value": "UTC", "label": "UTC (Coordinated Universal Time)"},
        {"value": "America/New_York", "label": "Eastern Time (US & Canada)"},
        {"value": "America/Chicago", "label": "Central Time (US & Canada)"},
        {"value": "America/Denver", "label": "Mountain Time (US & Canada)"},
        {"value": "America/Los_Angeles", "label": "Pacific Time (US & Canada)"},
        {"value": "Europe/London", "label": "London (GMT/BST)"},
        {"value": "Europe/Paris", "label": "Paris (CET/CEST)"},
        {"value": "Europe/Berlin", "label": "Berlin (CET/CEST)"},
        {"value": "Europe/Rome", "label": "Rome (CET/CEST)"},
        {"value": "Europe/Madrid", "label": "Madrid (CET/CEST)"},
        {"value": "Asia/Tokyo", "label": "Tokyo (JST)"},
        {"value": "Asia/Shanghai", "label": "Shanghai (CST)"},
        {"value": "Asia/Kolkata", "label": "Mumbai, Delhi (IST)"},
        {"value": "Australia/Sydney", "label": "Sydney (AEST/AEDT)"},
        {"value": "Australia/Melbourne", "label": "Melbourne (AEST/AEDT)"},
        {"value": "Pacific/Auckland", "label": "Auckland (NZST/NZDT)"},
    ]
