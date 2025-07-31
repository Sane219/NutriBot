# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Measures Implemented

### 1. Input Validation
- File upload validation (size, type, content)
- Text input sanitization
- Nutrition data range validation

### 2. Path Security
- Path traversal protection
- Model file integrity verification
- Restricted file access

### 3. Rate Limiting
- Request rate limiting per session
- DoS protection

### 4. XSRF Protection
- Cross-Site Request Forgery protection enabled
- Secure session handling

### 5. Dependency Security
- Pinned dependency versions
- Regular security audits

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Email security concerns to: [your-email@domain.com]
3. Include detailed steps to reproduce
4. Allow 48 hours for initial response

## Security Best Practices for Deployment

### Production Deployment
```bash
# Use secure requirements
pip install -r requirements_secure.txt

# Set secure environment variables
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=10

# Run with HTTPS
streamlit run app/main.py --server.port=8501 --server.enableCORS=false
```

### Docker Security
```dockerfile
# Use non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Limit resources
--memory=1g --cpus=1.0
```

### Network Security
- Use HTTPS in production
- Implement proper firewall rules
- Use reverse proxy (nginx/Apache)
- Enable security headers

## Security Checklist

- [x] XSRF protection enabled
- [x] File upload validation
- [x] Input sanitization
- [x] Path traversal protection
- [x] Rate limiting
- [x] Dependency pinning
- [ ] HTTPS enforcement
- [ ] Security headers
- [ ] Logging and monitoring
- [ ] Regular security audits

## Known Security Considerations

1. **Model Files**: Pickle files can execute arbitrary code. Only load trusted models.
2. **OCR Processing**: Large images can cause memory exhaustion.
3. **Regex Processing**: Complex patterns can cause ReDoS attacks.
4. **User Input**: All user input is sanitized but should be monitored.

## Security Updates

Check for security updates regularly:
```bash
pip-audit
safety check
```