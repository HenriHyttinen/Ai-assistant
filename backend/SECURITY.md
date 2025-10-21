# Security Implementation

This document outlines the security measures implemented in the Numbers Don't Lie application.

## Data Encryption

### In Transit
- **HTTPS/TLS**: All API communications use HTTPS in production
- **JWT Tokens**: Access and refresh tokens are signed with secure algorithms
- **OAuth2**: Secure OAuth2 flows for Google and GitHub authentication

### At Rest
- **Password Hashing**: Passwords are hashed using bcrypt with salt
- **Sensitive Data Encryption**: Sensitive fields are encrypted using Fernet (AES 128)
- **Database Security**: Database connections use encrypted connections

## Encrypted Fields

The following fields are encrypted at rest:

### User Data
- `two_factor_secret`: 2FA TOTP secret
- `backup_codes`: 2FA backup codes

### Health Profile Data
- `dietary_preferences`: JSON string of dietary preferences
- `dietary_restrictions`: JSON string of dietary restrictions
- `strength_indicators`: JSON string of strength metrics
- `exercise_types`: JSON string of exercise types

## Security Headers

The application includes the following security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (HTTPS only)

## Rate Limiting

- **General API**: 100 requests per minute per IP
- **AI Endpoints**: 10 requests per minute per user
- **Auth Endpoints**: 5 requests per minute per IP

## Authentication & Authorization

- **JWT Tokens**: Secure token-based authentication
- **Refresh Tokens**: Automatic token refresh with secure rotation
- **2FA Support**: TOTP-based two-factor authentication
- **OAuth2**: Google and GitHub OAuth integration

## Data Privacy

- **Consent Management**: Users can control data collection and processing
- **Data Export**: Users can export their data in multiple formats
- **Data Deletion**: Users can request data deletion
- **Anonymization**: AI insights exclude personally identifiable information

## Environment Variables

Set the following environment variables for production:

```bash
# Encryption
ENCRYPTION_KEY=your-32-character-encryption-key-here

# Security
FORCE_HTTPS=true
SECRET_KEY=your-super-secret-jwt-key-here

# Database
DATABASE_URL=postgresql://user:password@host:port/database
```

## Migration

To encrypt existing data, run:

```bash
python migrate_encrypt_data.py
```

## Security Checklist

- [x] Passwords hashed with bcrypt
- [x] Sensitive data encrypted at rest
- [x] HTTPS enforced in production
- [x] Security headers implemented
- [x] Rate limiting configured
- [x] JWT tokens with expiration
- [x] Refresh token rotation
- [x] 2FA support
- [x] OAuth2 integration
- [x] CORS properly configured
- [x] Input validation and sanitization
- [x] Error handling without information leakage
