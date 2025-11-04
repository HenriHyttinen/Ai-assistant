# Error Handling Approach

## Overview

The system implements comprehensive error handling at multiple levels to ensure reliability, graceful degradation, and user-friendly error messages. This document outlines the error handling strategies, fallback mechanisms, circuit breaker patterns, and retry logic.

## Error Handling Layers

### 1. Application-Level Middleware

**Location**: `backend/main.py` (Lines 117-126)

**Implementation**:
```python
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next: Callable):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
```

**Purpose**: Catches unhandled exceptions at the application level
**Benefits**: Prevents application crashes, provides consistent error responses

### 2. Route-Level Error Handling

**Location**: All route handlers in `backend/routes/nutrition.py`

**Pattern**:
```python
@router.post("/endpoint")
def endpoint_handler(...):
    try:
        # Business logic
        ...
        return result
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        db.rollback()
        logger.error(f"Error in endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error message: {str(e)}"
        )
```

**Key Points**:
- **HTTPException**: Re-raised to preserve status codes
- **Database Rollback**: Ensures data consistency
- **Detailed Logging**: Includes stack traces for debugging
- **User-Friendly Messages**: Clear error messages without sensitive data

### 3. Service-Level Error Handling

**Location**: All service classes (`backend/services/`)

**Pattern**:
```python
def service_method(self, db: Session, ...):
    try:
        # Service logic
        ...
        return result
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error in service method: {e}", exc_info=True)
        db.rollback()
        raise
```

**Benefits**:
- Specific error types handled appropriately
- Database transactions rolled back on errors
- Errors propagate with context

## HTTPException Status Codes

### Standard Status Codes

**400 Bad Request**: Invalid input data
```python
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid meal ID format"
)
```

**404 Not Found**: Resource not found
```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Meal plan not found"
)
```

**500 Internal Server Error**: Unexpected server errors
```python
raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=f"Error generating meal plan: {str(e)}"
)
```

**Usage Locations**:
- All route handlers validate inputs and resources
- Consistent error responses across endpoints
- Frontend can handle errors appropriately

## Fallback Mechanisms

### 1. AI Recovery Service

**Location**: `backend/services/ai_recovery_service.py`

**Purpose**: Handles AI failures with multiple fallback strategies

**Strategies**:
1. **Cached Response**: Return cached result if available
2. **Simplified AI**: Use simpler AI prompts with fewer constraints
3. **Rule-Based**: Use database recipes matching criteria
4. **Mock Response**: Return template response as last resort

**Implementation**:
```python
async def execute_with_fallbacks(
    self,
    primary_func: Callable,
    service_name: str,
    request_data: Dict[str, Any],
    cache_ttl: int = 300,
    *args,
    **kwargs
) -> Any:
    # Check cache first
    cached_response = self.get_cached_response(cache_key)
    if cached_response:
        return cached_response
    
    # Try primary function with retry
    try:
        result = await self.execute_with_retry(primary_func, service_name, *args, **kwargs)
        self.cache_response(cache_key, result, cache_ttl)
        return result
    except Exception as e:
        # Try fallback strategies
        for strategy in self.fallback_strategies:
            try:
                fallback_result = await self._execute_fallback_strategy(...)
                if fallback_result:
                    return fallback_result
            except Exception:
                continue
        
        raise e
```

**Usage**: Applied to all AI-dependent operations

### 2. Database Fallbacks

**Location**: `backend/ai/functions.py:_get_nutrition_from_database()`

**Purpose**: Falls back to estimates if database lookup fails

**Process**:
1. Try database lookup (fuzzy matching)
2. If not found, try category-based matching
3. If still not found, use estimate functions
4. Log fallback usage for monitoring

**Example**:
```python
def _get_nutrition_from_database(self, ingredient_name: str, quantity: float, unit: str):
    # Try database lookup
    ingredient = self._find_ingredient_in_database(ingredient_name)
    if ingredient:
        return self._calculate_from_database(ingredient, quantity, unit)
    
    # Fallback to estimates
    logger.warning(f"Database lookup failed for {ingredient_name}, using estimate")
    return self._estimate_nutrition_for_ingredient(ingredient_name, quantity, unit)
```

### 3. Recipe Generation Fallbacks

**Location**: `backend/ai/nutrition_ai.py:_fallback_meal_plan()`

**Purpose**: Provides basic meal plans when AI is unavailable

**Strategy**:
- Use database recipes matching user preferences
- Simple meal structure (breakfast, lunch, dinner, snack)
- No AI-generated recipes
- Still respects dietary restrictions

## Circuit Breaker Pattern

### Frontend Circuit Breaker

**Location**: `frontend/src/services/api.ts` (Lines 149-165)

**Implementation**:
```typescript
if (serverDownTime > 0 && (Date.now() - serverDownTime) > SERVER_DOWN_THRESHOLD) {
    console.warn('Circuit breaker open - server down too long, using cache only');
    const cached = getCachedResponse(url, error.config?.params);
    if (cached) return Promise.resolve(cached);
    return Promise.reject(new Error('Server unavailable - circuit breaker open'));
}
```

**Behavior**:
- Monitors server availability
- Opens circuit after threshold (default: 30 seconds)
- Returns cached data when circuit is open
- Prevents repeated failed requests

### Backend Retry Logic

**Location**: `backend/services/ai_recovery_service.py:execute_with_retry()`

