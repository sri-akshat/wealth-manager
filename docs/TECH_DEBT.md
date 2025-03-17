# Technical Debt Backlog

## High Priority

### Security & Authentication
- [ ] Update JWT secret keys to be environment variables across all services
- [ ] Implement token refresh mechanism
- [ ] Add rate limiting for authentication endpoints

### Code Quality
- [ ] Update deprecated SQLAlchemy usage (replace declarative_base)
- [ ] Migrate from datetime.utcnow() to datetime.now(datetime.UTC)
- [ ] Update Pydantic v1 style validators to v2 syntax
- [ ] Add input validation for all API endpoints
- [ ] investor service should refer to investor Id instead of user Id

## Medium Priority

### Testing
- [ ] Add integration tests for inter-service communication
- [ ] Implement end-to-end testing suite
- [ ] Add performance tests for critical endpoints
- [ ] Add load testing scenarios

### Documentation
- [ ] Add API documentation using OpenAPI specifications
- [ ] Document service interaction patterns
- [ ] Add setup guide for local development

### Monitoring & Logging
- [ ] Implement structured logging across all services
- [ ] Add metrics collection for performance monitoring
- [ ] Set up centralized logging system

## Low Priority

### Development Experience
- [ ] Set up pre-commit hooks for code formatting
- [ ] Add development containers configuration
- [ ] Improve error messages and debugging information
- [ ] pydantic-settings needs to be included in requirements
- [ ] ⁠OpenAPI documentation does not create request body. - need to be fixed.
- [ ] ⁠create a test script to pre-load test data when the database is getting created ??

### Infrastructure
- [ ] Containerize all services
- [ ] Set up CI/CD pipelines
- [ ] Add infrastructure as code templates

## Completed Items
- [x] Fix floating-point precision issues in investment calculations
- [x] Add proper test coverage for user service
- [x] Add proper test coverage for investment service

## Notes
- Priority levels may change based on business requirements
- New items should be added with a date and owner
- Completed items should be moved to the "Completed Items" section with completion date 