**Implementation**:
```python
async def execute_with_retry(
    self,
    func: Callable,
    service_name: str,
    max_retries: int = 3,
    *args,
    **kwargs
) -> Any:
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = (2 ** attempt) * 1000  # Exponential backoff
            logger.warning(f"Retry {attempt + 1}/{max_retries} for {service_name}: {e}")
            await asyncio.sleep(wait_time / 1000)
    
    raise Exception(f"Failed after {max_retries} retries")
```

**Features**:
- **Exponential Backoff**: Wait time increases with each retry (1s, 2s, 4s)
- **Configurable Retries**: Default 3 attempts, configurable per service
- **Logging**: Each retry attempt is logged
- **Service-Specific**: Different retry strategies for different services

## Retry Logic Details

### AI API Retries

**Location**: `backend/ai/nutrition_ai.py:_call_openai()`

**Strategy**:
- **Maximum Retries**: 3 attempts
- **Backoff Strategy**: Exponential backoff (1s, 2s, 4s)
- **Retry Conditions**: 
  - Network errors
  - Rate limit errors (429)
  - Timeout errors
- **Non-Retryable**: 
  - Invalid API key (401)
  - Invalid request format (400)
  - Content policy violations (403)

### Database Operation Retries

**Location**: Database operations in services

**Strategy**:
- **Transaction Retries**: Automatic on deadlock
- **Connection Retries**: SQLAlchemy connection pool handles
- **Query Timeouts**: 30-second timeout for long queries

## Error Logging

### Logging Levels

**ERROR**: Unexpected errors requiring attention
```python
logger.error(f"Error generating meal plan: {e}", exc_info=True)
```

**WARNING**: Recoverable errors or fallbacks used
```python
logger.warning(f"Database lookup failed for {ingredient}, using estimate")
```

**INFO**: Normal operations and important events
```python
logger.info(f"Generated meal plan {meal_plan_id} with {meal_count} meals")
```

**DEBUG**: Detailed diagnostic information
```python
logger.debug(f"RAG retrieved {len(recipes)} similar recipes")
```

### Logging Configuration

**Location**: `backend/logging_config.py`

**Features**:
- **File Logging**: Errors logged to files
- **Console Logging**: Development console output
- **Log Rotation**: Prevents log files from growing too large
- **Structured Logging**: JSON format for production

## User-Friendly Error Messages

### Frontend Error Handling

**Location**: `frontend/src/utils/errorUtils.ts`

**Approach**:
- Catch API errors
- Display user-friendly messages
- Hide technical details
- Provide actionable guidance

**Example**:
```typescript
try {
    await generateMealPlan();
} catch (error) {
    if (error.response?.status === 400) {
        toast.error("Please check your meal plan settings");
    } else if (error.response?.status === 500) {
        toast.error("Server error. Please try again later");
    } else {
        toast.error("Failed to generate meal plan");
    }
}
```

### Backend Error Messages

**Principles**:
1. **Clear and Actionable**: Tell user what went wrong and how to fix it
2. **No Sensitive Data**: Don't expose internal system details
3. **Consistent Format**: Same error structure across all endpoints
4. **Appropriate Detail Level**: Enough information to understand, not overwhelm

## Error Recovery Strategies

### 1. Automatic Recovery

**Nutrition Calculation**:
- Database lookup fails → Use estimate
- Estimate unavailable → Use defaults
- Always returns valid nutrition values

**Recipe Generation**:
- AI fails → Use database recipes
- Database empty → Use fallback templates
- Always returns valid meal plans

### 2. Manual Recovery

**User Actions**:
- Regenerate meal if error occurs
- Retry failed operations
- Clear cache and retry

**Admin Actions**:
- Review error logs
- Fix data issues
- Restart services if needed

## Monitoring and Alerting

### Error Metrics

**Tracked Metrics**:
- Error rate by endpoint
- Error rate by error type
- Fallback usage frequency
- Retry attempt counts
- Circuit breaker state

### Alerting Thresholds

**Critical Alerts**:
- Error rate > 10% for any endpoint
- AI failures > 50% for any service
- Database connection failures
- Circuit breaker open > 5 minutes

**Warning Alerts**:
- Error rate > 5% for any endpoint
- Fallback usage > 20%
- Retry attempts > 50% of requests

## Best Practices

### 1. Fail Fast, Recover Gracefully
- Validate inputs early
- Return errors quickly
- Use fallbacks for recovery

### 2. Log Everything
- Include context in error logs
- Use appropriate log levels
- Include stack traces for errors

### 3. User Experience
- Never show technical errors to users
- Provide actionable error messages
- Allow users to retry operations

### 4. Data Consistency
- Always rollback database transactions on errors
- Validate data before committing
- Use database constraints

### 5. Performance
- Don't retry indefinitely
- Use exponential backoff
- Cache responses when possible

## Future Improvements

### 1. Distributed Tracing
- Track requests across services
- Identify failure points
- Measure latency

### 2. Error Aggregation
- Group similar errors
- Identify patterns
- Prioritize fixes

### 3. Predictive Failure Detection
- Monitor error trends
- Predict failures before they occur
- Proactive recovery

### 4. Automated Recovery
- Self-healing systems
- Automatic service restarts
- Dynamic fallback selection

## Conclusion

The error handling approach ensures:
- ✅ Reliability through multiple fallback layers
- ✅ User-friendly error messages
- ✅ Comprehensive logging for debugging
- ✅ Graceful degradation when services fail
- ✅ Data consistency through transaction management
- ✅ Performance through caching and retry strategies

